import os
import pexpect
import tempfile
import time
import re
import sys
import collections

sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.util import shCmd


def ping_from_vxworks(proxy, target_address, retries=3):
    for _ in range(1, retries):
        if ':' in target_address:
            lines = proxy.send_and_return_all('ping6 -c 1 ' + target_address)
        else:
            lines = proxy.send_and_return_all('ping -c 1 ' + target_address)
        # print('\n'.join(lines))
        for line in lines:
            if (('64 bytes from %s:' % target_address) in line or
                    ('%s bytes=64' % target_address) in line):
                return True
        time.sleep(0.5)
    return False


def ping_from_linux(proxy, target_address, retries=3):
    for _ in range(1, retries):
        if ':' in target_address:
            lines = proxy.send_and_return_all('ping -6 -c 1 ' + target_address)
        else:
            lines = proxy.send_and_return_all('ping -c 1 ' + target_address)
        # print('\n'.join(lines))
        for line in lines:
            if ' received, 0% packet loss,' in line:
                return True
            if ' received, 100% packet loss,' in line:
                return False
        time.sleep(0.5)
    return False


def ping_from_host(target_address, retries=3):
    for _ in range(1, retries):
        if ':' in target_address:
            lines = shCmd('ping6 -c 1 ' + target_address)
        else:
            lines = shCmd('ping -c 1 ' + target_address)
        for line in lines:
            if (('64 bytes from %s' % target_address) in line or
                    ('%s bytes=64' % target_address) in line):
                return True
        time.sleep(0.5)
    return False


def gmtime_str():
    return '%d%02d%02d_%02d.%02d.%02d' % time.gmtime()[:6]


def localtime_str():
    return '%d%02d%02d_%02d.%02d.%02d' % time.localtime()[:6]


def _eta_str(eta):
    if eta > 59:
        return '%sm %ss' % divmod(eta, 60)
    else:
        return '%ss' % eta


class ip_exception(Exception):
    def __init__(self, s):
        self.msg = s

    def __str__(self):
        return self.msg


class engine_error(ip_exception):
    "Raised when there's a bug in the test engine or your test app"
    pass


class test_fail(ip_exception):
    "Raised when the target stack fails a test case"
    pass


class configError(ip_exception):
    "Raised if the config setup is bad"
    pass


class native_error(ip_exception):
    "Raised if you try to do something towards a native host that isnt allowed"
    pass


class net_setup_error(ip_exception):
    "Raised if the network requirements arent fullfilled"
    pass


class internal_error(ip_exception):
    "Raised when there's a bug in the program, such as unexpected data"
    pass


class _dummy:
    def setlog(*_):
        pass


class _log(object):
    # !!! one global and one per object. make each instance call the class method to make the global/merged log
    def __init__(self, log, verbose):
        self.testname = ''
        self.logfile = log
        self.verbose = verbose
        self.context = ''
        self.logfile.write(
            'Begin log at GMT: (%s), Localtime: (%s)\n' % (time.asctime(time.gmtime()), time.asctime(time.localtime())))
        self.logfile.write('Following timestamps are GMT\n')
        self.starttime = None
        self.v6 = ''

    def __call__(self, msg, newline=True, echo=False, printtime=False, context=False):
        # Write msg to the logfile.
        # Default is to add a newline, not echo it to screen too, not prepend the output 
        # with a timestamp and not write the product.file.test context on each line.
        s = ''
        if printtime:
            s = gmtime_str() + ' '
        if context:
            s += self.context + ' - '
        s += msg
        self.logfile.write(s + '\n')
        if echo:
            if newline:
                print(s)
            else:
                print(s.ljust(75))  # print(s.ljust(75), end=' ')
                sys.stdout.flush()
        elif self.verbose:
            print(s)

    def write(self, s):
        self(s)

    def flush(self):
        self.logfile.flush()

    def start(self, test, quiet, v6, echo):
        newcontext = test.prodname + '.' + test.modname + '.' + test.testname
        if self.context != '':
            raise engine_error(
                'log.start: new test started without ending the last one. new=%s, old=%s' % (newcontext, self.context))
        self('')
        self('-' * 80)
        self('-' * 30 + ' Test starts ' + '-' * 37)
        self('-' * 80)
        self.context = newcontext
        if not test.doc:
            raise engine_error('\nYou forgot to document your test "%s"' % newcontext)
        timestr = "ETA: " + _eta_str(test.eta)
        self('\n' + ' ' * 4 + test.doc + '.', echo=not quiet)
        self('IPv' + ('4', '6')[int(bool(v6))] + " " + timestr, newline=False, echo=echo, context=True)
        self.v6 = v6
        self.starttime = time.time()

    def stop(self, success=True):
        if not self.starttime:
            return
        time_passed = int(time.time() - self.starttime)
        self('')
        if isinstance(success, list):
            self.__handle_test_results(success, time_passed)
        else:
            if isinstance(success, str) and success.startswith('skipped'):
                self(self.context + ' Test %s ' % success + '-' * 60)
            elif success:
                self(self.context + ' Test Passed ' + '-' * 40)
            else:
                self(self.context + ' Test Failed ' + '-' * 60)
            oldcontext = self.context
            self.context = ''
            if isinstance(success, str) and success.startswith('skipped'):
                self(success, newline=True, echo=True)
            elif isinstance(success, str) and success.startswith('restart'):
                self(success, newline=True, echo=True)
            elif success:
                self('OK ' + _eta_str(time_passed), newline=True, echo=True, printtime=False)
            else:
                if oldcontext:
                    self(oldcontext + ' test case failed', newline=True, echo=True)
                else:
                    self(oldcontext + ' failed', newline=True, echo=True)

        self('-' * 80)
        self('-' * 30 + ' Test ends ' + '-' * 39)
        self('-' * 80)

    def __handle_test_results(self, test_results, time_passed):
        # handle a list of test case results
        # assume each list element is (testName, testResult)
        test_duration = int(time_passed / len(test_results) + 0.5)
        timestr = "ETA: " + _eta_str(test_duration)
        for test_name, test_result in test_results:
            self('%s - IPv' % test_name + ('4', '6')[int(bool(self.v6))] + " " + timestr, newline=False, echo=True)
            if test_result.lower() == 'skip':
                self('skipped', newline=True, echo=True)
            elif test_result.lower() == 'pass':
                self('OK ' + _eta_str(test_duration), newline=True, echo=True, printtime=False)
            elif test_result.lower() == 'fail':
                self(' failed', newline=True, echo=True)
            else:
                raise internal_error('test case %s result %s not recognized' % (test_name, test_result))
        self.context = ''


