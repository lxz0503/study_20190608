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
"""Ipnet tcp socktest tests"""

from pytestAuto.utils.api import _config, _test


class c0010socket:
    ''' tcp socket test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'socket'
        return _test(self, log, hosts, v6, opt, proto, funcname)
 
class c0020bind:
    """ tcp bind test """
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'bind'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0030connect:
    ''' tcp connect test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'connect'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0040accept:
    ''' tcp accept test '''
    def config(self):
        eta = 8
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'accept'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0050getsockname:
    ''' tcp getsockname test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'getsockname'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0060getpeername:
    ''' tcp getpeername test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'getpeername'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0070send:
    ''' tcp send test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'send'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0080sendto:
    ''' tcp sendto test '''
    def config(self):
        eta = 2
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'sendto'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0090sendmsg:
    ''' tcp sendmsg test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'sendmsg'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0100recv:
    ''' tcp recv test '''
    def config(self):
        eta = 2
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'recv'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0110recvfrom:
    ''' tcp recvfrom test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'recvfrom'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0120recvmsg:
    ''' tcp recvmsg test '''
    def config(self):
        eta = 2
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'recvmsg'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0130ioctl:
    ''' tcp ioctl test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'ioctl'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0140select:
    ''' tcp select test '''
    def config(self):
        eta = 8
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'select'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0150shutdown:
    ''' tcp shutdown test '''
    def config(self):
        eta = 1
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'shutdown'
        return _test(self, log, hosts, v6, opt, proto, funcname)

class c0160close:
    ''' tcp close test '''
    def config(self):
        eta = 11
        _config(self, eta)
 
    def test(self, log, hosts, v6, opt):
        proto = 'tcp'
        funcname = 'close'
        return _test(self, log, hosts, v6, opt, proto, funcname)

