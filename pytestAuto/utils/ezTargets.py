import tempfile
from abc import ABCMeta, abstractmethod
from io import IOBase
import logging
import os
import re
import sys
import threading
import time

import pexpect


from utils.ezTestEngine import ip, ShellOperations, telnet, shell_ops, session
from utils.ezUtils import checkPath, runCmd, shCmd, readYaml, readYamlConfig
from utils.util import IF, abnet, abnet6
from utils.log_record import log


class VLMException(Exception): pass


class ConfigError(Exception): pass


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('>>> %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def createTapName(board, prefix='tap'):
    name = '%s-%s' % (prefix, board)
    if len(name) >= 16:
        raise ConfigError('Tap name {name} length exceeds 15')
    return name


def createNetDevId(ip, prefix='mynet'):
    return '%s%s' % (prefix, ip.get_raw_addr()[3])


def createMacAddr(ip):
    a, b, c, d = ip.get_raw_addr()
    oui = '00:40:47'  # Wind River OUI (Organizationally Unique Identifier)
    return '%s:%02x:%02x:%02x' % (oui, b, c, d)


def netmaskStr2Hex(ip4Mask, prefix=''):
    return prefix + ''.join(['{:02x}'.format(int(x)) for x in ip4Mask.split('.')])


def netmaskHex2Str(ip4Mask):
    if len(ip4Mask) != 8:
        raise ConfigError(f'{ip4Mask} has incorrect format')
    rets = []
    for i in range(0, 8, 2):
        print(i, type(i))
        s = '0x%s' % ip4Mask[i:i + 2]
        rets.append(str(int(s, base=16)))
    return '.'.join(rets)


wants_to_quit = False


def safe(f, *args, **kwargs):
    """runs something and silently discards errors"""
    try:
        f(*args, **kwargs)
    except KeyboardInterrupt:
        global wants_to_quit
        wants_to_quit = True
        try:
            f(*args, **kwargs)
        except:
            pass
    except:
        #        raise #uncomment for testengine debugging
        try:
            Target.wait_prompt(1)  # not possible
        except:  # pexpect.TIMEOUT:
            pass


class Image(metaclass=ABCMeta):
    def __init__(self, bin, dtb=None, user=None, passwd=None, debug=False):
        self.bin = bin
        self.dtb = dtb
        self.user = user
        self.passwd = passwd
        self.debug = debug
        # checkPath(self.bin)
        if self.dtb is not None:
            checkPath(self.dtb)

    @abstractmethod
    def run(self, command, logfile=None):
        pass

    def getBin(self):
        return self.bin

    def getDtb(self):
        return self.dtb


class VxWorksImage(Image):
    def run(self, console):
        log.debug('VxWorksImage.run()')
        expect_array = [
            '-> ',  # 0
            'assword: ',  # 1
            'ogin: ',  # 2
            # 'Login Banner #1',  # xiaozhan, for FTP test suite
        ]

        for _ in range(3):
            try:
                i = console.expect(expect_array)
                if i == 2:  # 'ogin: ',
                    log.debug('found vxworks login:')
                    if not self.user:
                        raise ConfigError('%s\nA user was required but none configured for target: %s at %s:%s\n%s' % (
                            'x' * 79, self.name, self.addr, self.port, 'x' * 80))
                    console.sendline(self.user)
                if i == 1:  # 'assword: ',
                    log.debug('found vxworks password:')
                    if not self.passwd:
                        raise ConfigError(
                            '%s\nA password was required but none configured for target: %s at %s:%s\n%s' % (
                                'x' * 79, self.name, self.addr, self.port, 'x' * 80))
                    console.sendline(self.passwd)
                if i == 0:  # '-> ',
                    log.debug('found vxworks C interpreter ->')
                    break
                # xiaozhan, add
                # if i == 3:  # ''Login Banner #1',
                #     log.debug('found login banner')
                #     break
            except pexpect.TIMEOUT:
                console.send('\r')
        else:
            raise ConfigError('Failed to start vxworks image')


# only work for Ubuntu 20.04 image focal-server-cloudimg-amd64.img
class LinuxImage(Image):
    def __init__(self, bin, dtb=None, user=None, passwd=None, debug=False, prompt=None, device=None):
        super().__init__(bin, dtb, user, passwd, debug)
        self.configYaml = 'config/ezConfigTargetQEMUs.yaml'
        log.debug(f'=============using config========== {self.configYaml}')
        self.config = readYamlConfig(self.configYaml, key='LINUX-IMAGE')
        self.bin = self.config['image']  # xiaozhan debug, this is the linux bin
        self.prompt = self.config['prompt']
        self.device = self.config['device']
        self.user = self.config['user']
        self.passwd = self.config['passwd']

    def run(self, console):
        log.debug('LinuxImage.run()')
        expect_array = [
            self.prompt,  # 0
            'Password: ',  # 1
            'ubuntu login: ',  # 2
        ]

        for _ in range(3):
            try:
                i = console.expect_exact(expect_array)
                # i = console.expect(expect_array)
                if i == 2:  # 'ogin: ',
                    log.debug('found Ubuntu login:')
                    if not self.user:
                        raise ConfigError('%s\nA user was required but none configured for target: %s at %s:%s\n%s' % (
                            'x' * 79, self.name, self.addr, self.port, 'x' * 80))
                    console.sendline(self.user)
                if i == 1:  # 'assword: ',
                    log.debug('found Ubuntu password:')
                    if not self.passwd:
                        raise ConfigError(
                            '%s\nA password was required but none configured for target: %s at %s:%s\n%s' % (
                                'x' * 79, self.name, self.addr, self.port, 'x' * 80))
                    console.sendline(self.passwd)
                if i == 0:  # '-> ',
                    log.debug('found Ubuntu prompt')
                    break
            except pexpect.TIMEOUT:
                console.send('\r')
        else:
            raise ConfigError('Failed to start Ubuntu image')


class ip_exception(Exception):
    def __init__(self, s):
        self.msg = s

    def __str__(self):
        return self.msg


class config_error(ip_exception):
    """Raised if the config setup is bad"""
    pass


class engine_error(ip_exception):
    "Raised when there's a bug in the test engine or your test app"
    pass


class test_fail(ip_exception):
    """Raised when the target stack fails a test case"""
    pass


class engine_state(object):
    # engine state/bookkeeping
    # Only keep 1 global all the time (singleton)
    # This is so different targets dont select the same IP to add to an interface for example.
    def __init__(self):
        self.ip_count = 1
        self.net_count = 1
        self.ip_count6 = 1
        self.net_count6 = 1
        self.ips = {}  # keep track of what ips have been used so we can alloc new ones.
        self.vlan_range = (3, 4094)  # vlans_used = []
        self.vlan_count = 3

    def alloc_ip(self, v6='', net=None, addr=None, prefixlen=None):
        if v6 and net == 0:
            raise 'nope'

        if addr:
            addr = ip(addr)
            if addr in self.ips:
                self.ips[addr] = self.ips[addr] + 1
            else:
                self.ips[addr] = 1
            return addr

        if prefixlen == None:
            prefixlen = IF(v6, 112, 24)
        if v6:
            if net == None:
                net = self.net_count6

            parts = abnet6.strip(':')
            parts = abnet6.split(':')
            while len(parts) < 8:
                parts.append('0')

            index = prefixlen / 16
            parts[index - 1] = str(net)
            parts[index] = str(self.ip_count6)

            # s = '%s:%X:%X' % (abnet6, net, self.ip_count6) #(2000:ln)::net:hostid
            self.ip_count6 += 1
            s = ":".join(parts)
        else:
            if net == None:
                net = self.net_count
            s = abnet + str(net) + '.' + str(self.ip_count)
            self.ip_count += 1
        s = s + '/%s' % prefixlen
        a = ip(s)
        self.ips[a] = 1
        return a

    def free_ip(self, addr):
        addr = ip(addr)
        if addr in self.ips and self.ips[addr] > 1:
            self.ips[addr] = self.ips[addr] - 1
        else:
            self.ips.pop(addr)

    def alloc_vlan(self):
        self.vlan_count += 1
        if self.vlan_count > self.vlan_range[1]:
            self.vlan_count = self.vlan_range[0]
        return self.vlan_count


global es
es = engine_state()


class netif(object):
    """
    A cached view of the actual network interfaces present.
    Variables:
    .addrs
    a dict(ionary) with addresses as keys
    retrieve with 'for addr in myip.addrs: print addr'

    .vr
    virtual router

    .ifname
    like 'eth0'

    .linktype
    'eth', 'loopback', 'vlan', 'tunnel'

    .mac
    as string

    for tunnels:
    .local_ip
    .remote_ip
    .tunnel_ttl
    """
    tun_count = 0

    def alloc_tun():
        '''used to acquire a unique tun device name.
        (doesnt separate diff kinds of tuns since they may only be called whatever on linux).
        these are unique over vr:s.'''
        netif.tun_count += 1
        # if netif.tun_count > netif.tun_range[1]:
        #    netif.tun_count = netif.tun_range[0]
        return netif.tun_count

    alloc_tun = staticmethod(alloc_tun)

    mpls_count = 0

    def alloc_mpls():
        netif.mpls_count += 1
        # if netif.mpls_count > netif.mpls_range[1]:
        #    netif.mpls_count = netif.mpls_range[0]
        return netif.mpls_count

    alloc_mpls = staticmethod(alloc_mpls)

    pppoe_count = 0

    def alloc_pppoe():
        netif.pppoe_count += 1
        return netif.pppoe_count

    alloc_pppoe = staticmethod(alloc_pppoe)

    def __init__(self, a_target):
        self.t = a_target
        self.addrs = {}
        self.dont_destroy_me = False
        self.dont_remove_ips = {}

    def las_prefix(self, vr=None):
        if vr is None:
            vr = self.vr
        return self.t.las_prefix(vr)

    def from_existing(self, ifname, vr, addrs, mac, linktype, tunnel_local_ip=None, tunnel_remote_ip=None,
                      tunnel_ttl=None):
        self.ifname = ifname
        self.vr = vr
        self.t.ts.netifs.append(self)  # xiaozhan, check ts
        self.addrs = addrs
        self.dont_remove_ips = dict(addrs)
        self.isup = vr == 0  # !!! wrong
        self.dont_destroy_me = True
        self.linktype = linktype  # eth, loopback, vlan, tunnel
        self.local_ip = tunnel_local_ip
        self.remote_ip = tunnel_remote_ip
        self.tunnel_ttl = tunnel_ttl
        self.mac = mac
        for a in addrs:
            es.alloc_ip(addr=a)  # xiaozhan, check es

    def rescan(self):
        """update the cached view of the interface. needed when something outside the
        testengine has changed the interface, like added an address. for example
        dhcp, ppp, mpls"""
        ifs = self.t._gather_existing_ifs()
        for i in ifs:
            if self.vr == i[1] and self.ifname == i[0]:
                me = i
                break
        else:
            raise test_fail('oops, netif gone')
        self.from_existing(*me)

    def __str__(self):
        s = ''
        for x in self.__dict__:
            s += "%s = %s\n" % (x, self.__dict__[x])
        return s

    def new(self, addr=None, vr=0, up=True,
            ifname=None,  # only allowed for ipnet (if you want to specify a specific ifname)
            vlan=False, vlan_parent_netif=None,
            pppoe=False, pppoe_parent_netif=None,
            tunnel=False, tunnel_local_ip=None, tunnel_remote_ip=None, tunnel_ttl=None,
            mpls=False, mpls_key=None):
        """vlan = ("new",  parent_netif) -> allocs new vlan id. number -> use this number. number may not be 0.
        tunnel = (ip|gre|min, local_ip, remote_ip, ttl)
        addr = None/"new"/ip[/prefixlen]
        """
        self.mac = None
        self.isup = False
        if vlan:
            self.parent_netif = self.t.get_dev(vlan_parent_netif)
            self.mac = self.parent_netif.mac
        elif pppoe:
            self.parent_netif = self.t.get_dev(pppoe_parent_netif)

        self.vr = vr
        if tunnel_local_ip:
            self.local_ip = ip(tunnel_local_ip)
        if tunnel_remote_ip:
            self.remote_ip = ip(tunnel_remote_ip)
        self.tunnel_ttl = tunnel_ttl

        if vlan:
            self.linktype = 'vlan'
        elif tunnel:
            self.linktype = 'tunnel'
        elif mpls:
            self.linktype = 'mpls'
        elif pppoe:
            self.linktype = 'pppoe'
        elif ifname[:2] == 'lo':
            self.linktype = 'loopback'

        if vlan:
            if vlan == 'new':
                self.id = es.alloc_vlan()
            else:
                self.id = vlan

        # make a name
        if ifname:
            self.ifname = ifname
        else:
            if vlan:
                self.ifname = 'vlan'

                def is_ifname_taken(num):
                    for iff in self.t.netifs:
                        if iff.vr == self.vr and iff.ifname == self.ifname + str(num):
                            return True
                    return False

                num = self.id  # preferrably if possible
                while is_ifname_taken(num):
                    num += 1
                self.ifname += str(num)  # !!!wont work on linux
            elif tunnel:
                # tuntype, local_ip, remote_ip, ttl = tunnel
                if tunnel == 'ip':
                    self.ifname = 'gif'
                elif tunnel == 'gre':
                    self.ifname = 'gre'
                elif tunnel == 'min':
                    self.ifname = 'gremin'
                elif tunnel == '6over4':
                    self.ifname = '6over4_'
                elif tunnel == '6to4':
                    self.ifname = '6to4_'
                elif tunnel == 'sit':
                    self.ifname = 'sit'
                else:
                    raise engine_error('not yet')
                self.ifname += str(netif.alloc_tun())
            elif mpls:
                self.ifname = 'mpls%s' % netif.alloc_mpls()
                self.mpls_key = mpls_key
            elif pppoe:
                self.ifname = 'pppoe%s' % netif.alloc_pppoe()
            else:
                raise engine_error('not yet')

        # create
        try:
            if self.linktype == 'mpls':  # subclass?
                self.t.sh.expect_prompt(self.las_prefix() + 'mplsctl -a -I %s' % self.ifname)
                self.t.sh.expect_prompt(self.las_prefix() + 'mplsctl -b -I %s -n %s' % (self.ifname, self.mpls_key))
                if self.vr:
                    self.set_vr(self.vr)
            else:
                self._create()
        except:
            raise
        self.t.netifs.append(self)

        # make type
        try:
            self.isup = False
            if self.linktype == 'vlan':
                self._set_vlan()
            elif self.linktype == 'tunnel':
                if hasattr(self, 'local_ip'):
                    self.local_ip = ip(tunnel_local_ip)
                    self.remote_ip = ip(tunnel_remote_ip)
                    self._make_tun()
            elif self.linktype == 'mpls' or self.linktype == 'loopback':
                pass
            elif self.linktype == 'pppoe':
                self._make_pppoe()
            else:
                raise ''

            if addr == None:
                pass
            elif isinstance(addr, str) and addr == 'new':
                self.add_ip(up=False)
            # elif isinstance(addr, ip):
            else:
                addr = ip(addr)
                self.add_ip(addr, up=False)

            if up:
                self.up()
        except:
            self.destroy(cleanup=True)
            raise

    def destroy(self, cleanup=False):
        self.t.ts.netifs.remove(self)
        addrs = [x for x in self.addrs if x not in self.dont_remove_ips]
        while addrs:
            safe(self.del_ip, addrs.pop(), cleanup=cleanup)
        if self.dont_destroy_me:
            return
        if self.linktype == 'mpls':
            self.down(cleanup)
            self.set_vr(0)
            s = self.las_prefix() + 'mplsctl -d -I %s' % self.ifname
            self.t.sh.expect_prompt(s, cleanup)
        else:
            self.down(cleanup)
            safe(self._destroy, cleanup=cleanup)

    def set_vr(self, vr):
        if vr == 0 and self.vr == 0:
            return
        self._set_vr(vr)
        self.vr = vr

    def set_vlan(self, vlan, live=False):
        "if live = True, change vlan id tag on the fly without bringing it down first"
        wasup = self.isup
        if not live:
            self.down()
        self._set_vlan(vlan)
        if not live and self.wasup:
            self.up()

    def get_link_addr(self):
        raise test_fail('Must be implemented by subclass since it is target type specific')

    def add_ip(self, addr=None, v6='', net=None, up=True, tentative=False, cga=False, primary=False):
        """
        To primary ethernet test netif
        addr = None will allocate a new, previously unused ip-address. ipv6 if v6 != ''
        net = one of [1..254], to add the new ip to another subnet
        up: change to make the netif Not go up (if it already isn't)
        """
        # !!!todo add cleanup option
        if addr:
            addr = es.alloc_ip(addr=addr)
        else:
            addr = es.alloc_ip(v6, net)

        try:
            self._add_ip(addr, tentative, cga, primary)
            time.sleep(
                0.3)  # add ti avoid test_fail: expect_prompt: linux wanted nothing. got: "['sudo ip link set vlan5 up']"
        except:
            es.free_ip(addr)
            raise

        self.addrs[addr] = True  # !!! +=1?
        if up:
            self.up()

        return addr

    def del_ip(self, addr, cleanup=False):
        addr = ip(addr)
        es.free_ip(addr)
        self.addrs.pop(addr)
        try:
            self._del_ip(addr)
        except:
            if not cleanup:
                raise

    def ip(self, v6=''):
        """
        returns primary test address of this interface.
        pass the v6 from the test() function argument
        if v6 == '6', primary ipv6 is returned
        """
        for a in self.addrs:
            if a.v6 == v6:
                if not a.is_multicast():
                    if a.addr.find('fe80') != 0:
                        # Non link local address
                        return a

    def link_local_unicast_ip6(self):
        """
        returns first link-local unicast IPv6 address of this interface.
        """
        for a in self.addrs:
            if a.v6 == '6':
                if not a.is_multicast():
                    if a.addr.startswith('fe80'):
                        # link local address
                        return a

    def get_link_flag(self, link_flag_id):
        "Returns the current state of the specified interface link flag (0, 1 or 2)"
        for line in self.t.sh.send_and_return_all(self.las_prefix() + 'ifconfig %s' % self.ifname):
            if 'LINK%d' % link_flag_id in line:
                return True
        return False

    def set_link_flag(self, link_flag_id, enable, cleanup=False):
        "Enables/disables the state of link flag 0, 1 or 2"
        if not cleanup:
            self.t.push_state_restorer(self.set_link_flag, (link_flag_id,
                                                            self.get_link_flag(link_flag_id),
                                                            True))
        self.t.sh.expect_prompt(self.las_prefix() + 'ifconfig %s %slink%d'
                                % (self.ifname, IF(enable, '', '-'), link_flag_id))

    def _qc_cmd(self, cmd):
        self.t.sh.expect_prompt(self.las_prefix() + 'qc ' + cmd)

    def qc(self):
        self._qc_cmd('-V 1 queue add dev %s netemu limit 10 drop 10' % self.ifname)

    def qc_add_queue(self, s, succeed=True):
        try:
            self._qc_cmd('queue add dev %s %s' % (self.ifname, s))
            self.t.push_state_restorer(self.qc_del_queues, [])
        except test_fail:
            if succeed:
                raise
            # else: command failed just as expected

    def qc_add_filter(self, s):
        self._qc_cmd('filter add dev %s %s' % (self.ifname, s))

    def qc_del_queues(self):
        self._qc_cmd('queue del dev ' + self.ifname)

    def qc_del_filters(self, s):
        self._qc_cmd('filter del dev %s %s' % (self.ifname, s))


# from KONG,xiaozhan
class netif_iptarget(netif):
    def _create(self):
        vr = IF(self.vr, '-V %s ' % self.vr, '')
        s = 'ifconfig %s%s create' % (vr, self.ifname)
        self.t.sh.expect_prompt(s)

    def _destroy(self, cleanup):
        vr = IF(self.vr, '-V %s ' % self.vr, '')
        if self.linktype == 'pppoe':
            s = 'ifconfig %s%s detach' % (vr, self.ifname)
            time.sleep(2)
        else:
            s = 'ifconfig %s%s destroy' % (vr, self.ifname)
        self.t.sh.expect_prompt(s, cleanup)

    def _set_vlan(self):
        vr = IF(self.vr, "-V %s " % self.vr, "")
        parentvr = IF(self.vr != 0, "#%s" % self.parent_netif.vr, "")
        self.t.sh.expect_prompt(
            'ifconfig %s%s vlan %s vlanif %s%s' % (vr, self.ifname, self.id, self.parent_netif.ifname, parentvr))
        # set mtu to 1496
        self.mtu('1496')

    def _make_tun(self):
        vr = IF(self.vr, "-V %s " % self.vr, '')
        self.t.sh.expect_prompt('ifconfig %s%s inet%s tunnel %s %s'
                                % (vr,
                                   self.ifname,
                                   self.local_ip.v6,
                                   self.local_ip.addr,
                                   self.remote_ip.addr))

        if self.ifname.find("gremin") != -1:
            self.t.sh.expect_prompt('ifconfig %s%s link0' % (vr, self.ifname))

    def _make_pppoe(self):
        vr = IF(self.vr, "-V %s " % self.vr, '')
        self.t.sh.send('pppconfig %s%s pppoe-setif %s' % (vr, self.ifname, self.parent_netif.ifname))
        self.t.sh.expect_exact('pppconfig: ok')
        self.t.sh.wait_prompt()

    def _set_vr(self, vr):
        self.t.sh.expect_prompt('ifconfig -V %s %s vr %s' % (self.vr, self.ifname, vr))

    def nodad_str(self, v6):
        if v6:
            for line in self.t.sh.send_and_return_all('ifconfig'):
                if line.find('nodad') >= 0:
                    return ' nodad'
        return ''

    def _add_ip(self, addr, tentative, cga, primary):
        vr = IF(self.vr, "-V %s " % self.vr, '')
        t = IF(tentative, ' tentative', self.nodad_str(addr.v6))
        c = IF(cga, ' cga', '')
        a = IF(primary, '', 'add ')
        self.t.sh.expect_prompt('ifconfig %s%s inet%s %s%s%s%s' % (vr, self.ifname, addr.v6, a, addr, t, c))
        return addr

    def _del_ip(self, addr):
        vr = IF(self.vr, "-V %s " % self.vr, '')
        self.t.sh.expect_prompt('ifconfig %s%s inet%s delete %s' % (vr, self.ifname, addr.v6, addr))

    def up(self, cleanup=False, _state='up'):
        if self.isup and _state == 'up':
            return
        vr = IF(self.vr, "-V %s " % self.vr, '')
        self.t.sh.expect_prompt('ifconfig %s%s %s' % (vr, self.ifname, _state))
        self.isup = _state == 'up'

    def down(self, cleanup=False):
        if not self.isup:
            return
        self.up(cleanup, _state='down')

    def mtu(self, new_mtu):
        "set interace MTU"
        vr_arg = IF(self.vr, '-V %s ' % self.vr, '')
        self.t.sh.expect_prompt('ifconfig %s%s mtu %s' % (vr_arg, self.ifname, new_mtu))

    def get_mtu(self):
        "returns interface MTU"
        vr_arg = IF(self.vr, '-V %s ' % self.vr, '')
        for line in self.t.sh.send_and_return_all('ifconfig %s%s' % (vr_arg, self.ifname)):
            m = re.match(r'.*?MTU:(\d+) ', line)
            if m:
                return m.group(1)
        raise engine_error('Cannot determine MTU for %s' % self.ifname)

    def get_link_addr(self):
        "returns link address of interface"
        for line in self.t.sh.send_and_return_all('ifconfig %s%s' %
                                                  (IF(self.vr, '-V %s ' % self.vr, ''),
                                                   self.ifname)):
            m = re.match(r'.*HWaddr (\S+)', line)
            if m:
                return m.group(1)
        return ''


# from KONG, xiaozhan
class netif_ipnet(netif_iptarget):
    pass


class session(object):
    def __init__(self, log=None, logverbose=None, addr=None, port=None, user=None, passwd=None, name=None, native=False,
                 dry=None, relogin=False, target_access=None, target_prefix=None, timeout=30):  # interactive=False
        # relogin = hack since ipcom shell share the same prompt variable across login shells
        # self.__dict__.update(kwargs)
        self.relogin = relogin
        self.login_ip = ip('%s/24' % addr)
        self.native = native
        self.port = port
        self.user = user
        self.passwd = passwd
        self.name = name
        self.dry = dry
        self.log = log
        self.logverbose = logverbose
        self.target_access = target_access
        self.target_prefix = target_prefix
        self.timeout = timeout
        self.prompt_magic = 'XunXiqX'  #
        # if name:
        self.prompt = name + '_' + self.prompt_magic
        self.bailmsg = '%s\nYou probably forgot to start the target: %s at %s:%s\n%s' % (
            'x' * 79, name, addr, port, 'x' * 80)
        self.sudo = '%s'
        # self.interactive=interactive
        # self.errnos = errnos_default
        self.errnos = None

    # pexpect session is stored in self.s between __init__ and second_init
    def second_init(self, timeout=30):
        self.s.timeout = timeout

    def login(self):
        for t in range(3):
            try:
                self._login()
            except config_error:
                pass
                # print "try %s" % t
            else:
                break
        else:
            self.log("Couldn't login to %s at %s://%s%s@%s:%s" % (
                self.name, self.type, self.user, IF(self.passwd is None, "", ':%s' % self.passwd), self.login_ip.addr,
                self.port), echo=True)
            raise config_error("4" + self.bailmsg)

    def send(self, cmd, newline, sudo=True):
        # print "%d:%s" % (len(cmd), cmd)
        ncmd = cmd
        # Joels super fix. When communicating with Linux/LKM targets over telnet
        # certain line length gives output garbled with escape characters.
        # Solution: Prepend with couple of blanks.
        if len(ncmd) == 57 or len(ncmd) == 60:
            ncmd = "  " + ncmd
        if newline:
            self.s.sendline(ncmd)
        else:
            self.s.send(ncmd)
        return cmd


class Target(metaclass=ABCMeta):
    def __init__(self, board, configYaml=None, logFile=None, timeout=20):
        # self._checkPexpectVersion()   # xiaozhan remove
        self.board = board
        self.configYaml = configYaml
        self.timeout = timeout
        # xiaozhan, add below
        self.console = None
        self.bridge = None
        self.image = None
        self.ip = None
        self.hostIp = None
        self.osPrompt = '# '  # xiaozhan, add
        # xiaozhan add,debug
        self.primary_ip = None
        self.primary_ip6 = None
        self.netifs = []

        if logFile is not None:
            if type(logFile) == str:
                self.logFile = open(logFile, 'wb')  # xiaozhan,
                # self.logFile = sys.stdout  # xiaozhan,
            elif isinstance(logFile, IOBase):  # tips: python 3
                self.logFile = logFile
            else:
                raise ConfigError('incorrect logFile %s' % logFile)

    @abstractmethod
    def boot(self, image):
        pass

    @abstractmethod
    def cleanup(self, image):
        pass

    @abstractmethod
    def ip(self):
        pass

    def send(self, cmd):
        if self.console:
            log.info('--- send=%s' % cmd)
            self.console.sendline(cmd)
        else:
            raise VLMException('self.console not set up')

    def expect(self, expect, timeout=20):
        if self.console is not None:
            log.debug('--- expect=%s' % expect)
            return self.console.expect(expect, timeout=timeout)
        else:
            raise VLMException('self.console not set up')

    def sendAndExpect(self, cmd, expect, timeout=20):
        if self.console is not None:
            log.info('--- send=%s' % cmd)
            # log.debug('--- expect=%s' % expect)
            self.console.sendline(cmd)
            return self.console.expect(expect, timeout=timeout)
        else:
            raise VLMException('self.console not set up')

    def sendAndReturnAll(self, cmd, expect, timeout=120):
        """return the lines not empty, each line gets stripped"""
        if self.console is not None:
            log.info('--- send=%s' % cmd)
            # log.debug('--- expect=%s' % expect)
            self.console.sendline(cmd)
            self.console.expect(expect, timeout=timeout)
            # lines = self.console.before.split(b'\n')

            ret = self.console.before.decode("utf-8")  # xiaozhan, debug
            # ret = self.console.before  # xiaozhan, add
            # Remove control codes, see http://dickey.his.com/xterm/xterm.faq.html  # xiaozhan, below operations are key points to remove special characters
            ret = ret.replace('\r\n\r\x00', '')
            ret = ret.replace(' \x08', '')
            ret = ret.replace('^[[A', '')
            ret = ret.replace('^[[K', '')
            lines = ret.split('\r\n')

            # Remove the echo of the executed command
            lines = lines[1:]
            if len(lines) == 0:
                return []

            non_empty_lines = []

            # strip leading / trailing whitespace
            strip_lines = True
            for line in lines:
                if strip_lines:
                    line = line.strip()
                non_empty_lines.append(line)

            # remove any leading empty lines
            while len(non_empty_lines) > 0 and non_empty_lines[0] == '':
                non_empty_lines = non_empty_lines[1:]

            # remove any trailing empty lines
            while len(non_empty_lines) > 0 and non_empty_lines[-1] == '':
                non_empty_lines = non_empty_lines[:-1]
            log.debug('----ret is----')  # xiaozhan add for debug
            log.debug(non_empty_lines)
            return non_empty_lines
            # return list(filter(lambda x: x != '', map(lambda x: x, lines)))
        else:
            raise VLMException('self.console not set up')

    def sendAndReturnAllByTimeout(self, cmd, cmd_timeout=30, strip_lines=True):
        """
        "cmd" is sent to the shell with a "newline" appended.
        A list of lines is returned as result after cmd_timeout seconds.
        All lines are not stripped.
        This funtion is used for the command without any returned prompt/flag, like "route monitor"
        """
        id, logfile = tempfile.mkstemp(prefix='tmp')
        # print('tempfile=%s' % logfile)
        magic_start = 'start_magic_start'
        magic_stop = 'stop_magic_stop'

        # save pexpect config
        old_timeout = self.console.timeout
        old_logfile = self.console.logfile

        with open(logfile, 'w') as fdw:
            self.console.logfile = fdw

            self.console.sendline('echo ' + magic_start + '\n')
            self.console.expect(magic_start)
            # print('step1')
            self.console.send(cmd + '\n')
            time.sleep(cmd_timeout)

            # print('step2')
            self.console.send('echo ' + magic_stop + '\n')
            self.console.expect(magic_stop)

        # print('step3')
        # restore pexpect config
        self.console.timeout = old_timeout
        self.console.logfile = old_logfile

        with open(logfile, 'r') as fdr:
            content = fdr.read()

        runCmd('rm -f %s' % logfile)

        # different version pexpects return slightly different results--(?s)means searching with changing lines
        ptn = r'(?s)%s\s*(.*?)%s' % (self.osPrompt + cmd, 'echo ' + magic_stop)
        # print('ptn===%s' % ptn)
        found = re.search(ptn, content)
        if found is not None:
            # content = found.groups()[0].replace(magic_start, '').replace('echo ', '').strip()
            content = found.groups()[0].replace(magic_start, '').strip()
            # print('content is:', content)
            # print('content end')
            if strip_lines:
                return [line.strip() for line in content.split('\n')]
            else:
                return [line for line in content.split('\n')]
        else:
            return []

    # def get_ip(self, cmd='ifconfig -a'):
    #     # TODO    xiaozhan, use sendAndReturnAll to get ipv4 and ipv6 addresses to replace the original -- class ip
    #     ret = '\n'.join(self.sendAndReturnAll(cmd, self.osPrompt))
    #     # res = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', ret)
    #     res = re.findall(r'inet (\d+\.\d+\.\d+\.\d+)', ret)
    #     res6 = re.findall(r'inet6 unicast (\d+::\d+)', ret)
    #     if res:
    #         log.debug('IPv4 address-------')
    #         log.debug(res)
    #     if res6:
    #         log.debug('IPv6 address-------')
    #         log.debug(res6)
    #     return res, res6

    # from KONG, xiaozhan add
    def add_vlan(self, *a, **k):
        """shortcut for add_netif() with 'vlan' = 'new'"""
        if 'vlan' not in k:
            k['vlan'] = 'new'
        return self.add_netif(*a, **k)

    def add_netif(self, *a, **k):
        """
        addr = None, vr = 0, up = True,
        ifname = None,
        vlan = False, vlan_parent_netif = None,
        pppoe = False, pppoe_parent_netif = None,
        tunnel = False, tunnel_local_ip = None,  tunnel_remote_ip = None,  tunnel_ttl = None,
        mpls = False, mpls_key = None

        addr: None sets no ip
        'new' allocates one
        ip[/prefixlen] use this ip and optionally prefixlen
        ifname: only allowed for ipnet (if you want to specify a specific ifname)
        vlan: 'new' which allocates a new vlan id.
        or an integer -> use this number. number may not be 0.
        vlan_parent_netif: attach vlan to this netif if chosen
        tunnel = 'ip', 'gre', 'min'

        """
        return self._add_netif(*a, **k)

    def _add_netif(self, *a, **k):
        x = netif_ipnet(self)
        x.new(*a, **k)
        return x

    def netif(self, linktype='eth', vr=0, nth_not_login=0):
        '''
        First network interface of a certain kind (linktype) is returned.
        linktype can be eth, loopback, vlan, tunnel, mpls, etc.
        nth_not_login returns the nth interface of type linktype which is not carrying the login_ip. 1 = 1st'''
        ifs = self.netifs(linktype, vr)
        if nth_not_login == 0:
            for n in ifs:
                if [x for x in n.addrs if self.login_ip() == x]:  # self.s.login_ip in n.addrs?
                    return n
            if ifs != []:
                return ifs[0]
        else:
            non_login_ifs = []
            for n in ifs:
                if [x for x in n.addrs if self.login_ip() == x]:
                    continue
                non_login_ifs.append(n)
            if len(non_login_ifs) >= nth_not_login:
                return non_login_ifs[nth_not_login - 1]
        raise engine_error('Non-existant netif requested')

    def get_dev(self, devname, vr=0):
        """gets the first in the list, no matter vr"""
        if not devname:
            return self.netif(vr=vr)
        if isinstance(devname, netif):
            return devname
        if '#' in devname:
            devname, vr = devname.split('#')
        for d in self.netifs:
            if d.ifname == devname and d.vr == vr:
                return d
        raise engine_error('not found')

    def alloc_ip(self, *a, **k):
        """
        v6='', net = None, addr = None, prefixlen=None
        Reserve a previously unused ip address. If none is given,
        a new one will be given to you with the properties of net/prefixlen specified.
        The parts are 10.luckynumber.<net or latest used net>.ip_count

        """
        # this just propagates to engine_state
        return es.alloc_ip(*a, **k)

    def alloc_vlan(self):
        'acquire new unique vlan ids'
        return es.alloc_vlan()


class VLMTarget(Target):
    def __init__(self, board, configYaml='default', log=None, timeout=20):
        self._checkPexpectVersion()

        if configYaml == 'default':
            self.configYaml = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           'ezConfigTargetVLMs.yaml')
            logger.debug('using default config %s' % self.configYaml)
        else:
            self.configYaml = configYaml
            logger.debug('using customized config %s' % self.configYaml)
        checkPath(self.configYaml)

        self.board = board
        self.timeout = timeout
        self.console = None
        self.status = None
        self.log = log

        self.image = None
        self.ip = None
        self.hostIp = None

        self.config = readYamlConfig(self.configYaml, key=self.board)
        self.bootLoader = self.config['bootLoader']
        self.autoBootFlag = self.config['autoBootFlag']
        self.bootPrompt = self.config['bootPrompt']
        self.osPrompt = self.config['osPrompt']
        self.cmdPrompt = '[vxWorks *]# '
        self.imageStartAddr = self.config['imageStartAddr']
        self.dtbStartAddr = self.config['dtbStartAddr']
        self.netDriver = self.config['netDriver']

        self.defaultHost = readYamlConfig(self.configYaml)['defaultHost']
        logger.debug(f'default host={self.defaultHost}')

        self.user = 'target'
        self.password = 'vxTarget'
        self.vlmTool = '/folk/vlm/commandline/vlmTool'
        self.getAttrOnReserve = True
        self.bootTimeout = 300
        self.bootRetryTime = 2

    def boot(self, image, hostIp=None):
        logger.info('boot %s with %s' % (self.board, image.getBin()))
        checkPath(image.getBin())
        if image.getDtb() is not None:
            checkPath(image.getDtb())
        self.image = image

        if hostIp is None:
            self.hostIp = self.defaultHost
        else:
            self.hostIp = hostIp
        logger.info(f'using host={self.hostIp}')

        for num in range(self.bootRetryTime):
            try:
                self.status = 'UNKNOWN'
                self.unreserve()  # force existing console telnet to disconnect itself

                self.reserve()
                if self.status != 'RESERVED':
                    raise VLMException('failed to reserve the target %s' % self.board)

                self.ip = ip(self.IP_Address, self.IP_Mask)

                self.__setupBootArg(image)
                if self.status != 'SETUP':
                    raise VLMException('failed to setup the target %s' % self.board)

                self.status = 'LOADING'
                self.console.send('\n')
                self.console.expect(self.osPrompt, timeout=60)

                bootloader = self._getBootloaderType()
                if bootloader == 'vxboot':
                    if False:
                        # self.console.send('\n')    # do not send('\n')
                        self.console.expect(self.osPrompt, timeout=60)
                    else:
                        self.image.run(self.console)
                elif bootloader == 'uboot':
                    self.console.send('boot')
                    self.image.run(self.console)
                else:
                    raise ConfigError('')

                logger.info('loaded image %s' % self.image.getBin())
                self.status = 'LOADED'
                break
            except pexpect.TIMEOUT:
                print('\nEXCEPTION: boot image TIMEOUT and retry %s time' % (num + 1))
                self.status = 'LOAD_TIMEOUT'
                self.bootTimeout += 60
                if self.console.isalive():
                    self.console.terminate()
                self.console = None
            except pexpect.EOF:
                print('\nEXCEPTION: boot image EOF and retry %s time' % (num + 1))
                self.status = 'LOAD_EOF'
                if self.console.isalive():
                    self.console.terminate()
                self.console = None

        if self.status != 'LOADED':
            raise VLMException('\nEXCEPTION: failed to load the image %s and %s to the target %s, target status:%s' % (
                self.image.getBin(), self.image.getDtb(), self.board, self.status))

        # reset command line prompt
        self.console.sendAndExpect(f'set prompt "{self.cmdPrompt}"', '# ')
        self.console.close()  # close VLMConsole

        s = telnet(addr=self.Terminal_Server, port=int(self.Terminal_Server_Port) + 2000, name=self.board, timeout=10)
        s.login()
        self.console = s
        return shell_ops(self.console)

    def cleanup(self):
        logger.info(f'cleanup the target{self.board}')
        if self.console is not None:
            self.console.s.sendline('set prompt "%s"' % self.cmdPrompt)
            self.console.s.sendcontrol(']')
            self.console.s.expect('telnet> ')
            self.console.s.sendline('q')
            self.console.s.expect('Connection closed.')
            self.console = None
        return

    def ip(self):
        return self.ip.get_addr_str()

    def connect(self):
        if self.console is not None:
            return self.console

        s = telnet(addr=self.Terminal_Server, port=int(self.Terminal_Server_Port) + 2000, name=self.board, timeout=10)
        s.login()
        self.console = s
        return shell_ops(self.console)

    def disconnect(self):
        return self.cleanup()

    def reserve(self, user=None):
        logger.info('reserve %s' % self.board)
        self.cmdStatus, self.output = self.__vlmToolCmd('reserve', self.board)

        self.status = 'UNKNOWN'

        if self.board in self.output:
            self.status = 'RESERVED'
            if self.getAttrOnReserve:
                self.getAttr(self.output)

        return self.status == 'RESERVED'

    def unreserve(self):
        ''' unreserve a target through the VLM CLI command (vlmTool) '''
        logger.info('unreserve %s' % self.board)
        self.cmdStatus, self.output = self.__vlmToolCmd('unreserve', self.board)

        self.status = 'UNKNOWN'

        if self.output[0] == '1':
            self.status = 'UNRESERVED'

        return self.status == 'UNRESERVED'

    def getAttr(self, output=''):
        logger.info('getAttr %s' % self.board)
        if not output:
            _, self.output = self.__vlmToolCmd('getAttr', self.board)

        displayAtttributes = ('Target_ID',
                              'BSP',
                              'Architecture',
                              'CPU',
                              'Boot_Device',
                              'IP_Address',
                              'IP_Mask',
                              'Gateway',
                              'Reserved_By',
                              'Terminal_Server',
                              'Terminal_Server_Port',
                              )
        for line in [x for x in self.output.split('\n') if x.strip()]:
            k, v = line.split(': ', 1)
            k = k.replace(' ', '_').replace('\t', '')
            setattr(self, k, v.strip())
            if k in displayAtttributes:
                logger.info('\ttarget attribute  "%s" : "%s"' % (k, v))

    def reboot(self):
        logger.info('reboot %s' % self.board)
        self.status = 'UNKNOWN'
        self.cmdStatus, self.output = self.__vlmToolCmd('reboot', self.board)
        self.status = 'REBOOTED'
        return self.status == 'REBOOTED'

    def __setupBootArg(self, build):
        logger.info('setup %s boot args' % self.board)

        self.reboot()
        time.sleep(3)

        self.console = VLMConsole(self.Terminal_Server, int(self.Terminal_Server_Port) + 2000, self.bootPrompt)

        self.console.open()
        self.console.expect(self.autoBootFlag, timeout=self.bootTimeout)

        self.console.send('\n')  # send return key
        self.console.expect(self.bootPrompt, 10)

        bootloader = self._getBootloaderType()
        if bootloader == 'vxboot':
            bootArgs = self.__setupVxbootBootArg(build)
        elif bootloader == 'uboot':
            bootArgs = self.__setupUbootBootArg(build)
        else:
            raise ConfigError('')

        self.status = 'SETUP'
        return self.status == 'SETUP'

    def __setupVxbootBootArg(self, build):
        ''' set up boot parameters for vxboot image
        a) reboot
        b) set up boot parameters
        c) load image automatically
        '''
        # set up vxboot boot parameters, e.g.
        # @gei(0,0)pek-cc-pb02l:/view_test/lchen3/vxcert/tftpboot/vxWorks 
        # h=128.224.160.44 e=128.224.167.56:fffffe00 g=128.224.166.1 u=target tn=itl_64 pw=vxTarget     
        bootArgs = '@%s%s:%s h=%s e=%s:%s g=%s u=%s tn=%s pw=%s' % (
            self.netDriver, self.hostIp, build.getBin(), self.hostIp, self.IP_Address, netmaskStr2Hex(self.IP_Mask),
            self.Gateway, self.user, 'itl_64', self.password)
        logger.info('\tbootArgs: %s' % bootArgs)
        self.console.send(bootArgs)
        self.console.expect(self.osPrompt, timeout=60)
        return bootArgs

    def __setupUbootBootArg(self, build):
        ''' set up boot parameters: bootargs, bootcmd
        a) reboot
        b) go to uboot command line
        c) set up boot parameters
        d) saveenv
        '''
        self.console.send('setenv ipaddr %s' % self.IP_Address)
        self.console.expect(self.bootPrompt)

        self.console.send('setenv netmask %s' % self.IP_Mask)
        self.console.expect(self.bootPrompt)

        self.console.send('setenv serverip %s' % self.hostIp)
        self.console.expect(self.bootPrompt)

        self.console.send('setenv gatewayip %s' % self.Gateway)
        self.console.expect(self.bootPrompt)

        bootCmd = 'tftp %s %s; tftp %s %s; bootm %s - %s' % (
            self.imageStartAddr, build.getBin(), self.dtbStartAddr, build.getDtb(), self.imageStartAddr,
            self.dtbStartAddr)
        bootCmd = 'setenv bootcmd \'%s\'' % bootCmd
        logger.info('\tbootArgs: %s' % bootCmd)
        self.console.send(bootCmd)
        self.console.expect(self.bootPrompt)
        self.console.send('saveenv', 'Erasing SPI flash...Writing to SPI flash...done')
        self.console.expect(self.bootPrompt)

        # self.console.send('printenv')
        # self.console.expect('Environment size: .*? bytes.*?%s' % self.bootPrompt)
        return bootCmd

    def _checkPexpectVersion(self):
        if pexpect.__version__ < '4.2.1':
            print('pexpect version %s not supported, should be 4.2.1 or later' % pexpect.__version__)
            sys.exit(1)

    def _getBootloaderType(self):
        return readYaml(self.configYaml)[self.board]['bootLoader']

    def __vlmToolCmd(self, cmd, *args):
        if cmd == 'reserve':
            params = ' -t %s' % (args[0])
            if self.getAttrOnReserve:
                params += ' -l'
        elif cmd == 'unreserve':
            params = '-t %s' % (args[0])
        elif cmd == 'reboot':
            params = '-t %s' % (args[0])
        elif cmd == 'getAttr':
            params = '-t %s all' % (args[0])
        else:
            raise ConfigError(f'vlmTool command {cmd} not recognized')

        cmd = '%s %s %s' % (self.vlmTool, cmd, params)
        return runCmd(cmd)