def netmask_to_prefixlen(m):
    d = {255: 8, 0: 0, 128: 1, 128 + 64: 2, 128 + 64 + 32: 3, 128 + 64 + 32 + 16: 4, 128 + 64 + 32 + 16 + 8: 5,
         128 + 64 + 32 + 16 + 8 + 4: 6, 128 + 64 + 32 + 16 + 8 + 4 + 2: 7}
    return sum([d[int(x)] for x in m.split(".")])


def prefixlen_to_netmask(p, v6=''):
    "v6: ipv4 is default. needed to correctly make a netmask for ipv6"
    if v6:
        bitmax = 128
    else:
        bitmax = 32
    if p < 0 or p > bitmax:
        raise 'prefixlen_to_netmask: %s' % p

    def prefixlen_to_bin(p):
        return '1' * p + '0' * (bitmax - p)

    b = prefixlen_to_bin(p)
    if v6:
        s = []
        for x in range(0, 128, 4):
            s.append(b[x:x + 4])
    else:
        s = b[:8], b[8:16], b[16:24], b[24:]

    def bin_to_dec(b, nbits):
        r = 0
        for x in range(0, nbits):
            r += int(b[x]) << (nbits - 1 - x)
        return str(r)

    if v6:
        f = [int(bin_to_dec(x, 4)) for x in s]
        r = []
        for x in range(0, 32, 4):
            r.append('%X%X%X%X' % (f[x], f[x + 1], f[x + 2], f[x + 3]))
    else:
        r = [bin_to_dec(x, 8) for x in s]

    if v6:
        return ':'.join(r)

    else:
        return '.'.join(r)


def IF(boolean, true, false):
    'beware: no short circuiting'
    if boolean:
        return true
    return false


class ip(object):
    def __init__(self, addr, netmask_or_prefixlen=None):
        '''
        Make an "ip" object out of a string representation / other ip object / target (primary ip)
        Running str(myip) will return "ip/prefixlen"
        addr = "a.b.c.d[/e]" "a:b[/e]"
        Objects of type ip act immutable.

        variables publically available:
        .addr
        the string representation of the host id part of the address

        .prefixlen
        returns 1 to 32 for ipv4-addresses and possibly more for v6!

        .v6
        if the address is v6 or not
        '''

        if hasattr(addr, 'ip') and isinstance(addr.ip, collections.Callable):
            # it's actually a host
            addr = addr.ip()

        if isinstance(addr, ip):
            self._addr = addr._addr
            self.prefixlen = addr.prefixlen
            self.v6 = addr.v6
            self.scope = addr.scope
            self._addrstr = addr._addrstr
            return

        if addr == 'localhost':  # v6?
            addr = '127.0.0.1'

        pfx = None
        if netmask_or_prefixlen != None:
            if '.' in netmask_or_prefixlen:
                pfx = netmask_to_prefixlen(netmask_or_prefixlen)
            else:
                pfx = int(netmask_or_prefixlen)

        if ':' in addr:
            self.v6 = '6'
        else:
            self.v6 = ''

        if '/' in addr:
            d = addr.split('/')
            addr = d[0]
            self.prefixlen = int(d[1])
        elif pfx != None:
            self.prefixlen = int(pfx)
        else:
            self.prefixlen = IF(self.v6, 128, 32)

        if '%' in addr:
            addr, self.scope = addr.split('%')
        else:
            self.scope = None

        self._addr = addr.lower()

        if self.v6 and '.' in self._addr:
            middle = self._addr.rfind(':')
            firsthalf = self._addr[:middle]
            ls = self._addr[middle + 1:].split('.')
            ls = hex(int(ls[0]) * 256 + int(ls[1]))[2:] + ":" + hex(int(ls[2]) * 256 + int(ls[3]))[2:]
            self._addr = firsthalf + ":" + ls

        import socket
        family = IF(self.v6, socket.AF_INET6, socket.AF_INET)
        self._addrstr = socket.inet_ntop(family, socket.inet_pton(family, self._addr))

        def _tolist(s):
            if self.v6:
                if s == '::':
                    return [0] * 8
                ls = s.split(':')
                if '::' not in s:
                    return [int(x, 16) for x in ls]
                if s.startswith('::'):
                    ls = ls[1:]
                elif s.endswith('::'):
                    ls = ls[:-1]
                n = len(ls) - 1
                pos = ls.index('')
                ls = ls[:pos] + ["0"] * (8 - n) + ls[pos + 1:]
                return [int(x, 16) for x in ls]
            else:  # v4
                ls = s.split('.')
                return [int(x) for x in ls]

        self._addr = _tolist(self._addr)

        def _get(self):
            if self.v6:
                a = ':'.join([hex(x)[2:] for x in self._addr])
                family = IF(self.v6, socket.AF_INET6, socket.AF_INET)
                a = socket.inet_ntop(family, socket.inet_pton(family, a))
                if self.scope:
                    a += '%' + self.scope
                return a
            else:
                return '.'.join([str(x) for x in self._addr])

        ip.addr = property(_get)

    def mask(self, netmask_or_prefixlen):
        """
        Return a new ip object masked with the netmask.
        Netmask is passed as string and prefixlen as int.
        """

        def nm4str_to_nm(n):
            return [int(x) for x in n.split('.')]

        if isinstance(netmask_or_prefixlen, str):
            nm = nm4str_to_nm(netmask_or_prefixlen)
            pfx = netmask_to_prefixlen(netmask_or_prefixlen)
        elif not self.v6:
            nm = nm4str_to_nm(prefixlen_to_netmask(netmask_or_prefixlen))
            pfx = netmask_or_prefixlen
        else:  # prefixlen v6
            p = pfx = netmask_or_prefixlen
            nm = []
            while p > 0:
                nm.append((0xffff << (16 - min(p, 16))) & 0xffff)
                p -= 16
            nm = nm + [0] * (8 - len(nm))

        r = ip(self)
        r._addr = [a & b for a, b in zip(self._addr, nm)]
        r.prefixlen = pfx
        return r

    def broadcast(self, netmask_or_prefixlen):
        # !!! copy of mask() above. merge!
        def nm4str_to_nm(n):
            return [int(x) for x in n.split('.')]

        if isinstance(netmask_or_prefixlen, str):
            nm = nm4str_to_nm(netmask_or_prefixlen)
            pfx = netmask_to_prefixlen(netmask_or_prefixlen)
        elif not self.v6:
            nm = nm4str_to_nm(prefixlen_to_netmask(netmask_or_prefixlen))
            pfx = netmask_or_prefixlen
        else:  # prefixlen v6
            p = pfx = netmask_or_prefixlen
            nm = []
            while p > 0:
                nm.append((0xffff << (16 - min(p, 16))) & 0xffff)
                p -= 16
            nm = nm + [0] * (8 - len(nm))

        r = ip(self)
        r._addr = [a | (~b & 0xff) for a, b in zip(self._addr, nm)]
        r.prefixlen = pfx
        return r

    def __str__(self):
        return "%s/%s" % (self.addr, self.prefixlen)

    __repr__ = __str__

    def __cmp__(self, other):
        if isinstance(other, ip):
            return cmp(self.addr, other.addr)
        return False

    def __eq__(self, other):
        """
        ==  see if ips are the same (no matter previous ipv6 representation)
        Does not take the netmask into account
        """
        if isinstance(other, ip):
            return self.addr == other.addr
        elif other == None:
            return False
        else:
            return self.addr == other.split('/')[0]

    def __ne__(self, other):
        "not =="
        return not (self == other)

    def __hash__(self):
        return hash(self._addrstr)

    def is_multicast(self):
        "decide if addr is a multicast address"
        if self.addr.find('ff') == 0:
            return True
        for net in range(224, 239):
            if self.addr.find(str(net) + '.') == 0:
                return True
        return False

    def get_network(self):
        "Returns the network part of the address"
        return self.mask(self.prefixlen)

    def get_raw_addr(self):
        return self._addr

    def get_addr_str(self):
        return '.'.join([str(x) for x in self._addr])

    def get_networkid_str(self):
        return ('%s' % self.get_network()).replace('.0/', '.1/')


