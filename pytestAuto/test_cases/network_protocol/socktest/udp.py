#############################################################################
#
# Copyright (c) 2020-2021 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

#
"""Ipnet udp socktest tests"""

from pytestAuto.utils.api import _config, _test

class c0010socket:
    ''' udp socket test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'socket'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0020bind:
    ''' udp bind test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'bind'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0030connect:
    ''' udp connect test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'connect'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0050getsockname:
    ''' udp getsockname test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'getsockname'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0060getpeername:
    ''' udp getpeername test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'getpeername'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0070send:
    ''' udp send test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'send'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0080sendto:
    ''' udp sendto test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'sendto'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0090sendmsg:
    ''' udp sendmsg test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'sendmsg'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0100recv:
    ''' udp recv test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'recv'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0110recvfrom:
    ''' udp recvfrom test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'recvfrom'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0120recvmsg:
    ''' udp recvmsg test '''
    def config(self):
        eta = 2
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'recvmsg'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0130ioctl:
    ''' udp ioctl test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'ioctl'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0140select:
    ''' udp select test '''
    def config(self):
        eta = 7
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'select'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0150shutdown:
    ''' udp shutdown test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'udp'
        funcname = 'shutdown'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0170recvmsg_controllen:
    '''udp socket recvmsg msghdr.msg_controllen test '''
    def config(self):
       self.hosts = 2
       self.eta = 1 
       self.v6 = True
       
    def test(self, log, hosts, v6, opt):
        log('run udp socket recvmsg controllen test', echo=True)
        server, client = hosts
        s, c = server.ipcom_shell(), client.ipcom_shell()

        s6 = '6' if v6 else ''
        s_ip = s.ip(6) if v6 else s.ip()

        c_cmd = 'C mysendto%s("%s")' % (s6, s_ip)

        # msghdr.msg_controllen set to '1' 
        s_cmd = 'C recvmsg_controllen_test%s(1)' % s6
        s.send(s_cmd)
        c.send_and_wait_prompt(c_cmd)
        if 'test pass' not in s.return_all():
            raise test_fail('msg_controllen is not 0 when truncated.')

        # msghdr.msg_controllen set to '16'
        s_cmd = 'C recvmsg_controllen_test%s(16)' % s6
        s.send(s_cmd)
        c.send_and_wait_prompt(c_cmd)
        if 'test pass' not in s.return_all():
            raise test_fail('recvmsg failed for enough msg_controllen.')

