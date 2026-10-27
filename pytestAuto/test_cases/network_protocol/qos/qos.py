#############################################################################
#
# Copyright (c) 2006-2020, 2022 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

'QoS'

def basic(log, c, s, qarg, buflen, localhost=True):
    log("Set queue and args to %s" % qarg)

    def int2(c,s):
        c.set_sysvar("ipcom.telnet.max_sessions", "0")
        s.set_sysvar("ipcom.telnet.max_sessions", "0")
        # Use some secondary shells, so that if they 'hang' in the test
        # the cleanup may still go through.
        c.ping(s, count=1, retries=4, timeout=5)
        s.ping(c, count=1, retries=4, timeout=5)

        timeout = 240
        s2 = s.ipcom_shell()
        c2 = c.ipcom_shell()
        s2.ttcp_sink(v6 = s.ip().v6, timeout=timeout)
        c2.ttcp_source(s.ip(), v6 = c.ip().v6, buflen=buflen, nbuf=1024, timeout=timeout)
        s2.ttcp_expect(timeout=timeout)
        c2.ttcp_expect(timeout=timeout)

    # RTO recovers much faster if the timestamp option is enabled
    c_shell = c.ipcom_shell()
    c_shell.configure_tcp_timestamp(True)
    s_shell = s.ipcom_shell()
    s_shell.configure_tcp_timestamp(True)

    c.netif().qc_add_queue(qarg)
    s.netif().qc_add_queue(qarg)

    int2(c,s)

    if localhost:
        c.netif(linktype = 'loopback').qc_add_queue(qarg)
        c2 = c.login()
        int2(c,c2)

def basic_udp(log, c, s, qarg, buflen, checkrate, localhost=False):
    log("Set queue and args to %s" % qarg)

    def int2(c,s,checkrate):
        c.set_sysvar("ipcom.telnet.max_sessions", "0")
        s.set_sysvar("ipcom.telnet.max_sessions", "0")
        # Use some secondary shells, so that if they 'hang' in the test
        # the cleanup may still go through.
        c.ping(s, count=1, retries=4, timeout=5)
        s.ping(c, count=1, retries=4, timeout=5)

        timeout = 240
        s2 = s.ipcom_shell()
        c2 = c.ipcom_shell()
        s2.ttcp_sink(v6 = s.ip().v6, timeout=timeout, udp=True)
        c2.ttcp_source(s.ip(), v6 = c.ip().v6, buflen=buflen, nbuf=256, timeout=timeout, udp=True)
        s2.ttcp_expect(timeout=timeout)
        res = c2.ttcp_expect(timeout=timeout)
        #res[2] is KB/sec in ttcp_expect()
        if int(res[2], 10) > checkrate:
            raise test_fail('Really rate %s must be less than setting rate:%d ' % (res[2], checkrate))

    c_shell = c.ipcom_shell()
    s_shell = s.ipcom_shell()

    c.netif().qc_add_queue(qarg)
    s.netif().qc_add_queue(qarg)

    int2(c,s,checkrate)

def check_default_id(c, default_id):
    lines=c.send_and_return_all('qc queue show dev %s' % c.netif().ifname)
    for i in range(len(lines)):
        if lines[i].strip() and lines[i].find('default id: %s' % default_id) != -1:
            return
    else:
        raise test_fail('Can tot find any default id')

class dpaf:
    'Test drop presence-aware-FIFO (DPAF) queue'
    def config(self):
        self.hosts = 2
        self.eta = 8
        self.works_on_gpp = False

    def test(self, log, (c,s), v6, __):
        basic(log, c, s, "dpaf limit 10", 1000)


class htbc:
    'Test rate limit when using Hierarchical Token Bucket Container (HTBC)'
    def config(self):
        self.hosts = 2
        self.eta = 25
        self.works_on_lkm     = False
        self.works_on_gpp = False

    def test(self, log, (c,s), v6, __):
        basic(log, c, s, "htbc rate 100kbps burst 50kB", 700)

class htbc_udp_frag:
    'Test udp large packet(> MTU) rate limit when using Hierarchical Token Bucket Container (HTBC)'
    def config(self):
        self.hosts = 2
        self.eta = 25
        self.works_on_lkm     = False
        self.works_on_gpp = False

    def test(self, log, (c,s), v6, __):
        basic_udp(log, c, s, "htbc rate 200kbps", 8500, 200)

class htbc_default:
    'Test to change default queue when using Hierarchical Token Bucket Container (HTBC)'
    def config(self):
        self.hosts = 1
        self.eta = 25
        self.works_on_lkm     = False
        self.works_on_gpp = False

    def test(self, log, c, v6, __):
        c.netif().qc_add_queue("root handle 1 mbc bands 2 default_band 0")
        c.netif().qc_add_queue("parent 1 handle 1000 htbc rate 70kbps")
        check_default_id(c, '1002')
        c.netif().qc_add_queue("parent 1000 handle 2001 htbc rate 20kbps default")
        check_default_id(c, '2001')