"""    
    s_args = {'log':self.log,
              'logverbose':self.logverbose,
              'addr':login_ip,
              'port':port,
              'user':user,
              'passwd':passwd,
              'name':target_name,
              'native' : native,
              'dry':self.opt['dry'],
              'target_access' : target_access,
              'target_prefix' : target_prefix,
              'timeout' : self.opt['timeout'] }
"""


class session(object):
    def __init__(self, log=None, logverbose=None, addr=None, port=None, user=None, passwd=None, name=None, native=False,
                 dry=None, relogin=False, target_access='', target_prefix=None, timeout=30):  # interactive=False
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
        self.prompt = name + '_' + self.prompt_magic
        self.old_prompt = None
        self.bailmsg = '%s\nYou probably forgot to start the target: %s at %s:%s\n%s' % (
            'x' * 79, name, addr, port, 'x' * 80)
        self.sudo = '%s'

    def set_old_prompt(self, prompt):
        self.old_prompt = prompt

    # pexpect session is stored in self.s between __init__ and second_init
    def second_init(self, timeout=30):
        self.s.timeout = timeout

    def login(self):
        for t in range(3):
            try:
                self._login()
            except configError:
                pass
                # print "try %s" % t
            else:
                break
        else:
            self.log("Couldn't login to %s at %s://%s%s@%s:%s" % (
                self.name, self.type, self.user, IF(self.passwd is None, "", ':%s' % self.passwd), self.login_ip.addr,
                self.port), echo=True)
            raise configError("4" + self.bailmsg)

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