class VLMConsole:
    def __init__(self, ip, port, bootPrompt, logFile=None):
        self.console = None
        self.ip = ip
        self.port = port
        self.bootPrompt = bootPrompt
        self.logFile = logFile

    def open(self, timeout=60):
        logger.info(f'open {self.ip} {self.port}')
        if self.console is not None:
            return self.console

        try:
            tcmd = f'telnet {self.ip} {self.port}'
            logger.info(f'{tcmd}')
            self.console = pexpect.spawn(tcmd, echo=False, timeout=timeout)
            if self.logFile is not None:
                self.console.logfile = self.logFile
            connectFlag = str('Connected to %s.' % self.ip)

            expect_array = [r"scape character is '^]'.",  # connected
                            connectFlag,  # connected
                            self.bootPrompt,  # connected and at boot loader
                            '->',  # connected and at vxworks C interpreter
                            pexpect.EOF,  # disconnected
                            pexpect.TIMEOUT,  # time out
                            ]

            connStatuses = ('T_CONNECTED', 'T_CONNECTED',
                            'T_BOOTLOADER', 'T_VXWORKS', 'T_EOF', 'T_TIMEOUT',)
            for _ in range(1):
                i = self.console.expect(expect_array, timeout)
                logger.info('%s returns %s' % (tcmd, connStatuses[i]))
                return self.console
            else:
                raise VLMException('\nFailed to login using telnet: %s %s\n' % (self.ip, self.port))
        except VLMException as e:
            print(e)
            print(self.console.before)

    def close(self):
        logger.info(f'close {self.ip} {self.port}')
        if self.console is not None:
            self.console.sendcontrol(']')
            self.console.expect('telnet> ')
            self.console.sendline('q')
            self.console.expect('Connection closed.')
            self.console = None
        return

    def isalive(self):
        if self.console:
            logger.debug('\n--- isalive')
            return self.console.isalive()
        else:
            raise VLMException('self.console not set up')

    def terminate(self):
        if self.console:
            logger.debug('\n--- terminate')
            return self.console.terminate()
        else:
            raise VLMException('self.console not set up')

    def send(self, cmd):
        if self.console:
            logger.debug('\n--- send="%s"' % cmd)
            self.console.sendline(cmd)
        else:
            raise VLMException('self.console not set up')

    def expect(self, expect, timeout=20):
        if self.console is not None:
            logger.debug('\n--- expect="%s" within %s seconds' % (expect, timeout))
            return self.console.expect(expect, timeout=timeout)
        else:
            raise VLMException('self.console not set up')

    def sendAndExpect(self, cmd, expect, timeout=20):
        if self.console is not None:
            logger.debug('\n--- send="%s" and expect="%s" within %s seconds' % (cmd, expect, timeout))
            self.console.sendline(cmd)
            return self.console.expect(expect, timeout=timeout)
        else:
            raise VLMException('self.console not set up')

    def sendAndReturnAll(self, cmd, expect='-> ', timeout=20):
        '''return the lines not empty, each line gets stripped'''
        if self.console is not None:
            logger.debug('\n--- send="%s", expect="%s" and return all within %s seconds' % (cmd, expect, timeout))
            self.console.sendline(cmd)
            self.console.expect(expect, timeout=timeout)
            # lines = self.console.before.split(b'\n')

            ret = self.console.before.decode("utf-8")
            # Remove control codes, see http://dickey.his.com/xterm/xterm.faq.html
            ret = ret.replace('\r\n\r\x00', '')
            ret = ret.replace(' \x08', '')
            ret = ret.replace('^[[A', '')
            ret = ret.replace('^[[K', '')
            lines = ret.split('\r\n')

            # Remove the echo of the executed command
            lines = lines[1:]
            if len(lines) == 0:
                return []

            non_empty_lines = []

            # strip leading / trailing whitespace
            strip_lines = True
            for line in lines:
                if strip_lines:
                    line = line.strip()
                non_empty_lines.append(line)

            # remove any leading empty lines
            while len(non_empty_lines) > 0 and non_empty_lines[0] == '':
                non_empty_lines = non_empty_lines[1:]

            # remove any trailing empty lines
            while len(non_empty_lines) > 0 and non_empty_lines[-1] == '':
                non_empty_lines = non_empty_lines[:-1]

            return non_empty_lines
            # return list(filter(lambda x: x != '', map(lambda x: x, lines)))
        else:
            raise VLMException('self.console not set up')


