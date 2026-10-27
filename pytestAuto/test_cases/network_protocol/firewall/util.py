#############################################################################
#
# Copyright (c) 2006-2013 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################


import getpass
import re
import time

def _make_ln():
    import users
    user = getpass.getuser()
    if user in users.users:
        return ((users.users.index(user)*3) % 254)+1
    print
    if user == 'root':
        'You run the test as root, this is not recommended. Run it as an ordinary user. Proceeding...'
    else:
        print 'You (user %s) are not in config/users.py, it is recommended you add yourself last to the list. Proceeding...' % user
    print
    import random
    return random.randint(1,24)*10+random.randint(5,9)


ln = _make_ln() # lucky number
abnet = '10.' + str(ln) + '.'
abnet6 = '2005:' + str(ln) + ':'
mac_re = ('[0-9a-fA-F][0-9a-fA-F]:'*6)[:-1]
ip_re = (r'[0-9]{1,3}\.'*4)[:-2]
ip6_re = r'[0-9A-Fa-f:\.]+(?:%\S+)?'


def IF(boolean, true, false):
    'beware: no short circuiting'
    if boolean:
        return true
    return false


def prefixlen_to_netmask(p, v6 = ''):
    "v6: ipv4 is default. needed to correctly make a netmask for ipv6"
    if v6:
        bitmax = 128
    else:
        bitmax = 32
    if p < 0 or p > bitmax:
        raise 'prefixlen_to_netmask: %s' % p

    def prefixlen_to_bin(p):
        return '1'*p + '0'*(bitmax-p)

    b = prefixlen_to_bin(p)
    if v6:
        s = []
        for x in range(0,128,4):
            s.append(b[x:x+4])
    else:
        s = b[:8], b[8:16], b[16:24], b[24:]

    def bin_to_dec(b, nbits):
        r = 0
        for x in range(0,nbits):
            r += int(b[x]) << (nbits-1 - x)
        return str(r)

    if v6:
        f = [int(bin_to_dec(x,4)) for x in s]
        r = []
        for x in range(0,32,4):
            r.append('%X%X%X%X' % (f[x],f[x+1],f[x+2],f[x+3]))
    else:
        r = [bin_to_dec(x,8) for x in s]

    if v6:
        return ':'.join(r)

    else:
        return '.'.join(r)


def ip_and(ip, netmask_or_prefixlen):
    '''ANDs an ip with its netmask.
    a.b.c.d/24 -> a.b.c.0'''
    np = netmask_or_prefixlen
    if '.' in ip:
        if "." not in str(np):
            np = prefixlen_to_netmask(np)
        a = ip.split(".")
        b = np.split(".")
        def f((x,y)):
            return str(int(x) & int(y))
        return ".".join(map(f, zip(a,b)))
    #raise "no v6 yet"
    return ip


hosts_per_net_layout = {'rcs': 3, 'nat': 4, 'nat6': 4, 'roam': 4, 'ipsec': 4}