class telnet(session):
    """operates on an iptarget"""

    def _login(self):
        self.type = 'telnet'
        self.shelltype = 'dontknow'
        # print 'Logging in to %s:%s using telnet' % (self.login_ip.addr, self.port)
        s = _dummy()
        timeout = None
        for tries in range(3):
            try:
                if not self.dry:
                    tcmd = "%s%s %s %d" % (self.target_access, self.type, self.login_ip.addr, self.port)
                    # print('== telnet cmd:%s, prompt:%s' % (tcmd, self.prompt))
                    s = pexpect.spawn(tcmd, timeout=20)
                    # Linux is needs some time to turn  TTY echo off during login
                    # so we should not set delaybeforesend to 0 yet.
                    # s.delaybeforesend = 0
                    telnet_timeout = False

                expect_array = [r'Welcome to (\w+)[!|\s]',  # 0
                                'assword: ',  # 1
                                'ogin: ',  # 2
                                'vxWorks',  # 3
                                '-> ',  # 4
                                'BusyBox ',  # 5
                                'sh-',  # 6
                                '# ',  # 7
                                'RTNET> ',  # 8
                                ]

                for _ in range(4):
                    try:
                        i = s.expect(expect_array, timeout=10)
                        # print('== return i=%s' % i)

                        if i == 5 or i == 6 or i == 7:  # 'BusyBox ', 'sh-', '# ',
                            # BusyBox
                            s.sendline('export PS1="%s"' % self.prompt)
                            # Need to expect twice to get in sync with prompt.
                            s.expect(self.prompt)
                            s.expect(self.prompt)

                            s.sendline('echo prOmpt_sYnc')
                            s.expect('prOmpt_sYnc')
                            s.expect(self.prompt)
                            self.shelltype = 'linux'
                            break
                        if i == 4:  # '-> ',
                            if not self.dry:
                                s.sendline('cmd')
                        if i == 3:  # 'vxWorks',
                            # vxworks native shell.
                            if not self.dry:
                                s.sendline('set prompt ' + self.prompt)
                                s.expect(re.escape(self.prompt))
                                s.expect(re.escape(self.prompt))
                                s.sendline('unalias ifconfig')
                                s.expect(re.escape(self.prompt))
                                s.sendline('unalias netstat')
                                s.expect(re.escape(self.prompt))
                                s.sendline('unalias route')
                                s.expect(re.escape(self.prompt))
                                s.sendline('cd /ram')
                                s.expect(re.escape(self.prompt))
                                self.old_prompt = '"[vxWorks *]# "'
                            self.shelltype = 'vxworks'
                            break
                        if i == 2:  # 'ogin: ',
                            if not self.user:
                                raise configError(
                                    '%s\nA user was required but none configured for target: %s at %s:%s\n%s' % (
                                        'x' * 79, self.name, self.addr, self.port, 'x' * 80))
                            s.sendline(self.user)
                        if i == 1:  # 'assword: ',
                            if not self.passwd:
                                raise configError(
                                    '%s\nA password was required but none configured for target: %s at %s:%s\n%s' % (
                                        'x' * 79, self.name, self.addr, self.port, 'x' * 80))
                            s.sendline(self.passwd)  # password correct?

                            expect_array.append('@')

                        if i == 8 or i == 9:
                            if telnet_timeout:
                                # RTNet
                                self.prompt = 'RTNET> '
                                self.shelltype = 'rtnet'
                                break
                            else:
                                if not self.dry:
                                    self.prompt = self.prompt.split('_')[0] + '_' + self.login_ip.addr + '_' + \
                                                  self.prompt.split('_')[1]
                                    s.sendline('export PS1="%s"' % self.prompt)
                                    s.expect(re.escape(self.prompt))
                                    s.expect(re.escape(self.prompt))
                                    # The UML's are a bit slow at times.
                                    timeout = 40

                                if self.user != 'root':
                                    self.sudo = 'sudo %s'
                                self.shelltype = 'linux'
                                break

                        if i == 0:  # r'Welcome to (\w+)[!|\s]',
                            r = s.match.group(1)
                            if r == 'OSE':  # nowhere near support for OSE yet
                                self.shelltype = 'ose'
                                self.prompt = '$'

                            if r == 'FreeBSD':
                                self.shelltype = 'freebsd'
                            if r == 'uNAP':
                                self.prompt = '#>1'
                            if r == 'IPCOM':
                                self.shelltype = 'ipcom'

                            if not self.dry and not self.relogin and r != 'OSE' and r != 'Ubuntu':
                                self.shelltype = 'ipcom'
                                s.sendline('prompt ' + self.prompt)
                                i = s.expect(['ok', pexpect.TIMEOUT])
                                if i == 1:
                                    self.log(self.bailmsg, newline=True, echo=True)
                                    sys.stdout.flush()
                                    raise configError("3" + self.bailmsg)
                            s.expect(re.escape(self.prompt))
                            break
                    except pexpect.TIMEOUT:
                        s.send('\r')
                        telnet_timeout = True
                else:
                    # we failed to parse the login prompt
                    raise configError('%s\nFailed to login using telnet: %s at %s:%s\n%s' % (
                        'x' * 79, self.name, self.addr, self.port, 'x' * 80))

                # successful login
                break
            except configError as inst:
                raise
            except:
                import time
                time.sleep(1)
        else:
            self.log("Failed to establish telnet connection to %s" % (self.login_ip.addr))
            raise configError(self.bailmsg)

        s.delaybeforesend = 0

        if not timeout:
            timeout = self.timeout
        self.s = s
        self.second_init(timeout=timeout)

    def logout(self):
        if self.shelltype == 'rtnet':
            self.s.sendcontrol(']')
            self.s.expect('telnet> ')
            self.s.sendline('q')
            self.s.expect('Connection closed.')
        else:
            if self.old_prompt is not None and self.shelltype == 'vxworks':
                # print('== set prompt to old value:|%s|' % self.old_prompt)
                self.s.sendline('set prompt ' + self.old_prompt)
                self.s.expect(re.escape(self.old_prompt))
            self.s.sendcontrol(']')
            self.s.expect('telnet> ')
            self.s.sendline('q')
            self.s.expect('Connection closed.')

    def send(self, cmd, newline, sudo=True, *a, **k):
        if not sudo:
            cmd2 = cmd
        else:
            cmd2 = self.sudo % cmd
        session.send(self, cmd2, newline, sudo)
        return cmd2


# bash on linux
class ssh(session):
    '''operates on a baselinux
    Expects passwordless sudo unless logged in as root.'''

    def _login(self):
        self.type = 'ssh'
        self.shelltype = 'linux'
        # log('Logging in to %s:%s using ssh' % (addr, port))
        s = _dummy()
        if not self.dry:
            try:
                cmd = 'ssh '
                cmd += '-x -p %s -l %s %s' % (self.port, self.user, self.login_ip.addr)
                # print(cmd)
                s = pexpect.spawn(cmd)
                # Linux is needs some time to turn  TTY echo off during login
                # so we should not set delaybeforesend to 0 yet.
                s.delaybeforesend = 1  # rime

            except pexpect.TIMEOUT:
                raise configError(self.bailmsg)

            oldprompt = r'.*?\~[\$\#]'
            for _ in range(2):
                i = s.expect([oldprompt,
                              'assword: ',
                              r'Are you sure you want to continue connecting \(yes/no\)\? ',
                              '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'])  # Offending key in .ssh/known_hosts
                # print('i=%s' % i)
                if i == 3:
                    s.expect("Host key verification failed")
                    # s.expect("(Offending key in .*)\r\n")
                    raise configError(s.before)
                if i == 2:
                    s.sendline('yes')
                if i == 1:
                    if not self.passwd:
                        raise configError(
                            '%s\nA password was required but none configured for target: %s at %s:%s\n%s' % (
                                'x' * 79, self.name, self.addr, self.port, 'x' * 80))
                    s.sendline(self.passwd)  # password correct?
                    s.expect(oldprompt)
                    break
                if i == 0:
                    break

        if not self.dry:
            s.sendline('export PS1=%s' % self.prompt)
            s.expect(re.escape(self.prompt))
            s.expect(re.escape(self.prompt))

        if self.user != 'root':
            self.sudo = 'sudo %s'

        s.delaybeforesend = 0

        self.s = s
        self.second_init()

    def logout(self):
        if not self.dry:
            self.s.sendline('exit')  # don't use sudo here
            self.s.expect(pexpect.EOF)
            # self.s.wait()
            # self.s.expect_exact(r'Connection to \w+ closed')

    def send(self, cmd, newline, sudo=True, *a, **k):
        if not sudo:
            cmd2 = cmd
        else:
            cmd2 = self.sudo % cmd
        session.send(self, cmd2, newline, sudo)
        return cmd2