class QemuTarget(Target):
    def __init__(self, board, configYaml=None, logFile=None, timeout=20):
        super().__init__(board, configYaml, logFile, timeout)  # xiaozhan
        if configYaml is None:
            self.configYaml = 'config/ezConfigTargetQEMUs.yaml'
        self.console = None
        self.shellOps = None
        self.shelltype = None
        self.image = None
        self.hostIp = None
        self.board = board
        self.cmdPrompt = '# '
        self.timeout = timeout
        self.bridge = readYamlConfig(self.configYaml, key='bridge')
        self.config = readYamlConfig(self.configYaml, key=self.board)
        self.ip = ip(self.config['ip'])  # xiaozhan, I don't want to use this ip class
        assert isinstance(self.ip, ip)
        self.tapName = None
        self.netBuilder = None

    def boot(self, image):
        log.debug('====boot the target %s with %s' % (self.board, image.getBin()))
        if self.netBuilder is None:
            # use singleton NetworkBuilder
            self.netBuilder = NetworkBuilder()
            self.console = self.netBuilder.add(self, image, self.ip)
        return self.console  # xiaozhan, check this console

    def cleanup(self):  # xiaozhan, debug  self.console.s.s  ---��Ϊself.console
        log.debug(f'====cleanup the target {self.board}')
        if self.console is not None:
            # xiaozhan, add for debug
            if not self.console.terminate(force=True):
                log.debug('====use ctrl+c to quit target====')
                self.console.sendcontrol('c')
                self.console.expect(pexpect.EOF)
            # xiaozhan, add, end
        if self.bridge is not None:
            shCmd('sudo ifconfig %s down' % self.tapName)
            shCmd('sudo brctl delif %s %s' % (self.bridge, self.tapName))
            shCmd('sudo tunctl -d  %s' % self.tapName)

        if self.netBuilder is not None:
            self.netBuilder.remove(self)

    def setup(self, image, targetIp=None, bridge=None, hostIp=None):
        log.debug(f'====setup the target {self.board}')
        assert isinstance(targetIp, ip)
        self.bridge = bridge
        self.image = image
        # self.ip = targetIp    # xiaozhan,  remove
        self.hostIp = hostIp
        if self.bridge is not None:
            self.tapName = createTapName(self.board)
            shCmd('sudo tunctl -u $USER -t %s' % self.tapName)
            shCmd('sudo brctl addif %s %s' % (bridge, self.tapName))
            shCmd('sudo ifconfig %s up' % self.tapName)
            return self.tapName
        else:
            return None

    def start(self):
        log.debug(f'====start the target {self.board} {self.ip}')
        cmd = self.__createQemuCmd(self.image, self.ip, self.tapName)
        log.debug('=======start cmd for qemu target %s ===' % self.board)
        log.debug(cmd)

        if isinstance(self.image, LinuxImage):
            self.timeout = 180

        # self.console = pexpect.spawn(cmd, timeout=self.timeout, encoding='utf-8')  # xiaozhan, add encoding='utf-8'
        self.console = pexpect.spawn(cmd, timeout=self.timeout)  # xiaozhan, add encoding='utf-8'
        self.image.run(self.console)
        # xiaozhan add
        if self.logFile is not None:
            self.console.logfile = self.logFile
        # xiaozhan, add for debug
        if isinstance(self.image, VxWorksImage):
            pass
        # xiaozhan, end
        if isinstance(self.image, LinuxImage):
            prompt = self.image.prompt
            device = self.image.device
            ip = self.ip.get_addr_str()
            prefixlen = self.ip.prefixlen
            self.console.sendline(f'sudo ip addr add {ip}/{prefixlen} dev {device}')
            self.console.expect_exact(prompt)
            self.console.sendline(f'sudo ip link set dev {device} up')
            self.console.expect_exact(prompt)
            # xiaozhan,manually add ipv6
            self.console.sendline(f'sudo ip addr add 2000::80/64 dev ens3')  # xiaozhan, add
            self.console.expect_exact(prompt)
        return self.console

    def get_ip(self):
        ip = self.config['ip']  # a.b.c.d/24
        ip6 = self.config['ip6']  # 2000::a/64
        return ip.split('/')[0], ip6.split('/')[0]

    # xiaozhan, echo test  # TODO debug
    def echo_server(self, ip2=None, proto='udp', bufsize=8192, port=7301, echo_once=False, reuse_addr=False,
                   limit_recv=0):
        """for ipcom shell"""
        if not ip2:
            ip2 = self.ip()
        else:
            ip2 = ip(ip2)
        if echo_once:
            echo_once = '-x '
        else:
            echo_once = ''
        if reuse_addr:
            reuse_addr = '-k '
        else:
            reuse_addr = ''

        self.sh.send('echoserver -t %s -b %s -p %s -L %s %s %s %s' % (
        proto, bufsize, port, limit_recv, echo_once, reuse_addr, ip2.addr))
        if proto == 'raw':
            self.sh.expect_exact(['echoserver is now listening at %s.*' % (ip2.addr),
                                  'echoserver is now listening at %s.*' % (ip2.addr.upper())])
        else:
            self.sh.expect_exact(['echoserver is now listening at %s.%s' % (ip2.addr, port),
                                  'echoserver is now listening at %s.%s' % (ip2.addr.upper(), port)])
        self.sh.wait_prompt()

    def ip(self):
        return self.ip.get_addr_str()

    def connect(self):
        if self.shellOps is not None:
            return self.shellOps
        else:
            raise ConfigError(f'{self.board} not booted')

    def disconnect(self):
        pass

    def __createQemuCmd(self, image, ip, tap):
        cmd = 'sudo qemu-system-x86_64 -m %s -smp %s ' % (self.config['memory'], self.config['smp'])

        if 'machine' in self.config:
            cmd += '-machine %s ' % self.config['machine']
        elif 'cpu' in self.config:
            cmd += '-cpu %s ' % self.config['cpu']
        else:
            raise ConfigError(f'either machine or cpu should be defined in {self.config}')

        if 'append' in self.config:
            cmd += '-kernel %s ' % image.getBin()
        elif 'image' in self.config:
            cmd += '-boot order=d -hda %s ' % image.getBin()
        else:
            raise ConfigError(f'either append or image should be defined in {self.config}')

        if ip is not None:
            netDevId = createNetDevId(ip)
            if 'append' in self.config:
                cmd += '-append "%s e=%s" ' % (self.config['append'], ip.get_addr_str())
            elif 'image' in self.config:
                cmd += ''
            cmd += '-netdev tap,id=%s,ifname=%s,script=no,downscript=no ' % (netDevId, tap)
            cmd += '-device e1000,netdev=%s,mac=%s ' % (netDevId, createMacAddr(ip))

        cmd += '--serial %s -nographic -monitor none ' % self.config['serial']

        if 'enable-kvm' in self.config and self.config['enable-kvm']:
            cmd += '-enable-kvm '

        if 'disk' in self.config and self.config['disk']:
            cmd += '-device ahci,id=ahci '
            for i in range(len(self.config['disk'])):
                if self.config['disk'][i].startswith('/'):  # handle abosulate path
                    dst = self.config['disk'][i]
                    checkPath(dst)
                else:
                    dst = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                       self.config['disk'][i])
                    checkPath(dst)
                cmd += '-drive id=disk%s,file=%s,if=none ' % (i + 1, dst)
                cmd += '-device ide-drive,drive=disk%s,bus=ahci.%s ' % (i + 1, i)
        return cmd