def layout_net(layout, hosts, v6 = ''):
    'configures "hosts" according to "layout"'
    """
    configures 'hosts' according to 'layout'
    hosts: a list of hosts (as passed to test() if >1)
    layout:
        'default' Does nothing. returns hostlist as is.
        'rcs' Requires 3 hosts which will become router/client/server in that order.
              c and s will be end up on different nets with the r inbetween having 2
              interfaces, one for each network.
              c and s will have routes added to find the other network via r.
              All info is returned in a 'struct' ('n' below), paired with the rest of the hosts
              not needed for this setup.
              Struct members: (all netifs below are vlans)
              n.r     router host
              n.s     server
              n.c     client
              n.cif   client netif
              n.sif   server netif
              n.cnet  1 as in ip addr 10.lucky_number.cnet.hostid
              n.snet  2
              n.rifc  router netif facing client
              n.rifs  router netif facing server
              n.ripc  router ip on netif facing client
              n.rips  router ip on netif facing server
        'nat'
              Performs the 'rcs' setup except it only adds the route on the
              clients to find the server.
    """
    def nat(hosts, v6, fourhosts = True):
        ab = IF(v6, abnet6 + ':' + abnet, abnet)
        pfx = IF(v6, 96, 24)
        # Create 2 networks connected via a router
        if fourhosts:
            r, s, c, w = hosts
        else:
            r, s, c = hosts
        cif = c.add_vlan()
        cnet = 1
        c.ts.primary_ip = cif.add_ip("%s%s.1/%s" % (ab, cnet, pfx))
        c.ts.primary_ip6 = c.ts.primary_ip

        sif = s.add_vlan()
        snet = 2
        s.ts.primary_ip = sif.add_ip("%s%s.3/24" % (abnet, snet))
        s.ts.primary_ip6 = s.ts.primary_ip

        rifc = r.add_vlan(vlan = cif.id)
        ripc = rifc.add_ip("%s%s.3/%s" % (ab, cnet, pfx))
        rifs = r.add_vlan(vlan = sif.id)
        rips  = rifs.add_ip("%s%s.1/24" % (abnet, snet))
        rip2s = rifs.add_ip("%s%s.2/24" % (abnet, snet))
        r.ts.primary_ip = rips
        r.ts.primary_ip6 = r.ts.primary_ip

        class _nat:
            pass
        n = _nat()
        n.r, n.s, n.c = r,s,c # router, server, client
        n.cif = cif           #client netif
        n.sif = sif
        n.cnet = cnet         #10.lucky_number.client_net(cnet).ip
        n.snet = snet
        n.rifc = rifc         #router netif facing client
        n.rifs = rifs
        n.ripc = ripc         #router ip on netif facing client
        n.rips = rips
        n.rip2s = rip2s

        #make client able to reach server net
        n.c.add_route(IF(v6, '2006:' + str(ln) + '::/96', n.s.ip()), n.ripc) #need ip_and 24 here for linux

        if fourhosts:
            n.w = w
            n.c2if = w.add_vlan(vlan = n.cif.id)
            w.ts.primary_ip = n.c2if.add_ip("%s%s.2/%s" % (ab, n.cnet, pfx))
            w.ts.primary_ip6 = w.ts.primary_ip
            n.w.add_route(IF(v6, '2006:' + str(ln) + '::/96', n.s.ip()), n.ripc) #need ip_and 24 here for linux
        return n

    def nat2(hosts, v6):
        return nat([hosts[2], hosts[1], hosts[0]], v6, fourhosts = False)

    #
    #  r looks like ipout-eth0 (bridged network i.e. eth0 is bound to usbeth1
    #    witch connects to bif1 of the DUT. eth1 is the control interface)
    #  c looks like ipout-eth0 (bridged network i.e. eth0 is bound to usbeth2.
    #    eth1 is the control interface)
    #
    #  This topology is created by the --usb-devs option for the runtestsuites.py
    #  script
    #
    #  r ---- bif1-bridge-bif2 ---- c
    def bcs(hosts, v6):
        ab = IF(v6, abnet6 + ':' + abnet, abnet)
        pfx = IF(v6, 120, 24)

        # Create 1 bridged network
        b, s, c = hosts
        bnet = 1

        cif = c.ts.netifs[1]
        c.ts.primary_ip = cif.add_ip("%s%s.2/%s" % (ab, bnet, pfx))
        c.ts.primary_ip6 = c.ts.primary_ip

        sif = s.ts.netifs[1]
        s.ts.primary_ip = sif.add_ip("%s%s.3/%s" % (ab, bnet, pfx))
        s.ts.primary_ip6 = s.ts.primary_ip

        rifc = b.ts.netifs[3] # bif2
        ripc = b.ts.netifs[4].add_ip("%s%s.1/%s" % (ab, bnet, pfx))
        rips = ripc
        bif = b.ts.netifs[4]
        rifs = b.ts.netifs[2] # bif1
        b.ts.primary_ip = rips
        b.ts.primary_ip6 = b.ts.primary_ip

        # Pass the network back to look like the rcs topology so existing firewall
        # tests can run unmodified against bridge interfaces with ipfirewall
        # support.
        class _nat:
            pass
        n = _nat()
        n.r, n.s, n.c = b,s,c # router, server, client
        n.cif = cif           #client netif
        n.sif = sif
        n.cnet = bnet         #10.lucky_number.client_net(cnet).ip
        n.snet = bnet
        n.rifc = rifc         #router netif facing client
        n.rifs = rifs
        n.ripc = ripc         #router ip on netif facing client
        n.rips = rips
        n.bif = bif

        return n


    def rcs(hosts, v6):
        ab = IF(v6, abnet6 + ':' + abnet, abnet)
        pfx = IF(v6, 120, 24)
        # Create 2 networks connected via a router
        r, s, c = hosts
        cif = c.add_vlan()
        cnet = 1
        c.ts.primary_ip = cif.add_ip("%s%s.1/%s" % (ab, cnet, pfx))
        c.ts.primary_ip6 = c.ts.primary_ip

        sif = s.add_vlan()
        snet = 2
        s.ts.primary_ip = sif.add_ip("%s%s.3/%s" % (ab, snet, pfx))
        s.ts.primary_ip6 = s.ts.primary_ip

        rifc = r.add_vlan(vlan = cif.id)
        ripc = rifc.add_ip("%s%s.3/%s" % (ab, cnet, pfx))
        rifs = r.add_vlan(vlan = sif.id)
        rips = rifs.add_ip("%s%s.1/%s" % (ab, snet, pfx))
        r.ts.primary_ip = rips
        r.ts.primary_ip6 = r.ts.primary_ip

        class _nat:
            pass
        n = _nat()
        n.r, n.s, n.c = r,s,c # router, server, client
        n.cif = cif           #client netif
        n.sif = sif
        n.cnet = cnet         #10.lucky_number.client_net(cnet).ip
        n.snet = snet
        n.rifc = rifc         #router netif facing client
        n.rifs = rifs
        n.ripc = ripc         #router ip on netif facing client
        n.rips = rips

        #make client able to reach server net
        n.c.add_route(n.s.ip(v6).mask(pfx), n.ripc) #need ip_and 24 here for linux
        n.s.add_route(n.c.ip(v6).mask(pfx), n.rips) #need ip_and 24 here for linux
        return n

    def rcs2(hosts, v6):
        ab = IF(v6, abnet6 + ':' + abnet, abnet)
        pfx = IF(v6, 120, 24)
        # Create 2 networks connected via a router
        r, s, c, w = hosts
        cif = c.add_vlan()
        cnet = 1
        c.ts.primary_ip = cif.add_ip("%s%s.1/%s" % (ab, cnet, pfx))
        c.ts.primary_ip6 = c.ts.primary_ip

        sif = s.add_vlan()
        snet = 2
        s.ts.primary_ip = sif.add_ip("%s%s.3/%s" % (ab, snet, pfx))
        s.ts.primary_ip6 = s.ts.primary_ip

        wif = w.add_vlan(vlan = sif.id)
        wnet = 2
        w.ts.primary_ip = wif.add_ip("%s%s.2/%s" % (ab, wnet, pfx))
        w.ts.primary_ip6 = w.ts.primary_ip

        rifc = r.add_vlan(vlan = cif.id)
        ripc = rifc.add_ip("%s%s.3/%s" % (ab, cnet, pfx))
        rifs = r.add_vlan(vlan = sif.id)
        rips = rifs.add_ip("%s%s.1/%s" % (ab, snet, pfx))

        class _nat:
            pass
        n = _nat()
        n.r, n.s, n.c, n.w = r,s,c,w # router, server, client, server2
        n.cif = cif           #client netif
        n.sif = sif
        n.wif = wif
        n.cnet = cnet         #10.lucky_number.client_net(cnet).ip
        n.snet = snet
        n.wnet = wnet
        n.rifc = rifc         #router netif facing client
        n.rifs = rifs
        n.ripc = ripc         #router ip on netif facing client
        n.rips = rips

        #make clients able to reach server net
        n.c.add_route(n.s.ip(v6).mask(pfx), n.ripc) #need ip_and 24 here for linux
        n.s.add_route(n.c.ip(v6).mask(pfx), n.rips) #need ip_and 24 here for linux
        n.w.add_route(n.c.ip(v6).mask(pfx), n.rips) #need ip_and 24 here for linux
        return n

    def ipsec(hosts, v6):
        ab = IF(v6, abnet6 + ':' + abnet, abnet)
        pfx = IF(v6, 120, 24)
        # Create 2 networks connected via a 2 routers
        r1, r2, s, c = hosts

        cif = c.add_vlan()
        cnet = 2
        c.ts.primary_ip = cif.add_ip("%s%s.1/%s" % (ab, cnet, pfx))
        c.ts.primary_ip6 = c.ts.primary_ip

        sif = s.add_vlan()
        snet = 3
        s.ts.primary_ip = sif.add_ip("%s%s.1/%s" % (ab, snet, pfx))
        s.ts.primary_ip6 = s.ts.primary_ip

        r1_ifc = r1.add_vlan(vlan = cif.id)
        r1_ipc = r1_ifc.add_ip("%s%s.2/%s" % (ab, cnet, pfx))
        rnet = 4;
        r1_ifs = r1.add_vlan()
        r1_ips = r1_ifs.add_ip("%s%s.1/%s" % (ab, rnet, pfx))
        r1.ts.primary_ip = r1_ipc
        r1.ts.primary_ip6 = r1.ts.primary_ip

        r2_ifs = r2.add_vlan(vlan = sif.id)
        r2_ips = r2_ifs.add_ip("%s%s.2/%s" % (ab, snet, pfx))
        r2_ifc = r2.add_vlan(vlan = r1_ifs.id)
        r2_ipc = r2_ifc.add_ip("%s%s.2/%s" % (ab, rnet, pfx))
        r2.ts.primary_ip = r2_ips
        r2.ts.primary_ip6 = r2.ts.primary_ip

        class _nat:
            pass
        n = _nat()
        n.r1, n.r2, n.s, n.c = r1,r2,s,c # router1, router2, server, client
        n.cif = cif           #client netif
        n.sif = sif
        n.cnet = cnet         #10.lucky_number.client_net(cnet).ip
        n.snet = snet
        n.rnet = rnet

        n.r1_ifc = r1_ifc         #router1 netif facing client
        n.r1_ifs = r1_ifs
        n.r1_ipc = r1_ipc         #router ip on netif facing client
        n.r1_ips = r1_ips

        n.r2_ifc = r2_ifc         #router2 netif facing client
        n.r2_ifs = r2_ifs
        n.r2_ipc = r2_ipc         #router ip on netif facing client
        n.r2_ips = r2_ips

        n.c.add_route(n.s.ip(v6).mask(pfx), n.r1_ipc) #need ip_and 24 here for linux
        n.s.add_route(n.c.ip(v6).mask(pfx), n.r2_ips) #need ip_and 24 here for linux
        n.r1.add_route(n.s.ip(v6).mask(pfx), n.r2_ipc) #need ip_and 24 here for linux
        n.r2.add_route(n.c.ip(v6).mask(pfx), n.r1_ips) #need ip_and 24 here for linux
        return n

    def fos(hosts, v6):
        vr      = 0
        proxy   = 0
        vr0     = None
        for m in hosts:
            if m.type in ['fos_main', 'fos_ssh']:
                if vr == 0:
                    vr0 = m;
                for t in hosts:
                    if t.type in [ 'fos_main', 'fos_vswitch', 'fos_vr', 'fos_ssh']:
                        t.add_fos_vr(vr, m)
                vr=vr+1
            elif m.type == 'fos_vswitch':
                for t in hosts:
                    if t.type in [ 'fos_main', 'fos_vr', 'fos_ssh']:
                        t.add_fos_vswitch(proxy, m)
                proxy=proxy+1

        net = 254

        for proxy in vr0.fos_vswitch.keys():
            ## Configure local and remote end
            ##
            proxy_obj   = vr0.fos_vswitch[proxy]
            vr0_netif   = vr0.netif('eth', nth_not_login=proxy)
            proxy_netif = proxy_obj.netif('eth')

            vr0.add_fos_netpair(proxy, vr0_netif, proxy_netif)
            proxy_obj.add_fos_netpair(proxy, proxy_netif, vr0_netif)

            if v6 == '4and6':
                addr = vr0.alloc_ip(v6='', net = net, prefixlen = 24)
                vr0_netif.add_ip(addr)
                addr = vr0.alloc_ip(v6='6', net = net, prefixlen = 64)
                vr0_netif.add_ip(addr)

                addr = vr0.alloc_ip(v6='', net = net, prefixlen = 24)
                proxy_netif.add_ip(addr)
                addr = vr0.alloc_ip(v6='6', net = net, prefixlen = 64)
                proxy_netif.add_ip(addr)
            else:
                addr = vr0.alloc_ip(v6=v6, net = net, prefixlen = IF(v6, 64, 24))
                vr0_netif.add_ip(addr)
                addr = vr0.alloc_ip(v6=v6, net = net, prefixlen = IF(v6, 64, 24))
                proxy_netif.add_ip(addr)
            net=net-1
        return hosts

    if layout == 'ownlayout':
        return hosts
    elif layout == 'fos':
        return fos(hosts, v6)
    elif layout == 'default':
        for t in hosts:
            if v6 == '4and6':
                t.ts.primary_ip  = t.add_ip(v6='')
                t.ts.primary_ip6 = t.add_ip(v6='6')
            else:
                t.ts.primary_ip = t.add_ip(v6=v6) # used in t.ip()
                t.ts.primary_ip6 = t.ts.primary_ip
        return hosts
    elif layout == 'vlan':
        vlan_id = hosts[0].alloc_vlan()
        for h in hosts:
            iff = h.add_vlan(vlan = vlan_id)
            if v6 == '4and6':
                h.ts.primary_ip  = iff.add_ip(v6='')
                h.ts.primary_ip6 = iff.add_ip(v6='6')
            else:
                h.ts.primary_ip = iff.add_ip(v6=v6)
                h.ts.primary_ip6 = h.ts.primary_ip
        return hosts
    elif layout == 'nat':
        return nat(hosts, '')
    elif layout == 'nat6':
        return nat(hosts, '6')
    elif layout == 'nat2':
        return nat2(hosts, '')
    elif layout == 'nat26':
        return nat2(hosts, '6')
    elif layout == 'bcs':
        return bcs(hosts, '')
    elif layout == 'rcs':
        return rcs(hosts, '')
    elif layout == 'csr':
        return rcs([hosts[2], hosts[0], hosts[1]], '')
    elif layout == 'rcs6':
        return rcs(hosts, '6')
    elif layout == 'rcs2':
        return rcs2(hosts, '')
    elif layout == 'rcs26':
        return rcs2(hosts, '6')
    elif layout == 'ipsec':
        return ipsec(hosts, '')
    elif layout == 'ipsec6':
        return ipsec(hosts, '6')
    else:
        raise config_error('unknown self.net_layout')