class shell_ops(object):
    def __init__(self, session):
        self.s = session
        self.rmdir_cmd = 'rmdir '
        if self.s.shelltype == 'vxworks':
            self.rmdir_cmd = 'file remove '

    # core functions using the session's pexpect spawn
    def send(self, cmd, newline=True, sudo=True):
        '''just send with newline, this should be followed with waiting for the prompt
        (calls pexpect)'''
        # print '--- send   %s %s %s' % (time.time(), threading.current_thread(), cmd)
        self.s.send(cmd, newline, sudo)

        return cmd

    def expect(self, cmd, timeout=-1):
        """Dont use this directly, use expect_re or expect_exact
        (calls pexpect)"""

        def log_command_output():
            if self.s.log is not None:
                self.s.log('\n' + self.s.name + '>' + (str(self.s.s.before) + str(self.s.s.after)).replace('\r', ''))
                # self.s.log.flush()

        prompt = re.escape(self.s.prompt)
        if (isinstance(cmd, list) and prompt in cmd) or cmd == prompt:
            # Receive the prompt from the target is one of the acceptable outcomes
            i = self.s.s.expect(cmd, timeout)
            # print '--- expect before:%s' % self.s.s.before
            # print '--- expect after :%s' % self.s.s.after
            # print '\n\n'
            log_command_output()
            return i

        # else: receiving the prompt without seeing any of the specified outcomes
        # is an error condition and will result in a failed test case
        if isinstance(cmd, list):
            ls = [prompt] + cmd
        else:
            ls = [prompt, cmd]

        i = self.s.s.expect(ls, timeout)
        # print '--- expect before:%s' % self.s.s.before
        # print '--- expect after :%s' % self.s.s.after
        # print '\n\n'
        log_command_output()

        if i == 0:
            s = '''\ntarget: "%s" got prompt instead of expected "%s".
            Command run and what was returned:
            "%s"''' % (self.s.name, cmd, self.s.s.before.decode().replace('\r', ''))
            # self.s.log(s)
            raise test_fail(s)
        return i - 1

    # fluff (i.e. helper functions previously expanded in test cases)
    def send_and_wait_prompt(self, s):
        "Discard result"
        self.send(s)
        self.wait_prompt()

    def expect_re(self, cmd, timeout=-1):
        """
        Parse incoming stream with Regular Expressions, leave rest of instream untouched.
        Only eats prompts on failure.
        timeout = -1 will use self.s.s.timeout
        """
        return self.expect(cmd, timeout)

    def expect_exact(self, cmd, timeout=-1):
        """just like expect_re() but uses plain text instead of a regular expression"""
        if isinstance(cmd, list):
            ecmd = [re.escape(t) for t in cmd]
        else:
            ecmd = [re.escape(cmd)]
        return self.expect(ecmd, timeout)

    def expect_re_and_wait_prompt(self, *a, **k):
        'like expect_re() but waits for prompt after the matching was successful'
        r = self.expect_re(*a, **k)
        self.wait_prompt()
        return r

    def expect_exact_and_wait_prompt(self, *a, **k):
        'like expect_exact() but waits for prompt after the matching was successful'
        r = self.expect_exact(*a, **k)
        self.wait_prompt()
        return r

    def expect_get(self, cmd, timeout=-1, eat_prompt=True):
        '''
        The matches in cmd within () are returned as one result or a list of results
        example expect_get("RX packets:([0-9]+) errors:([0-9]+) dropped:([0-9]+)[^0-9]")
        will return the value [123, 456, 789]. If only one value is wanted (one '()'),
        the value is returned alone (not a list with only one member).
        Wait for prompt is done after match if eat_prompt.
        If this fails, it will have eaten the prompt.
        When nothing is matched, raises test_fail.
        When a list of alternatives are given as "cmd", (index,value(s)) is returned,
        otherwise just value(s).
        Values are either a value or a list of values if many "()" are present in the RE.
        (uses pexpect)
        '''
        if isinstance(cmd, list):
            i = self.expect_re([re.escape(self.s.prompt)] + cmd, timeout)
        else:
            i = self.expect_re([re.escape(self.s.prompt), cmd], timeout)
        if i == 0:
            # prompt gone
            raise test_fail('prompt reached instead of \n"%s"\nstuff after: "%s"' % (cmd, self.s.s.before))

        i = i - 1  # same numbering as before insertion of prompt
        matches = self.s.s.match  # save this before running wait_prompt which removes it
        if eat_prompt:
            self.wait_prompt()

        if matches:
            matches = matches.groups()
            if len(matches) == 1:
                matches = matches[0]

        if isinstance(cmd, list):
            return i, matches
        else:
            return matches

    def wait_prompt(self, timeout=-1, cleanup=False):
        '''
        All input is read and discarded up till the NEXT prompt.
        If there is still text in the output stream after this, you have probably forgotten
        to "sync" with the prompt after previous commands and will have a terrible time finding
        out whats gone wrong.
        "cleanup" is only used if you need to perform cleanup of something not cleaned up by
        the test engine.
        (This is how the original tcl expect_prompt works.)
        '''
        try:
            # print('shops.prompt=%s' % self.s.prompt)
            self.expect_exact(self.s.prompt, timeout)
        except pexpect.TIMEOUT:
            if not cleanup:
                self.s.log('%s never returned the prompt (%s)' % (self.s.name, self.s.s.before))
                raise
        # try: # not a good fix!
        #    self.expect_exact(self.s.prompt, timeout=2)
        # except pexpect.TIMEOUT:
        #    pass

    def expect_prompt(self, cmd0, timeout=-1, cleanup=False):
        '''
        Run "cmd" and expect the prompt immediately.
        If anything preceeds the prompt, an exception will be raised.
        The result of cmd must be silent or this will fail.
        Use timeout to change from default of 10 seconds.
        '''
        if cleanup:
            self.send(cmd0)
            self.wait_prompt()
            return

        all = self.send_and_return_all(cmd0)
        if all != []:
            raise test_fail('expect_prompt: %s wanted nothing. got: "%s".' % (self.s.name, all))

    def wait_prompt_not(self, bad, timeout=-1):
        """
        The 'bad' RE(s) may not appear before the prompt appears,
        anything else is ok
        'bad' may be one RE or a list of REs.
        (uses pexpect)
        """
        ls = [re.escape(self.s.prompt), bad]
        if isinstance(bad, list):
            ls = [re.escape(self.s.prompt)] + bad
        i = self.expect_re(ls, timeout)
        if i != 0:
            self.wait_prompt()
            self.s.log("got    : " + str(ls[i]) + re.sub(r'[\r\n\ ]', '', self.s.s.before), True)
            self.s.log("wanted just a prompt. ", True)
            raise test_fail('wait_prompt_not: %s got unexpected: "%s"' % (self.s.name, ls[i]))

    def expect_not(self, bad, timeout=1):
        """Waits for a second and returns happily unless "bad" arrives.
        The prompt must not show up."""
        ls = [pexpect.TIMEOUT, bad]
        if isinstance(bad, list):
            ls = [pexpect.TIMEOUT] + bad
        i = self.expect_re(ls, timeout)
        if i != 0:
            raise test_fail('expect_not: %s got unexpected "%s"' % (self.s.name, ls[i]))

    def send_and_return_all(self, cmd, newline=True, strip_lines=True, wait_timeout=-1, custom_prompt=None):
        """
        "cmd" is sent to the shell with a "newline" appended.
        A list of lines is returned as result. All lines are stripped
        of leading/ending whitespace if "strip_lines".
        (uses pexpect)
        """
        cmd = cmd.strip()
        self.send(cmd, newline)

        if custom_prompt:
            # Change to custom prompt
            original_prompt = self.s.prompt
            self.s.prompt = custom_prompt

        self.wait_prompt(timeout=wait_timeout)

        if custom_prompt:
            # Restore original prompt
            self.s.prompt = original_prompt

        all = self.s.s.before.decode("utf-8")
        # Remove control codes, see http://dickey.his.com/xterm/xterm.faq.html
        all = all.replace('\r\n\r\x00', '')
        all = all.replace(' \x08', '')
        all = all.replace('^[[A', '')
        all = all.replace('^[[K', '')
        lines = all.split('\r\n')

        # Remove the echo of the executed command
        lines = lines[1:]
        if len(lines) == 0:
            return []

        non_empty_lines = []

        # strip leading / trailing whitespace
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

    def send_and_return_all_by_timeout(self, cmd, cmd_timeout=30, strip_lines=True):
        """
        "cmd" is sent to the shell with a "newline" appended.
        A list of lines is returned as result after cmd_timeout seconds.
        All lines are not stripped.
        This funtion is used for the command without any returned prompt/flag, like "route monitor"
        """
        if pexpect.__version__ < '4.2.1':
            raise configError(
                'pexpect 4.2.1 and above are only supported. Your pexpect version is %s' % pexpect.__version__)
        # each call to this function uses the different temporary file
        _, logfile = tempfile.mkstemp()
        magic_start = 'start_magic_magic_start'
        magic_stop = 'stop_magic_magic_stop'

        # save pexpect config
        old_timeout = self.s.s.timeout
        old_logfile = self.s.s.logfile

        self.s.s.timeout = cmd_timeout + 10

        with open(logfile, 'wb') as fdw:
            self.s.s.logfile = fdw

            self.s.s.send('echo ' + magic_start + '\n')
            self.s.s.expect(magic_start)

            self.s.s.send(cmd + '\n')
            time.sleep(cmd_timeout)

            self.s.s.send('echo ' + magic_stop + '\n')
            self.s.s.expect(magic_stop)

        # restore pexpect config
        self.s.s.timeout = old_timeout
        self.s.s.logfile = old_logfile

        with open(logfile, 'rb') as fdr:
            content = fdr.read().decode('utf-8')

        shCmd('rm -f %s' % logfile)

        # different version pexpects return slightly different results
        ptn = r'(?s)%s\s*(.*?)%s' % (self.s.prompt + cmd, self.s.prompt + 'echo ' + magic_stop)
        found = re.search(ptn, content)
        if found is not None:
            content = found.groups()[0].replace(magic_start, '').replace('echo ', '').strip()
            if strip_lines:
                return [line.strip() for line in content.split('\n')]
            else:
                return [line for line in content.split('\n')]
        else:
            return []

    def return_all(self, strip_lines=True, wait_timeout=-1):
        """
        A list of lines is returned as result. All lines are stripped
        of leading/ending whitespace if "strip_lines".
        (uses pexpect)
        """
        self.wait_prompt(timeout=wait_timeout)
        all = self.s.s.before
        # Remove control codes, see http://dickey.his.com/xterm/xterm.faq.html
        all = all.replace('\r\n\r\x00', '')
        all = all.replace(' \x08', '')
        all = all.replace('^[[A', '')
        all = all.replace('^[[K', '')
        lines = all.split('\r\n')

        # Remove the echo of the executed command
        lines = lines[1:]
        if len(lines) == 0:
            return []

        non_empty_lines = []

        # strip leading / trailing whitespace
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

    def send_ctrl_c(self):
        # send CTRL+C and wait for promt
        print('shell_ops : send Ctrl+C')
        self.s.s.send('\003')  # send ctrl+c to target
        self.s.s.expect(self.s.prompt)


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
            target.wait_prompt(1)  # not possible
        except:  # pexpect.TIMEOUT:
            pass