class mbc:
    'Test sorting of traffic flows into different behaviors using Multi Band Container (MBC)'
    def config(self):
        self.hosts = 2
        self.eta = 15
        self.works_on_gpp = False

    def test(self, log, (c,s), v6, __):
        qarg = "mbc bands 2"

        def internal(c,s):
            if c == s:
                netif = c.netif(linktype = 'loopback')
            else:
                netif = s.netif()
            from util import IF
            proto = IF(v6, 58, 1)

            netif.qc_add_queue('handle 1 %s' % qarg)
            netif.qc_add_queue('parent 1 handle 1000 null')
            netif.qc_add_filter('parent 1 handle 1 proto %s flowid 1000' % proto)

            log("The ping should fail since all ICMP traffic is now dropped")
            c.ping(s, count=1, retries=3, timeout=2, succeed=False)
            s.ping(c, count=1, retries=3, timeout=2, succeed=False)
            netif.qc_del_filters('parent 1 handle 1')
            basic(log, c, s, qarg, 1000, localhost=False)

        internal(c,s)
        internal(c,c)


class netemu:
    """Test sending traffic trough the NETMU queue which will simulate a link
    - where packets experience random latency and reordering
    - where some packets are dropped
    - where some packet get corrupted during transit"""
    def config(self):
        self.hosts = 2
        self.eta = 45
        self.works_on_gpp = False
        self.works_on_lkm = False

    def test(self, log, (c,s), v6, __):
        basic(log, c, s, "netemu limit 60 min_latency 20 max_latency 40", 50)
        basic(log, c, s, "netemu limit 10 drop 60", 100)
        basic(log, c, s, "netemu limit 10 corrupt 50 random", 75, localhost=False)
        basic(log, c, s, "netemu limit 60 drop 20 pattern 8", 60, localhost=False)
        basic(log, c, s, "netemu limit 60 drop 20 random", 60, localhost=False)
        basic(log, c, s, "netemu limit 60 drop 20 corrupt 50 random", 60, localhost=False)

class none:
    'Test sending traffic without any queue attached to the interface'
    def config(self):
        self.hosts = 2
        self.eta = 7

    def test(self, log, (c,s), v6, __):
        basic(log, c, s, "none", 1000)


class block_on_netif:
    'Test that a process sending on a blocking socket can block on the outgoing interface'
    def config(self):
        self.hosts = 2
        self.eta = 15
        self.works_on_gpp = False
        self.works_on_lkm = False

    def test(self, log, hosts, v6, __):
        nut, peer = hosts
        nut_shell = nut.ipcom_shell()
        peer_shell = peer.ipcom_shell()

        nut.netif().qc_add_queue('netemu limit 4 min_latency 20 max_latency 50')

        nut_shell.try_flood(peer_shell, 10, peer.netif().ip(v6), v6)


class hierarchy:
    'Configure and run traffic through a hierarchy of queues'
    def config(self):
        self.hosts = 2
        self.eta = 5
        self.works_on_gpp = False
        self.works_on_lkm = False

    def test(self, log, hosts, v6, __):
        nut, peer = hosts
        nut_shell = nut.ipcom_shell()
        peer_shell = peer.ipcom_shell()

        netif = nut.netif()

        # Add verification of defect WIND00140644
        netif.qc_add_queue('root handle 10 mbc bands 2 default_band 1')
        netif.qc_add_queue('parent 10 handle 1000 htbc rate 15Mbit burst 64kB')
        # This line will cause a kernel panic if defect WIND00140644
        # is present
        netif.qc_add_queue('parent 1000 handle 1002 fifo limit 100')

        nut_shell.try_flood(peer_shell, 3, peer.netif().ip(v6), v6)


class invalid_config:
    'Pass a number of invalid configurations to the qc command'
    def config(self):
        self.hosts = 1
        self.eta = 1

    def test(self, log, hosts, v6, __):
        nut = hosts
        nut_shell = nut.ipcom_shell()

        netif = nut.netif()

        # Add verification of defect WIND00140644
        netif.qc_add_queue('root handle 10 mbc bands 2 default_band 1')
        # This line will cause a kernel panic if defect WIND00140644
        # is present
        netif.qc_add_queue('parent 10 handle 11 htbc rate 15Mbit burst 64kB', succeed=False)


        for cmd in ['root handle 10 mbc bandsXX 2 default_band 1',
                    'root htbc rate 15millibit burst 100kB',
                    'root fifo limit -10',
                    'root non_existing_type a 1']:
            netif.qc_add_queue(cmd, succeed=False)

        # Following must fail since ID=1 is reused by a child
        netif.qc_add_queue('root handle 1 htbc rate 2Mbit')
        netif.qc_add_queue('parent 1 handle 3 htbc rate 2Mbit')
        netif.qc_add_queue('parent 3 handle 1 mbc bands 2', succeed=False)

        # The following lines will cause a kernel panic if defect
        # WIND00179681 is present (using the same ID twice)
        netif.qc_add_queue('root handle 1 htbc rate 2Mbit')
        netif.qc_add_queue('parent 1 handle 1 mbc bands 2', succeed=False)

        # The following lines will cause a kernel panic if defect
        # WIND00179681 is present (replacing a non-existing MBC band
        # with another MBC)
        netif.qc_add_queue('root handle 1 htbc rate 2Mbit')
        netif.qc_add_queue('parent 1 handle 3 mbc bands 2')
        netif.qc_add_queue('parent 3 handle 5 mbc bands 2', succeed=False)