def get_next_frame(sock, timeout = ''):
    """
    Returns the first frame received on the passed socket.
       If timeout=-1, an empty dict is returned if no frame is immediately available
    Returns a dict with the keys 'length', 'network', 'transport'
       which contains total length of the IP datagram,
       a dict of all network layer fields,
       a dict of all transport layer fields,
    """
    frame = {}
    if timeout != -1:
        sock.select({ 'r' : (sock.fileno(),) }, timeout = timeout)
        sock.select_post({ 'r' : (sock.fileno(),) })

    if timeout == -1:
        raw_frame = sock.t.sh.send_and_return_all('socktest receive -s %d -l 1500 -N' % sock.fileno())
        # socktest will return this message if no frames are available for the socket when using the -N option
        if (('Failed, errno: ' + sock.t.sh.EWOULDBLOCK) in raw_frame or
            ('Failed, errno: ' + sock.t.sh.EAGAIN) in raw_frame):
            return frame
    else:
        raw_frame = sock.t.sh.send_and_return_all('socktest receive -s %d -l 1500' % sock.fileno())
    layer = 0
    addingpayload = False
    for l in raw_frame:
        # Check if the OSI layer has changed
        l = l.strip()
        if addingpayload:
            if l.find('0x') == 0:
                frame['payload']['hex'] += l.replace('0x','')
                frame['payload']['hex'] += ' '
                continue
            else:
                addingpayload = False
        if l.find('IPv') == 0:
            layer = 3
            continue
        if l.find('ICMP') == 0 or l.find('IGMP') == 0:
            layer = 4
            continue
        if l.find('PAYLOAD') == 0:
            addingpayload = True
            if not frame.has_key('payload'):
                frame['payload'] = {}
                frame['payload']['hex'] = ''
        if l.find(':') < 0:
            continue
        if layer == 4:
            if not frame.has_key('transport'):
                frame['transport'] = {}
            field, data = l.split(' : ')
            frame['transport'][field.strip()] = data.strip()
        elif layer == 3:
            if not frame.has_key('network'):
                frame['network'] = {}
            field, data = l.split(' : ')
            frame['network'][field.strip()] = data.strip()
        elif layer == 0:
            if l.find('Received') >= 0:
                frame['length'] = l.split(' ')[1]
    return frame