default_s_args = {'log': None,
                  'logverbose': None,
                  'addr': None,
                  'port': None,
                  'user': None,
                  'passwd': None,
                  'name': None,
                  'native': False,
                  'dry': None,
                  'target_access': '',
                  'target_prefix': None,
                  'timeout': 30,
                  }


class proxy(object):
    def __init__(self, session_type_name, s_args):
        assert session_type_name in ('telnet', 'ssh',)
        session_class = globals()[session_type_name]
        full_s_args = self.__create_args(s_args)
        s = session_class(**full_s_args)
        # if prompt is not None:
        #    s.old_prompt = prompt
        s.login()
        self.s = s
        shops = shell_ops(s)
        self.shops = shops

    def __create_args(self, s_args):
        ret_s_args = default_s_args
        for k in s_args:
            if k in ret_s_args:
                ret_s_args[k] = s_args[k]
        return ret_s_args

    def __getattr__(self, x):
        if hasattr(self.shops, x):
            return getattr(self.shops, x)  # hit step in pdb
        return getattr(self.tops, x)  # hit step in pdb

    def logout(self):
        self.shops.s.logout()


class ShellOperations(object):
    def __init__(self, expectChild, prompt='-> ', name='', log=None):
        self.s = expectChild
        self.prompt = prompt
        self.log = log
        self.name = name

    def send(self, cmd, newline=True):
        '''just send with newline, this should be followed with waiting for the prompt
        (calls pexpect)'''
        if newline:
            self.s.sendline(cmd)
        else:
            self.s.send(cmd)
        return cmd

    def expect(self, cmd, timeout=-1):
        '''Dont use this directly, use expect_re or expect_exact
        (calls pexpect)'''

        def log_command_output():
            if self.log is not None:
                self.log('\n' + self.name + '>' + (str(self.s.before) + str(self.s.after)).replace('\r', ''))
                # self.log.flush()

        prompt = re.escape(self.prompt)
        if (isinstance(cmd, list) and prompt in cmd) or cmd == prompt:
            # Receive the prompt from the target is one of the acceptable outcomes
            i = self.s.expect(cmd, timeout)
            # print('--- expect before:%s' % self.s.s.before)
            # print('--- expect after :%s' % self.s.s.after)
            # print('\n\n')
            log_command_output()
            return i

        # else: receiving the prompt without seeing any of the specified outcomes
        # is an error condition and will result in a failed test case
        if isinstance(cmd, list):
            ls = [prompt] + cmd
        else:
            ls = [prompt, cmd]

        i = self.s.expect(ls, timeout)
        # print('--- expect before:%s' % self.s.s.before)
        # print('--- expect after :%s' % self.s.s.after)
        # print('\n\n')
        log_command_output()

        if i == 0:
            s = '''\ntarget: "%s" got prompt instead of expected "%s".
            Command run and what was returned:
            "%s"''' % (self.name, cmd, self.s.before.decode("utf-8").replace('\r', ''))
            if self.log is not None:
                self.log(s)
            raise test_fail(s)
        return i - 1

    def expect_re(self, cmd, timeout=-1):
        """
        Parse incoming stream with Regular Expressions, leave rest of instream untouched.
        Only eats prompts on failure.
        timeout = -1 will use self.s.s.timeout
        """
        return self.expect(cmd, timeout)

    def expect_exact(self, cmd, timeout=-1):
        """just like expect_re() but uses plain text instead of a regular expression"""
        if isinstance(cmd, list):
            ecmd = [re.escape(t) for t in cmd]
        else:
            ecmd = [re.escape(cmd)]
        return self.expect(ecmd, timeout)

    def expect_re_and_wait_prompt(self, *a, **k):
        """like expect_re() but waits for prompt after the matching was successful"""
        r = self.expect_re(*a, **k)
        self.wait_prompt()
        return r

    def expect_exact_and_wait_prompt(self, *a, **k):
        """like expect_exact() but waits for prompt after the matching was successful"""
        r = self.expect_exact(*a, **k)
        self.wait_prompt()
        return r

    def expect_get(self, cmd, timeout=-1, eat_prompt=True):
        """
        The matches in cmd within () are returned as one result or a list of results
        example expect_get("RX packets:([0-9]+) errors:([0-9]+) dropped:([0-9]+)[^0-9]")
        will return the value [123, 456, 789]. If only one value is wanted (one '()'),
        the value is returned alone (not a list with only one member).
        Wait for prompt is done after match if eat_prompt.
        If this fails, it will have eaten the prompt.
        When nothing is matched, raises test_fail.
        When a list of alternatives are given as "cmd", (index,value(s)) is returned,
        otherwise just value(s).
        Values are either a value or a list of values if many "()" are present in the RE.
        (uses pexpect)
        """
        if isinstance(cmd, list):
            i = self.expect_re([re.escape(self.prompt)] + cmd, timeout)
        else:
            i = self.expect_re([re.escape(self.prompt), cmd], timeout)
        if i == 0:
            # prompt gone
            raise test_fail('prompt reached instead of \n"%s"\nstuff after: "%s"' % (cmd, self.s.s.before))

        i = i - 1  # same numbering as before insertion of prompt
        matches = self.s.match  # save this before running wait_prompt which removes it
        if eat_prompt:
            self.wait_prompt()

        if matches:
            matches = matches.groups()
            if len(matches) == 1:
                matches = matches[0]

        if isinstance(cmd, list):
            return i, matches
        else:
            return matches

    def wait_prompt(self, timeout=-1, cleanup=False):
        """
        All input is read and discarded up till the NEXT prompt.
        If there is still text in the output stream after this, you have probably forgotten
        to "sync" with the prompt after previous commands and will have a terrible time finding
        out whats gone wrong.
        "cleanup" is only used if you need to perform cleanup of something not cleaned up by
        the test engine.
        (This is how the original tcl expect_prompt works.)
        """
        try:
            self.expect_exact(self.prompt, timeout)
        except pexpect.TIMEOUT:
            if not cleanup:
                if self.log is not None:
                    self.log('%s never returned the prompt (%s)' % (self.name, self.s.before))
                raise
        # try: # not a good fix!
        #    self.expect_exact(self.prompt, timeout=2)
        # except pexpect.TIMEOUT:
        #    pass

    def expect_prompt(self, cmd, timeout=-1, cleanup=False):
        """
        Run "cmd" and expect the prompt immediately.
        If anything preceeds the prompt, an exception will be raised.
        The result of cmd must be silent or this will fail.
        Use timeout to change from default of 10 seconds.
        """
        if cleanup:
            self.send(cmd)
            self.wait_prompt()
            return

        ret = self.send_and_return_all(cmd)
        if len(ret) >= 1:
            raise test_fail('expect_prompt: %s wanted nothing. got: "%s".' % (self.name, ret))

    def wait_prompt_not(self, bad, timeout=-1):
        """
        The 'bad' RE(s) may not appear before the prompt appears,
        anything else is ok
        'bad' may be one RE or a list of REs.
        (uses pexpect)
        """
        ls = [re.escape(self.prompt), bad]
        if isinstance(bad, list):
            ls = [re.escape(self.prompt)] + bad
        i = self.expect_re(ls, timeout)
        if i != 0:
            self.wait_prompt()
            if self.log is not None:
                self.log("got    : " + str(ls[i]) + re.sub(r'[\r\n\ ]', '', self.s.before), True)
                self.log("wanted just a prompt. ", True)
            raise test_fail('wait_prompt_not: %s got unexpected: "%s"' % (self.name, ls[i]))

    def expect_not(self, bad, timeout=1):
        """Waits for a second and returns happily unless "bad" arrives.
        The prompt must not show up."""
        ls = [pexpect.TIMEOUT, bad]
        if isinstance(bad, list):
            ls = [pexpect.TIMEOUT] + bad
        i = self.expect_re(ls, timeout)
        if i != 0:
            raise test_fail('expect_not: %s got unexpected "%s"' % (self.name, ls[i]))

    # fluff (i.e. helper functions previously expanded in test cases)
    def send_and_wait_prompt(self, cmd):
        """Discard result"""
        self.send(cmd)
        self.wait_prompt()

    def send_and_return_all(self, cmd, newline=True, strip_lines=True, wait_timeout=-1, custom_prompt=None):
        """
        "cmd" is sent to the shell with a "newline" appended.
        A list of lines is returned as result. All lines are stripped
        of leading/ending whitespace if "strip_lines".
        (uses pexpect)
        """
        cmd = cmd.strip()
        self.send(cmd, newline)

        if custom_prompt:
            # Change to custom prompt
            original_prompt = self.prompt
            self.prompt = custom_prompt

        self.wait_prompt(timeout=wait_timeout)

        if custom_prompt:
            # Restore original prompt
            self.prompt = original_prompt

        ret = self.s.before.decode("utf-8")
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

    def send_and_return_all_by_timeout(self, cmd, cmd_timeout=30, strip_lines=True):
        """
        "cmd" is sent to the shell with a "newline" appended.
        A list of lines is returned as result after cmd_timeout seconds.
        All lines are not stripped.
        This funtion is used for the command without any returned prompt/flag, like "route monitor"
        """
        if pexpect.__version__ < '4.2.1':
            raise configError(
                'pexpect 4.2.1 and above are only supported. Your pexpect version is %s' % pexpect.__version__)
        # each call to this function uses the different temporary file
        _, logfile = tempfile.mkstemp()
        magic_start = 'start_magic_magic_start'
        magic_stop = 'stop_magic_magic_stop'

        # save pexpect config
        old_timeout = self.s.timeout
        old_logfile = self.s.logfile

        self.s.s.timeout = cmd_timeout + 10

        with open(logfile, 'wb') as fdw:
            self.s.logfile = fdw

            self.s.send('echo ' + magic_start + '\n')
            self.s.expect(magic_start)

            self.s.send(cmd + '\n')
            time.sleep(cmd_timeout)

            self.s.send('echo ' + magic_stop + '\n')
            self.s.expect(magic_stop)

        # restore pexpect config
        self.s.timeout = old_timeout
        self.s.logfile = old_logfile

        with open(logfile, 'rb') as fdr:
            content = fdr.read().decode('utf-8')

        shCmd('rm -f %s' % logfile)

        # different version pexpects return slightly different results
        ptn = r'(?s)%s\s*(.*?)%s' % (self.prompt + cmd, self.prompt + 'echo ' + magic_stop)
        found = re.search(ptn, content)
        if found is not None:
            content = found.groups()[0].replace(magic_start, '').replace('echo ', '').strip()
            if strip_lines:
                return [line.strip() for line in content.split('\n')]
            else:
                return [line for line in content.split('\n')]
        else:
            return []

    def return_all(self, strip_lines=True, wait_timeout=-1):
        """
        A list of lines is returned as result. All lines are stripped
        of leading/ending whitespace if "strip_lines".
        (uses pexpect)
        """
        self.wait_prompt(timeout=wait_timeout)
        ret = self.s.before
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

    def send_ctrl_c(self):
        # send CTRL+C and wait for promt
        print('shell_ops : send Ctrl+C')
        self.s.s.send('\003')  # send ctrl+c to target
        self.s.s.expect(self.prompt)


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
            target.wait_prompt(1)  # not possible
        except:  # pexpect.TIMEOUT:
            pass


default_s_args = {'log': None,
                  'logverbose': None,
                  'addr': None,
                  'port': None,
                  'user': None,
                  'passwd': None,
                  'name': None,
                  'native': False,
                  'dry': None,
                  'target_access': '',
                  'target_prefix': None,
                  'timeout': 30,
                  }


class proxy(object):
    def __init__(self, session_type_name, s_args):
        assert session_type_name in ('telnet', 'ssh',)
        session_class = globals()[session_type_name]
        full_s_args = self.__create_args(s_args)
        s = session_class(**full_s_args)
        # if prompt is not None:
        #    s.old_prompt = prompt
        s.login()
        self.s = s
        shops = shell_ops(s)
        self.shops = shops

    def __create_args(self, s_args):
        ret_s_args = default_s_args
        for k in s_args:
            if k in ret_s_args:
                ret_s_args[k] = s_args[k]
        return ret_s_args

    def __getattr__(self, x):
        if hasattr(self.shops, x):
            return getattr(self.shops, x)  # hit step in pdb
        return getattr(self.tops, x)  # hit step in pdb

    def logout(self):
        self.shops.s.logout()