class Singleton(object):  # xiaozhan, study this single mode design
    _instance_lock = threading.Lock()

    def __init__(self):
        log.debug('Singleton __init__()')
        pass

    def __new__(cls, *args, **kwargs):
        log.debug('Singleton __new__()')
        if not hasattr(Singleton, "_instance"):
            with Singleton._instance_lock:
                if not hasattr(Singleton, "_instance"):
                    Singleton._instance = object.__new__(cls)
        return Singleton._instance


class NetworkBuilder(Singleton):  # xiaozhan, single mode design to ensure there is only one bridge
    configYaml = None
    bridge = None
    tapNames = None
    targets = None
    builds = None
    ips = None
    consoles = None

    def __init__(self, configYaml=None):
        log.debug('NetworkBuilder __init__()')

        if NetworkBuilder.configYaml is None:
            self.configYaml = 'config/ezConfigTargetQEMUs.yaml'
        if NetworkBuilder.bridge is None:
            NetworkBuilder.bridge = readYamlConfig(self.configYaml, key='bridge')
        if NetworkBuilder.tapNames is None:
            NetworkBuilder.tapNames = []
        if NetworkBuilder.targets is None:
            NetworkBuilder.targets = []
            NetworkBuilder.builds = []
            NetworkBuilder.ips = []
            NetworkBuilder.consoles = []
            self.setup()  # xiaozhan, running setup when init this instance

    def setup(self):
        self.__setupBridge()

    def add(self, target, image, targetIp):
        log.debug('====NetworkBuilder add()====%s' % targetIp)
        assert isinstance(targetIp, ip)

        NetworkBuilder.targets.append(target)
        NetworkBuilder.builds.append(image)
        NetworkBuilder.ips.append(targetIp)

        target.setup(image, targetIp=targetIp, bridge=self.bridge)
        shellOps = target.start()

        netId = targetIp.get_networkid_str()
        log.debug('sudo ifconfig %s inet %s up' % (NetworkBuilder.bridge, netId))  # xiaozhan debug
        shCmd('sudo ifconfig %s inet %s up' % (NetworkBuilder.bridge, netId))

        NetworkBuilder.consoles.append(shellOps)
        return shellOps

    def remove(self, target):
        log.debug('NetworkBuilder remove()')
        i = NetworkBuilder.targets.index(target)
        NetworkBuilder.targets.remove(target)
        NetworkBuilder.builds.remove(NetworkBuilder.builds[i])
        NetworkBuilder.ips.remove(NetworkBuilder.ips[i])
        if not NetworkBuilder.targets:
            self.cleanup()

    def cleanup(self):
        log.debug('====NetworkBuilder cleanup()====')
        self.__cleanupBridge()

    def __checkConfig(self):
        assert len(NetworkBuilder.targets) == len(NetworkBuilder.builds) == len(NetworkBuilder.ips)

    def __setupBridge(self):
        if not self.__isBridgeExisted(NetworkBuilder.bridge):
            log.debug('======create bridge======')
            shCmd('sudo brctl addbr %s' % NetworkBuilder.bridge)
            shCmd('sudo brctl sethello %s 10' % NetworkBuilder.bridge)
            shCmd('sudo brctl setfd %s 0' % NetworkBuilder.bridge)

    def __cleanupBridge(self):
        if NetworkBuilder.bridge is not None:
            shCmd('sudo ip link set %s down' % NetworkBuilder.bridge)
            shCmd('sudo brctl delbr %s' % NetworkBuilder.bridge)
            NetworkBuilder.bridge = None
            NetworkBuilder.targets = None
            NetworkBuilder.builds = None
            NetworkBuilder.ips = None
            NetworkBuilder.tapNames = None
            NetworkBuilder.consoles = None

    def __isBridgeExisted(self, bridge):
        _, output = runCmd(f'sudo brctl show {bridge}')
        # if 'can\'t get info No such device' in output:   # xiaozhan, debug, this return value is wrong
        if 'bridge qemuBridge does not exist!' in output:  # xiaozhan, debug, this return value is wrong
            log.debug('-------xiaozhan bridge needs to create======')  # xiaozhan debug
            return False
        else:
            return True