def get_specific_frame(sock, frame_filter, timeout = ''):
    """
    Returns the first frame on <sock> where all fields in the frame_filter matches the received frame.
    frame_filter is in the format as returned by get_frame()
    """
    found = False
    while not found:
        frame = get_next_frame(sock, timeout = timeout)
        found = is_in_frame(frame_filter, frame)
    return frame

def is_in_frame(frame_filter, frame):
    found = True
    for f in frame_filter:
        layer_data = frame[f]
        layer_filter = frame_filter[f]
        for field in layer_filter:
            if (not layer_data.has_key(field) or
                layer_data[field].lower().find(layer_filter[field].lower()) != 0):
                found = False
    return found

def recv_until(sock, receive_opts='', done_func=(lambda s , n : True), timeout=-1):
    """
    Call socktest receive on sock expecting the prompt. Once the prompt is encountered,
    pass the text returned to done_func, which returns None if another receive call should
    be made.  Typically a receive timeout will have been set on the socket.
    """
    sh = sock.t.sh
    prompt = re.escape(sh.s.prompt)
    n = 0
    while True:
        sh.send('socktest receive -s %s -l 1500 %s' % (sock.fileno() , receive_opts), newline=True)
        # wait for prompt, but keep 'before'.
        sh.expect_re([prompt], timeout)
        res = done_func(sh.s.s.before, n)
        if res is not None:
            return res
        n = n + 1


def if_nametoindex(session, ifname):
    """
    Returns the interface index for a named interface
    or 0 if no such interface exists.
    """
    lines = session.send_and_return_all('socktest if_nametoindex ' + ifname)
    return int(lines[0])


def wait_for_dad(session, ifname, v6):
    """
    This function will block until there isn't any addresses in
    tentative state on the specified interface
    """
    while True:
        dad_finished = True
        for line in session.send_and_return_all('ifconfig -%s %s' % (IF(v6,'6','4'), ifname)):
            if line.find('tentative') >= 0:
                dad_finished = False
        if dad_finished:
            break
        time.sleep(0.2)