class OpenstackTarget(Target):
    def __init__(self, board, configYaml='default', log=None, timeout=180):
        if configYaml == 'default':
            self.configYaml = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           'ezConfigTargetOpenstackVMs.yaml')
        else:
            self.configYaml = configYaml
        checkPath(self.configYaml)

        self.cloudName = readYamlConfig(self.configYaml, 'cloud')['cloud_name']

        self.console = None
        self.log = log
        self.timeout = timeout

        self.board = board
        self.config = readYamlConfig(self.configYaml, key=self.board)
        self.serverName = self.config['name']
        self.image = None
        self.imageName = self.config['image']
        self.qemuPackageName = f'{self.imageName}.qcow2'
        self.flavor = self.config['flavor']
        self.ip = self.config['nics'][0]['ip']
        self.ipMask = self.config['nics'][0]['mask']
        self.device = self.config['nics'][0]['device']
        self.network = self.config['nics'][0]['network']

    def boot(self, image, hostIp=None, targetIp=None):
        logger.info(f'boot {self.board} with server name = {self.serverName}')
        self.image = image.getBin()
        checkPath(self.image)

        logger.info(f'\tcreating Qemu package {self.qemuPackageName} with image {self.image}')
        currentPath = os.getcwd()
        qemuPkg = createQemuPackage(currentPath, self.qemuPackageName, self.image, self.ip)
        logger.info(qemuPkg)

        clt = OpenstackClient(configYaml=self.configYaml)
        logger.info(f'\treplacing openstack image {self.imageName} with qemu package {qemuPkg}')
        clt.replaceImage(self.imageName, qemuPkg)

        logger.info(f'\treplacing openstack server {self.serverName} with')
        logger.info(f'\t\tflavor={self.flavor}')
        logger.info(f'\t\tnetwork={self.network}')
        logger.info(f'\t\tip={self.ip}')
        clt.replaceServer(self.serverName, self.imageName, self.flavor, self.network, fixIp=self.ip)

        # Openstack VM has no text-based console so that we use telnet to VM 
        # via virtio network as work around
        s = telnet(addr=self.ip, port=23, name=self.board, timeout=10)
        s.login()
        self.console = s
        return shell_ops(self.console)

    def ip(self):
        return self.ip

    def connect(self):
        if self.console is not None:
            return self.console

        s = telnet(addr=self.ip, port=23, name=self.board, timeout=10)
        s.login()
        self.console = s
        shops = shell_ops(self.console)
        return shops

    def disconnect(self):
        return self.cleanup()

    def cleanup(self):
        if self.console is not None:
            self.console.s.sendcontrol(']')
            self.console.s.expect('telnet> ')
            self.console.s.sendline('q')
            self.console.s.expect('Connection closed.')
            self.console = None
        return
