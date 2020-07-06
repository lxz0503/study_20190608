#!/usr/bin/env python
#############################################################################
#
# Copyright (c) 2006-2020 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

#
#modification history
#--------------------
#31mar20,clb update for helix support
#18mar20,rza support to send CTRL+]
#30aug17,clb support to capture "route monitor" output
#16sep14,dlk Fix merge error.
#21jul14,h_s change error number for ipsec related self test cases, V7SEC-6.
#29apr14,h_s adapt test script for vx7, US35892.
#


import sys
#sys.path.insert(0, 'thirdparty')

import os
import pdb
import pexpect
import re
import stat
import time
import traceback
import threading

from commands import getoutput
from threading import Thread
from pexpect import TIMEOUT

# xiaozhan    below is the config file
# hyan1@pek-vx-nwk1:/buildarea1/hyan1/vxworks7/helix/guests/vxworks-7/pkgs_v2/net/ipnet/NOT_IMPORTED/iptestengine/src$ ls ../config/config.py
# ../config/config.py*
# hyan1@pek-vx-nwk1:/buildarea1/hyan1/vxworks7/helix/guests/vxworks-7/pkgs_v2/net/ipnet/NOT_IMPORTED/iptestengine/src$ vi ../config/config.py

sys.path.insert(0, '../config')
import config
from util import *

################################################################################
#                       Errno string maps
################################################################################

errnos_default = {
        # defaults from linux. Note there are some duplicates (e.g. EWOULDBLOCK is EAGAIN)
        # We really only need a small subset of these...

        'E2BIG' : 'Argument list too long',
        'EACCES' : 'Permission denied',
        'EADDRINUSE' : 'Address already in use',
        'EADDRNOTAVAIL' : 'Cannot assign requested address',
        'EADV' : 'Advertise error',
        'EAFNOSUPPORT' : 'Address family not supported by protocol',
        'EAGAIN' : 'Resource temporarily unavailable',
        'EALREADY' : 'Operation already in progress',
        'EBADE' : 'Invalid exchange',
        'EBADF' : 'Bad file descriptor',
        'EBADFD' : 'File descriptor in bad state',
        'EBADMSG' : 'Bad message',
        'EBADR' : 'Invalid request descriptor',
        'EBADRQC' : 'Invalid request code',
        'EBADSLT' : 'Invalid slot',
        'EBFONT' : 'Bad font file format',
        'EBUSY' : 'Device or resource busy',
        'ECANCELED' : 'Operation canceled',
        'ECHILD' : 'No child processes',
        'ECHRNG' : 'Channel number out of range',
        'ECOMM' : 'Communication error on send',
        'ECONNABORTED' : 'Software caused connection abort',
        'ECONNREFUSED' : 'Connection refused',
        'ECONNRESET' : 'Connection reset by peer',
        'EDEADLK' : 'Resource deadlock avoided',
        'EDEADLOCK' : 'Resource deadlock avoided',
        'EDESTADDRREQ' : 'Destination address required',
        'EDOM' : 'Numerical argument out of domain',
        'EDOTDOT' : 'RFS specific error',
        'EDQUOT' : 'Disk quota exceeded',
        'EEXIST' : 'File exists',
        'EFAULT' : 'Bad address',
        'EFBIG' : 'File too large',
        'EHOSTDOWN' : 'Host is down',
        'EHOSTUNREACH' : 'No route to host',
        'EHWPOISON' : 'Memory page has hardware error',
        'EIDRM' : 'Identifier removed',
        'EILSEQ' : 'Invalid or incomplete multibyte or wide character',
        'EINPROGRESS' : 'Operation now in progress',
        'EINTR' : 'Interrupted system call',
        'EINVAL' : 'Invalid argument',
        'EIO' : 'Input/output error',
        'EISCONN' : 'Transport endpoint is already connected',
        'EISDIR' : 'Is a directory',
        'EISNAM' : 'Is a named type file',
        'EKEYEXPIRED' : 'Key has expired',
        'EKEYREJECTED' : 'Key was rejected by service',
        'EKEYREVOKED' : 'Key has been revoked',
        'EL2HLT' : 'Level 2 halted',
        'EL2NSYNC' : 'Level 2 not synchronized',
        'EL3HLT' : 'Level 3 halted',
        'EL3RST' : 'Level 3 reset',
        'ELIBACC' : 'Can not access a needed shared library',
        'ELIBBAD' : 'Accessing a corrupted shared library',
        'ELIBEXEC' : 'Cannot exec a shared library directly',
        'ELIBMAX' : 'Attempting to link in too many shared libraries',
        'ELIBSCN' : '.lib section in a.out corrupted',
        'ELNRNG' : 'Link number out of range',
        'ELOOP' : 'Too many levels of symbolic links',
        'EMEDIUMTYPE' : 'Wrong medium type',
        'EMFILE' : 'Too many open files',
        'EMLINK' : 'Too many links',
        'EMSGSIZE' : 'Message too long',
        'EMULTIHOP' : 'Multihop attempted',
        'ENAMETOOLONG' : 'File name too long',
        'ENAVAIL' : 'No XENIX semaphores available',
        'ENETDOWN' : 'Network is down',
        'ENETRESET' : 'Network dropped connection on reset',
        'ENETUNREACH' : 'Network is unreachable',
        'ENFILE' : 'Too many open files in system',
        'ENOANO' : 'No anode',
        'ENOBUFS' : 'No buffer space available',
        'ENOCSI' : 'No CSI structure available',
        'ENODATA' : 'No data available',
        'ENODEV' : 'No such device',
        'ENOENT' : 'No such file or directory',
        'ENOEXEC' : 'Exec format error',
        'ENOKEY' : 'Required key not available',
        'ENOLCK' : 'No locks available',
        'ENOLINK' : 'Link has been severed',
        'ENOMEDIUM' : 'No medium found',
        'ENOMEM' : 'Cannot allocate memory',
        'ENOMSG' : 'No message of desired type',
        'ENONET' : 'Machine is not on the network',
        'ENOPKG' : 'Package not installed',
        'ENOPROTOOPT' : 'Protocol not available',
        'ENOSPC' : 'No space left on device',
        'ENOSR' : 'Out of streams resources',
        'ENOSTR' : 'Device not a stream',
        'ENOSYS' : 'Function not implemented',
        'ENOTBLK' : 'Block device required',
        'ENOTCONN' : 'Transport endpoint is not connected',
        'ENOTDIR' : 'Not a directory',
        'ENOTEMPTY' : 'Directory not empty',
        'ENOTNAM' : 'Not a XENIX named type file',
        'ENOTRECOVERABLE' : 'State not recoverable',
        'ENOTSOCK' : 'Socket operation on non-socket',
        'ENOTSUP' : 'Operation not supported',
        'ENOTTY' : 'Inappropriate ioctl for device',
        'ENOTUNIQ' : 'Name not unique on network',
        'ENXIO' : 'No such device or address',
        'EOPNOTSUPP' : 'Operation not supported',
        'EOVERFLOW' : 'Value too large for defined data type',
        'EOWNERDEAD' : 'Owner died',
        'EPERM' : 'Operation not permitted',
        'EPFNOSUPPORT' : 'Protocol family not supported',
        'EPIPE' : 'Broken pipe',
        'EPROTO' : 'Protocol error',
        'EPROTONOSUPPORT' : 'Protocol not supported',
        'EPROTOTYPE' : 'Protocol wrong type for socket',
        'ERANGE' : 'Numerical result out of range',
        'EREMCHG' : 'Remote address changed',
        'EREMOTE' : 'Object is remote',
        'EREMOTEIO' : 'Remote I/O error',
        'ERESTART' : 'Interrupted system call should be restarted',
        'ERFKILL' : 'Operation not possible due to RF-kill',
        'EROFS' : 'Read-only file system',
        'ESHUTDOWN' : 'Cannot send after transport endpoint shutdown',
        'ESOCKTNOSUPPORT' : 'Socket type not supported',
        'ESPIPE' : 'Illegal seek',
        'ESRCH' : 'No such process',
        'ESRMNT' : 'Srmount error',
        'ESTALE' : 'Stale file handle',
        'ESTRPIPE' : 'Streams pipe error',
        'ETIME' : 'Timer expired',
        'ETIMEDOUT' : 'Connection timed out',
        'ETOOMANYREFS' : 'Too many references: cannot splice',
        'ETXTBSY' : 'Text file busy',
        'EUCLEAN' : 'Structure needs cleaning',
        'EUNATCH' : 'Protocol driver not attached',
        'EUSERS' : 'Too many users',
        'EWOULDBLOCK' : 'Resource temporarily unavailable',
        'EXDEV' : 'Invalid cross-device link',
        'EXFULL' : 'Exchange full',
    }

errnos_default_vx = {
        # Default generic errno strings for VxWorks.
        # We only need a subset of these.  Also, we run the 'errnos' command to get
        # a more accurate list for the target.
        'EPERM' : 'S_errno_EPERM',
        'ENOENT' : 'S_errno_ENOENT',
        'ESRCH' : 'S_errno_ESRCH',
        'EINTR' : 'S_errno_EINTR',
        'EIO' : 'S_errno_EIO',
        'ENXIO' : 'S_errno_ENXIO',
        'E2BIG' : 'S_errno_E2BIG',
        'ENOEXEC' : 'S_errno_ENOEXEC',
        'EBADF' : 'S_errno_EBADF',
        'ECHILD' : 'S_errno_ECHILD',
        'EAGAIN' : 'S_errno_EAGAIN',
        'ENOMEM' : 'S_errno_ENOMEM',
        'EACCES' : 'S_errno_EACCES',
        'EFAULT' : 'S_errno_EFAULT',
        'ENOTEMPTY' : 'S_errno_ENOTEMPTY',
        'EBUSY' : 'S_errno_EBUSY',
        'EEXIST' : 'S_errno_EEXIST',
        'EXDEV' : 'S_errno_EXDEV',
        'ENODEV' : 'S_errno_ENODEV',
        'ENOTDIR' : 'S_errno_ENOTDIR',
        'EISDIR' : 'S_errno_EISDIR',
        'EINVAL' : 'S_errno_EINVAL',
        'ENFILE' : 'S_errno_ENFILE',
        'EMFILE' : 'S_errno_EMFILE',
        'ENOTTY' : 'S_errno_ENOTTY',
        'ENAMETOOLONG' : 'S_errno_ENAMETOOLONG',
        'EFBIG' : 'S_errno_EFBIG',
        'ENOSPC' : 'S_errno_ENOSPC',
        'ESPIPE' : 'S_errno_ESPIPE',
        'EROFS' : 'S_errno_EROFS',
        'EMLINK' : 'S_errno_EMLINK',
        'EPIPE' : 'S_errno_EPIPE',
        'EDEADLK' : 'S_errno_EDEADLK',
        'ENOLCK' : 'S_errno_ENOLCK',
        'ENOTSUP' : 'S_errno_ENOTSUP',
        'EMSGSIZE' : 'S_errno_EMSGSIZE',
        'EDOM' : 'S_errno_EDOM',
        'ERANGE' : 'S_errno_ERANGE',
        'EDESTADDRREQ' : 'S_errno_EDESTADDRREQ',
        'EPROTOTYPE' : 'S_errno_EPROTOTYPE',
        'ENOPROTOOPT' : 'S_errno_ENOPROTOOPT',
        'EPROTONOSUPPORT' : 'S_errno_EPROTONOSUPPORT',
        'ESOCKTNOSUPPORT' : 'S_errno_ESOCKTNOSUPPORT',
        'EOPNOTSUPP' : 'S_errno_EOPNOTSUPP',
        'EPFNOSUPPORT' : 'S_errno_EPFNOSUPPORT',
        'EAFNOSUPPORT' : 'S_errno_EAFNOSUPPORT',
        'EADDRINUSE' : 'S_errno_EADDRINUSE',
        'EADDRNOTAVAIL' : 'S_errno_EADDRNOTAVAIL',
        'ENOTSOCK' : 'S_errno_ENOTSOCK',
        'ENETUNREACH' : 'S_errno_ENETUNREACH',
        'ENETRESET' : 'S_errno_ENETRESET',
        'ECONNABORTED' : 'S_errno_ECONNABORTED',
        'ECONNRESET' : 'S_errno_ECONNRESET',
        'ENOBUFS' : 'S_errno_ENOBUFS',
        'EISCONN' : 'S_errno_EISCONN',
        'ENOTCONN' : 'S_errno_ENOTCONN',
        'ESHUTDOWN' : 'S_errno_ESHUTDOWN',
        'ETOOMANYREFS' : 'S_errno_ETOOMANYREFS',
        'ETIMEDOUT' : 'S_errno_ETIMEDOUT',
        'ECONNREFUSED' : 'S_errno_ECONNREFUSED',
        'ENETDOWN' : 'S_errno_ENETDOWN',
        'ETXTBSY' : 'S_errno_ETXTBSY',
        'ELOOP' : 'S_errno_ELOOP',
        'EHOSTUNREACH' : 'S_errno_EHOSTUNREACH',
        'ENOTBLK' : 'S_errno_ENOTBLK',
        'EHOSTDOWN' : 'S_errno_EHOSTDOWN',
        'EINPROGRESS' : 'S_errno_EINPROGRESS',
        'EALREADY' : 'S_errno_EALREADY',
        'EWOULDBLOCK' : 'S_errno_EWOULDBLOCK',
        'ENOSYS' : 'S_errno_ENOSYS',
        'ECANCELED' : 'S_errno_ECANCELED',
        'ENOSR' : 'S_errno_ENOSR',
        'ENOSTR' : 'S_errno_ENOSTR',
        'EPROTO' : 'S_errno_EPROTO',
        'EBADMSG' : 'S_errno_EBADMSG',
        'ENODATA' : 'S_errno_ENODATA',
        'ETIME' : 'S_errno_ETIME',
        'ENOMSG' : 'S_errno_ENOMSG',
        'EFPOS' : 'S_errno_EFPOS',
        'EILSEQ' : 'S_errno_EILSEQ',
        'EDQUOT' : 'S_errno_EDQUOT',
        'EIDRM' : 'S_errno_EIDRM',
        'EOVERFLOW' : 'S_errno_EOVERFLOW',
        'EMULTIHOP' : 'S_errno_EMULTIHOP',
        'ENOLINK' : 'S_errno_ENOLINK',
        'ESTALE' : 'S_errno_ESTALE'
    }


################################################################################
#                       Exceptions
################################################################################
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


class config_error(ip_exception):
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

################################################################################
#                       Functions
################################################################################
def isiterable(o):
    return hasattr(o, '__iter__') or (hasattr(o, '__len__') and hasattr(o, '__getitem__'))

wants_to_quit = False
def safe(f, *args, **kwargs):
    'runs something and silently discards errors'
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
            target.wait_prompt(1) #not possible
        except: # pexpect.TIMEOUT:
            pass

def gmtime_str():
    return '%d%02d%02d_%02d.%02d.%02d' % time.gmtime()[:6]

def localtime_str():
    return '%d%02d%02d_%02d.%02d.%02d' % time.localtime()[:6]

def _eta_str(eta):
    if eta > 59:
        return '%sm %ss' % divmod(eta, 60)
    else:
        return '%ss' % eta

class _log(object):        #  xiaozhan, analyze how to capture log
    #!!! one global and one per object. make each instance call the class method to make the global/merged log
    def __init__(self, log, verbose):    # xiaozhan,  log is a file handler
        self.testname = ''
        self.logfile = log
        self.verbose = verbose
        self.context = ''
        self.logfile.write('Begin log at GMT: (%s), Localtime: (%s)\n' % (time.asctime(time.gmtime()), time.asctime(time.localtime())))
        self.logfile.write('Following timestamps are GMT\n')
        self.starttime = None
        self.v6 = ''


    def __call__(self, msg, newline = True, echo = False, printtime = False, context = False):
        """Write msg to the logfile.
        Default is to add a newline, not echo it to screen too, not prepend the output with a timestamp and not write the product.file.test context on each line."""
        s = ''
        if printtime:
            s = gmtime_str() + ' '
        if context:
            s += self.context + ' - '
        s += msg
        self.logfile.write(s + '\n')
        if echo:
            if newline:
                print s
            else:
                print s.ljust(75),
                sys.stdout.flush()
        elif self.verbose:
            print s


    def write(self, s):
        self(s)


    def flush(self):
        self.logfile.flush()


    def start(self, test, quiet, v6, echo):
        newcontext = test.prodname + '.' + test.modname + '.' + test.testname
        if self.context != '':
            raise engine_error('log.start: new test started without ending the last one. new=%s, old=%s' % (newcontext, self.context))
        self('')
        self('-'*80)
        self('-'*30 + ' Test starts ' + '-'*37)
        self('-'*80)
        self.context = newcontext
        if not test.doc:
            raise engine_error('\nYou forgot to document your test "%s"' % newcontext)
        timestr = "ETA: " + _eta_str(test.eta)
        self('\n' + ' '*4 + test.doc + '.', echo = not quiet)
        self('IPv' + ('4','6')[int(bool(v6))] + " " + timestr, newline = False, echo = echo, context = True)
        self.v6 = v6
        self.starttime = time.time()


    def stop(self, success = True):
        if not self.starttime:
            return
        time_passed = int(time.time() - self.starttime)
        self('')
        if isinstance(success, list):
            self.__handle_test_results(success, time_passed)
        else:
            if isinstance(success, str) and success.startswith('skipped'):
                self(self.context + ' Test %s ' % success  + '-'*60)
            elif success:
                self(self.context + ' Test Passed ' + '-'*40)
            else:
                self(self.context + ' Test Failed ' + '-'*60)
            oldcontext = self.context
            self.context = ''
            if isinstance(success, str) and success.startswith('skipped'):
                self(success, newline = True, echo = True)
            elif isinstance(success, str) and success.startswith('restart'):
                self(success, newline = True, echo = True)
            elif success:
                self('OK ' + _eta_str(time_passed), newline = True, echo = True, printtime = False)
            else:
                if oldcontext:
                    self(oldcontext + ' test case failed', newline = True, echo = True)
                else:
                    self(oldcontext + ' failed', newline = True, echo = True)
        
        self('-'*80)
        self('-'*30 + ' Test ends ' + '-'*39)
        self('-'*80)

    def __handle_test_results(self, test_results, time_passed):
        # handle a list of test case results
        # assume each list element is (testName, testResult)
        test_duration = int(time_passed / len(test_results) + 0.5)
        timestr = "ETA: " + _eta_str(test_duration)
        for test_name, test_result in test_results:
            self('%s - IPv' % test_name + ('4','6')[int(bool(self.v6))] + " " + timestr, newline = False, echo = True)
            if test_result.lower() == 'skip':
                self('skipped', newline = True, echo = True)
            elif test_result.lower() == 'pass':
                self('OK ' + _eta_str(test_duration), newline = True, echo = True, printtime = False)
            elif test_result.lower() == 'fail':
                self(' failed', newline = True, echo = True)
            else:
                raise internal_error('test case %s result %s not recognized' % (test_name, test_result))
        self.context = ''
        

################################################################################
#                       session types
################################################################################
class session(object):
    def __init__(self, log=None, logverbose=None, addr=None, port=None, user=None, passwd=None, name=None, native = False, dry=None, relogin = False, target_access=None, target_prefix = None, timeout = 30): #interactive=False
        # relogin = hack since ipcom shell share the same prompt variable across login shells
        #self.__dict__.update(kwargs)
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
        self.prompt_magic = 'XunXiqX' #
        #if name:
        self.prompt = name + '_' + self.prompt_magic
        self.bailmsg = '%s\nYou probably forgot to start the target: %s at %s:%s\n%s' % ('x'*79, name, addr, port, 'x'*80)
        self.sudo = '%s'
        #self.interactive=interactive
        self.errnos = errnos_default


    #pexpect session is stored in self.s between __init__ and second_init
    def second_init(self, timeout = 30):
        self.s.timeout = timeout


    def login(self):
        for t in range(3):
            try:
                self._login()
            except config_error:
                pass
                #print "try %s" % t
            else:
                break
        else:
            self.log("Couldn't login to %s at %s://%s%s@%s:%s" % (self.name, self.type, self.user, IF(self.passwd is None, "", ':%s' % self.passwd), self.login_ip.addr, self.port), echo=True)
            raise config_error("4"+self.bailmsg)


    def send(self, cmd, newline, sudo = True):
        #print "%d:%s" % (len(cmd), cmd)
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


class _dummy:
    def setlog(*_):
        pass


#ipout
class telnet(session):
    'operates on an iptarget'
    def _login(self):
        self.type = 'telnet'
        self.shelltype = 'dontknow'
        #print 'Logging in to %s:%s using telnet' % (self.login_ip.addr, self.port)
        s = _dummy()
        timeout = None
        for tries in range(5):
            try:
                if not self.dry:
                    tcmd = "%s%s %s %d" % (self.target_access, self.type, self.login_ip.addr, self.port)
                    #print 'telnet cmd:%s, prompt:%s' % (tcmd, self.prompt)
                    s = pexpect.spawn(tcmd, timeout=20)
                    # Linux is needs some time to turn  TTY echo off during login
                    # so we should not set delaybeforesend to 0 yet.
                    # s.delaybeforesend = 0
                    telnet_timeout = False
                    
                expect_array = [r'Welcome to (\w+)[!|\s]', # 0
                                  'assword: ',             # 1
                                  'ogin: ',                # 2 
                                  'vxWorks',               # 3
                                  '-> ',                   # 4
                                  'BusyBox ',              # 5
                                  'sh-',                   # 6
                                  '# ',                    # 7
                                  'RTNET> ',               # 8
                               ]
                
                for _ in range(4):
                    try:
                        i = s.expect(expect_array, timeout = 10)
    
                        if i == 5 or i == 6 or i == 7: # 'BusyBox ', 'sh-', '# ',
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
                        if i == 4: # '-> ', 
                            if not self.dry:
                                s.sendline('cmd')
                        if i == 3: # 'vxWorks',
                            # vxworks native shell.
                            self.errnos = errnos_default_vx
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
                            self.shelltype = 'vxworks'
                            break
                        if i == 2: # 'ogin: ',  
                            if not self.user:
                                raise config_error('%s\nA user was required but none configured for target: %s at %s:%s\n%s' % ('x'*79, self.name, self.addr, self.port, 'x'*80))
                            s.sendline(self.user)
                        if i == 1: # 'assword: ', 
                            if not self.passwd:
                                raise config_error('%s\nA password was required but none configured for target: %s at %s:%s\n%s' % ('x'*79, self.name, self.addr, self.port, 'x'*80))
                            s.sendline(self.passwd) # password correct?
    
                            expect_array.append('@')
                            
                        if i == 8 or i == 9:
                            if telnet_timeout:
                                # RTNet
                                self.prompt = 'RTNET> '
                                self.shelltype = 'rtnet'
                                break                                
                            else:
                                if not self.dry:
                                    self.prompt = self.prompt.split('_')[0] + '_' + self.login_ip.addr + '_' + self.prompt.split('_')[1]
                                    s.sendline('export PS1="%s"' % self.prompt)
                                    s.expect(re.escape(self.prompt))
                                    s.expect(re.escape(self.prompt))
                                    # The UML's are a bit slow at times.
                                    timeout = 40
        
                                if self.user != 'root':
                                    self.sudo = 'sudo %s'
                                self.shelltype = 'linux'
                                break
                        
                        if i == 0: # r'Welcome to (\w+)[!|\s]',
                            r = s.match.group(1)
                            if r == 'OSE': #nowhere near support for OSE yet
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
                                i = s.expect(['ok', TIMEOUT])
                                if i == 1:
                                    self.log(self.bailmsg, newline = True, echo = True)
                                    sys.stdout.flush()
                                    raise config_error("3"+self.bailmsg)
                            s.expect(re.escape(self.prompt))
                            break
                    except pexpect.TIMEOUT:
                        s.send('\r')
                        telnet_timeout = True
                else:
                    # we failed to parse the login prompt
                    raise config_error('%s\nFailed to login using telnet: %s at %s:%s\n%s' % ('x'*79, self.name, self.addr, self.port, 'x'*80))

                #successful login
                break
            except config_error, inst:
                raise
            except:
                import time
                time.sleep(1)
        else:
            self.log("Failed to establish telnet connection to %s" % (self.login_ip.addr))
            raise config_error(self.bailmsg)

        s.delaybeforesend = 0

        if not timeout:
            timeout = self.timeout
        self.s = s
        self.second_init(timeout = timeout)

    def logout(self):
        if self.shelltype == 'rtnet':
            self.s.sendcontrol(']')
            self.s.expect('telnet> ')
            self.s.sendline('q')
            self.s.expect('Connection closed.')
        else:
            self.s.sendline('exit')
            self.s.expect(pexpect.EOF)
            #self.s.wait()
            #self.s.expect_exact('Connection closed by foreign host')

    def send(self, cmd, newline, sudo=True, *a, **k):
        if not sudo:
            cmd2 = cmd
        else:
            cmd2 = self.sudo % cmd
        session.send(self, cmd2, newline, sudo)
        return cmd2



#Linux mgmt for uNAP
class utelnet(session):
    'operates on an iptarget'
    def _login(self):
        self.type = 'telnet'
        self.shelltype = 'dontknow'
        #print 'Logging in to %s:%s using telnet' % (self.login_ip.addr, self.port)
        s = _dummy()
        brk = False
        timeout = None

        for tries in range(5):
            try:

                if not self.dry:
                    tcmd = "%s%s %s %d" % (self.target_access, self.type, self.login_ip.addr, self.port)
                    #s = pexpect.spawn(self.type, [self.login_ip.addr, str(self.port)], 20)
                    s = pexpect.spawn(tcmd, timeout=20)
                    # Linux is needs some time to turn  TTY echo off during login
                    # so we should not set delaybeforesend to 0 yet.
                    # s.delaybeforesend = 0

                expect_array = [  'assword: ', 'ogin: ']
                for _ in range(5):
                    i = s.expect(expect_array, timeout = 60)

                    if i == 0:
                        if not self.passwd:
                            raise config_error('%s\nA password was required but none configured for target: %s at %s:%s\n%s' % \
                                                   ('x'*79, self.name, self.addr, self.port, 'x'*80))
                        s.sendline(self.passwd) # password correct?

                        expect_array.append('@')
                        break

                    if i == 1:
                        if not self.user:
                            raise config_error('%s\nA user was required but none configured for target: %s at %s:%s\n%s' % \
                                                   ('x'*79, self.name, self.addr, self.port, 'x'*80))
                        s.sendline(self.user)
                else:
                    # we failed to parse the login prompt
                    raise config_error('%s\nFailed to login using telnet: %s at %s:%s\n%s' % \
                                           ('x'*79, self.name, self.addr, self.port, 'x'*80))

                for _ in range(2):
                    i = s.expect([r'Welcome to (\w+)[!|\s]', '\$ '], timeout = 60)
                    if i ==  0:

                        r = s.match.group(1)
                        if r == 'uNAP':
                            self.prompt = '#>1'

                        if r == 'Ubuntu':
                            self.prompt = 'uNAPmgmt>'

                    if i == 1:
                        break
                else:

                    raise config_error('unable to login')

                if not self.dry:
                    s.sendline('export PS1="%s"' % self.prompt)
                    s.expect(re.escape(self.prompt))
                    s.expect(re.escape(self.prompt))
                            # The UML's are a bit slow at times.
                    timeout = 40

                    if self.user != 'root':
                        self.sudo = 'sudo %s'
                    self.shelltype = 'linux'

                #successful login
                break
            except config_error, inst:
                raise
            except:
                import time
                time.sleep(1)
        else:
            self.log("Failed to establish uNAP telnet connection to %s" % (self.login_ip.addr))
            raise config_error(self.bailmsg)

        s.delaybeforesend = 0

        if not timeout:
            timeout = 30
        self.s = s
        self.second_init(timeout = timeout)

    def logout(self):
        self.s.sendline('exit')
        self.s.expect(pexpect.EOF)
        #self.s.wait()
        #self.s.expect_exact('Connection closed by foreign host')

    def send(self, cmd, newline, sudo=True, *a, **k):
        if not sudo:
            cmd2 = cmd
        else:
            cmd2 = self.sudo % cmd
        session.send(self, cmd2, newline, sudo)
        return cmd2

#bash on linux
class ssh(session):
    '''operates on a baselinux
    Expects passwordless sudo unless logged in as root.'''
    def _login(self):
        self.type = 'ssh'
        #log('Logging in to %s:%s using ssh' % (addr, port))
        s = _dummy()
        if not self.dry:
            try:
                cmd = 'ssh '
                cmd += '-x -p %s -l %s %s "sh --noprofile -i"' % (self.port, self.user, self.login_ip.addr)
                self.log(cmd)
                s = pexpect.spawn(cmd)
                # Linux is needs some time to turn  TTY echo off during login
                # so we should not set delaybeforesend to 0 yet.
                s.delaybeforesend = 1 # rime

            except pexpect.TIMEOUT:
                raise config_error(self.bailmsg)

            oldprompt = 'sh-.*[$#]'
            for _ in range(2):
                i = s.expect([oldprompt,
                                 'assword: ',
                                 'Are you sure you want to continue connecting \(yes/no\)\? ',
                                 '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@']) #Offending key in .ssh/known_hosts
                if i == 3:
                    s.expect("Host key verification failed")
                    #s.expect("(Offending key in .*)\r\n")
                    raise config_error(s.before)
                if i == 2:
                    s.sendline('yes')
                if i == 1:
                    if not self.passwd:
                        raise config_error('%s\nA password was required but none configured for target: %s at %s:%s\n%s' % ('x'*79, self.name, self.addr, self.port, 'x'*80))
                    s.sendline(self.passwd) # password correct?
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
            self.s.sendline('exit') # don't use sudo here
            self.s.expect(pexpect.EOF)
            #self.s.wait()
            #self.s.expect_exact(r'Connection to \w+ closed')


    def send(self, cmd, newline, sudo=True, *a, **k):
        if not sudo:
            cmd2 = cmd
        else:
            cmd2 = self.sudo % cmd
        session.send(self, cmd2, newline, sudo)
        return cmd2


class ipcom_ssh(session):
    'operates on an iptarget'
    def _login(self):
        self.type = 'ipcom_ssh'
        s = _dummy()
        if not self.dry:
            try:
                cmd = 'ssh -x -t -p %s -l %s %s' % (self.port, 'ftp', self.login_ip.addr)
                self.log(cmd)
                s = pexpect.spawn(cmd)
                # Linux is needs some time to turn  TTY echo off during login
                # so we should not set delaybeforesend to 0 yet.
                #s.delaybeforesend = 0

            except pexpect.TIMEOUT:
                raise config_error(self.bailmsg)

            for _ in range(2):
                i = s.expect([self.prompt_magic,
                              'assword: ',
                              'Are you sure you want to continue connecting \(yes/no\)\? ',
                              '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', #Offending key in .ssh/known_hosts
                              ':' + re.escape(self.login_ip.addr)])
                if i == 3:
                    s.expect(re.escape("Host key verification failed"))
                    #s.expect("(Offending key in .*)\r\n")
                    raise config_error(s.before)
                if i == 2:
                    s.sendline('yes')
                if i == 1:
                    if not self.passwd:
                        raise config_error('%s\nA password was required but none configured for target: %s at %s:%s\n%s' % ('x'*79, self.name, self.addr, self.port, 'x'*80))
                    s.sendline('interpeak') # password correct?
                    s.expect([re.escape(self.login_ip.addr), re.escape(self.prompt_magic)])
                    break
                if i == 0 or i == 4:
                    break

        s.delaybeforesend = 0

        self.s = s
        self.second_init()


    def logout(self):
        self.s.sendline('exit')
        self.s.expect(pexpect.EOF)
        #self.s.wait()
        #self.s.expect_exact('Connection closed by foreign host')


class bash(session):
    '''operates on a baselinux
    Expects passwordless sudo unless logged in as root.'''
    def _login(self):
        self.type = 'bash'

        #log('Logging in to %s:%s using ssh' % (addr, port))
        s = _dummy()
        if not self.dry:
            try:
                cmd = self.target_access + "bash"
                print cmd
                self.log(cmd)
                s = pexpect.spawn(self.sudo % cmd)

            except pexpect.TIMEOUT:
                raise config_error(self.bailmsg)

            #s.setecho(False)
            s.sendline('export PS1="%s"' % self.prompt)
            s.expect(re.escape(self.prompt))
            s.expect(re.escape(self.prompt))
            s.expect(re.escape(self.prompt))

        s.delaybeforesend = 0

        self.s = s
        self.second_init()


    def logout(self):
        if not self.dry:
            self.s.sendline('exit') # don't use sudo here
            self.s.expect(pexpect.EOF)

    def send(self, cmd, newline, sudo=True, *a, **k):
        if not sudo:
            cmd2 = cmd
        else:
            cmd2 = self.sudo % cmd
        session.send(self, cmd2, newline, sudo)
        return cmd2

################################################################################
# shell operations
class shell_ops(object):
    def __init__(self, session):
        self.s = session
        self.rmdir_cmd = 'rmdir '
        if self.s.shelltype == 'vxworks':
            self.rmdir_cmd = 'file remove '

        self.geterrnos()
        # cache some common errno strings for convenient access
        for e in ['EACCES',
                  'EADDRINUSE',
                  'EADDRNOTAVAIL',
                  'EAGAIN',
                  'EALREADY',
                  'EBADF',
                  'EBUSY',
                  'ECONNABORTED',
                  'ECONNREFUSED',
                  'ECONNRESET',
                  'EDESTADDRREQ',
                  'EEXIST',
                  'EHOSTUNREACH',
                  'EINPROGRESS',
                  'EINVAL',
                  'EISCONN',
                  'EMSGSIZE',
                  'ENETDOWN',
                  'ENETUNREACH',
                  'ENOMEM',
                  'ENOSYS',
                  'ENOTCONN',
                  'ENOTSUP',
                  'ENXIO',
                  'EOPNOTSUPP',
                  'ESHUTDOWN',
                  'ESRCH',
                  'ETIMEDOUT',
                  'EWOULDBLOCK']:
            setattr(self, e, self.s.errnos[e]);

    # core functions using the session's pexpect spawn
    def send(self, cmd, newline = True, sudo = True):
        '''just send with newline, this should be followed with waiting for the prompt
        (calls pexpect)'''
        #print '--- send   %s %s %s' % (time.time(), threading.current_thread(), cmd)
        self.s.send(cmd, newline, sudo)
        
        return cmd

    def expect(self, cmd, timeout = -1):
        '''Dont use this directly, use expect_re or expect_exact
        (calls pexpect)'''
        def log_command_output():
            self.s.log('\n' + self.s.name + '>' + (str(self.s.s.before) + str(self.s.s.after)).replace('\r',''))
            #self.s.log.flush()
        
        #print '--- expect %s %s %s' % (time.time(), threading.current_thread(), cmd)
           
        prompt = re.escape(self.s.prompt)
        if (isinstance(cmd, list) and prompt in cmd) or cmd == prompt:
            # Receive the prompt from the target is one of the acceptable outcomes
            i = self.s.s.expect(cmd, timeout)
            #print '--- expect before:%s' % self.s.s.before
            #print '--- expect after :%s' % self.s.s.after
            #print '\n\n'
            log_command_output()
            return i

        # else: receiving the prompt without seeing any of the specified outcomes
        # is an error condition and will result in a failed test case
        if isinstance(cmd, list):
            ls = [prompt] + cmd
        else:
            ls = [prompt, cmd]

        i = self.s.s.expect(ls, timeout)
        #print '--- expect before:%s' % self.s.s.before
        #print '--- expect after :%s' % self.s.s.after
        #print '\n\n'        
        log_command_output()

        if i == 0:
            s = '''\ntarget: "%s" got prompt instead of expected "%s".
            Command run and what was returned:
            "%s"''' % (self.s.name, cmd, self.s.s.before.replace('\r',''))
            self.s.log(s)
            raise test_fail(s)
        return i - 1


    # fluff (i.e. helper functions previously expanded in test cases)
    def send_and_wait_prompt(self, s):
        "Discard result"
        self.send(s)
        self.wait_prompt()

    def expect_re(self, cmd, timeout = -1):
        '''
        Parse incoming stream with Regular Expressions, leave rest of instream untouched.
        Only eats prompts on failure.
        timeout = -1 will use self.s.s.timeout
        '''
        return self.expect(cmd, timeout)

    def expect_exact(self, cmd, timeout = -1):
        'just like expect_re() but uses plain text instead of a regular expression'
        if isinstance(cmd, list):
            ecmd = [re.escape(t) for t in cmd]
        else:
            ecmd = [re.escape(cmd)]
        return self.expect(ecmd, timeout)


    def expect_re_and_wait_prompt(self, *a,**k):
        'like expect_re() but waits for prompt after the matching was successful'
        r = self.expect_re(*a,**k)
        self.wait_prompt()
        return r


    def expect_exact_and_wait_prompt(self, *a,**k):
        'like expect_exact() but waits for prompt after the matching was successful'
        r = self.expect_exact(*a,**k)
        self.wait_prompt()
        return r


    def expect_get(self, cmd, timeout = -1, eat_prompt = True):
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
            #prompt gone
            raise test_fail('prompt reached instead of \n"%s"\nstuff after: "%s"' % (cmd, self.s.s.before))

        i = i - 1 #same numbering as before insertion of prompt
        matches = self.s.s.match #save this before running wait_prompt which removes it
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


    def wait_prompt(self, timeout = -1, cleanup = False):
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
            self.expect_exact(self.s.prompt, timeout)
        except pexpect.TIMEOUT:
            if not cleanup:
                self.s.log('%s never returned the prompt (%s)' % (self.s.name, self.s.s.before))
                raise
        #try: # not a good fix!
        #    self.expect_exact(self.s.prompt, timeout=2)
        #except pexpect.TIMEOUT:
        #    pass


    def expect_prompt(self, cmd0, timeout = -1, cleanup=False):
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


    def wait_prompt_not(self, bad, timeout = -1):
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
            self.s.log("got    : " + str(ls[i]) + re.sub('[\r\n\ ]', '', self.s.s.before), True)
            self.s.log("wanted just a prompt. ", True)
            raise test_fail('wait_prompt_not: %s got unexpected: "%s"' % (self.s.name, ls[i]))


    def expect_not(self, bad, timeout = 1):
        '''Waits for a second and returns happily unless "bad" arrives.
        The prompt must not show up.'''
        ls = [pexpect.TIMEOUT, bad]
        if isinstance(bad, list):
            ls = [pexpect.TIMEOUT] + bad
        i = self.expect_re(ls, timeout)
        if i != 0:
            raise test_fail('expect_not: %s got unexpected "%s"' % (self.s.name, ls[i]))


    def send_and_return_all(self, cmd, newline = True, strip_lines=True, wait_timeout = -1, custom_prompt=None):
        '''
        "cmd" is sent to the shell with a "newline" appended.
        A list of lines is returned as result. All lines are stripped
        of leading/ending whitespace if "strip_lines".
        (uses pexpect)
        '''
        cmd = cmd.strip()
        self.send(cmd,newline)

        if custom_prompt:
            # Change to custom prompt
            original_prompt = self.s.prompt
            self.s.prompt = custom_prompt

        self.wait_prompt(timeout=wait_timeout)

        if custom_prompt:
            # Restore original prompt
            self.s.prompt = original_prompt

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


    def send_and_return_all_by_timeout(self, cmd, cmd_timeout=30, strip_lines=True):
        '''
        "cmd" is sent to the shell with a "newline" appended.
        A list of lines is returned as result after cmd_timeout seconds. 
        All lines are not stripped.
        This funtion is used for the command without any returned prompt/flag, like "route monitor"
        '''
        if pexpect.__version__ not in ('0.999', '4.2.1'):
            if pexpect.__version__ < '4.2.1':
                raise config_error('pexpect 0.999 or 4.2.1 are only supported. Your pexpect version is %s' % pexpect.__version__)
        logfile = '/tmp/pexpect_log'
        magic_start = 'start_magic_magic_start'
        magic_stop = 'stop_magic_magic_stop'

        # save pexpect config
        old_timeout = self.s.s.timeout
        if pexpect.__version__ == '0.999':
            old_logfile = self.s.s.log_file
        elif pexpect.__version__ >= '4.2.1':
            old_logfile = self.s.s.logfile
            
        self.s.s.timeout = cmd_timeout + 10
        
        with open(logfile, 'w') as fdw:
            if pexpect.__version__ == '0.999':
                self.s.s.log_file = fdw
            elif pexpect.__version__ >= '4.2.1':
                self.s.s.logfile = fdw
    
            self.s.s.send('echo ' + magic_start + '\n')
            self.s.s.expect(magic_start)
            
            self.s.s.send(cmd + '\n')
            time.sleep(cmd_timeout)
            
            self.s.s.send('echo ' + magic_stop + '\n')
            self.s.s.expect(magic_stop)
    
        # restore pexpect config
        self.s.s.timeout = old_timeout
        if pexpect.__version__ == '0.999':
            self.s.s.log_file = old_logfile
        elif pexpect.__version__ >= '4.2.1':
            self.s.s.logfile = old_logfile
        
        with open(logfile, 'r') as fdr:
            content = fdr.read()
        
        getoutput('rm -f %s' % logfile)
        
        # different version pexpects return slightly different results
        if pexpect.__version__ == '0.999':
            ptn = '(?s)%s\s*(.*?)%s' % (self.s.prompt + cmd, 'echo ' + magic_stop)
        elif pexpect.__version__ >= '4.2.1':
            ptn = '(?s)%s\s*(.*?)%s' % ('\n' + cmd, 'echo ' + magic_stop)
        found = re.search(ptn, content)
        if found is not None:
            content = found.groups()[0].replace(magic_start, '').replace('echo ', '').strip()
            if strip_lines:
                return map(lambda line: line.strip(), content.split('\n'))
            else:
                return map(lambda line: line, content.split('\n'))
        else:
            return []        


    def return_all(self, strip_lines=True, wait_timeout = -1):
        '''
        A list of lines is returned as result. All lines are stripped
        of leading/ending whitespace if "strip_lines".
        (uses pexpect)
        '''
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
        print 'shell_ops : send Ctrl+C'
        self.s.s.send('\003')  # send ctrl+c to target
        self.s.s.expect(self.s.prompt)
    
    def send_ctrl_right_square_bracket(self):
        # send CTRL+]
        #print 'shell_ops : send Ctrl+]'
        self.s.s.send('\x1d')  # send ctrl+] to target
    
    def geterrnos(self):
        if self.s.shelltype == 'vxworks' or self.s.shelltype == 'ipcom':
            # Do not modify the defaults
            self.s.errnos = self.s.errnos.copy()
            pat = re.compile("(E[A-Z]+) (.*)$")
            for line in self.send_and_return_all('errnos', wait_timeout = 5):
                m = pat.match(line)
                if m:
                    errno, errstr = m.groups()
                    self.s.errnos[errno] = errstr


################################################################################
class custom_command(shell_ops):
    def __init__(self, s, ts):
        shell_ops.__init__(self, s)
        self.ts = ts
        self.prompt_pushed = False
        self._logged_in = False

    def push_prompt(self, p):
        self.old = self.s.prompt
        self.s.prompt = p
        self.prompt_pushed = True

    def pop_prompt(self):
        self.s.prompt = self.old
        self.prompt_pushed = False

    def logged_in(self):
        self._logged_in = True
        self.ts.custom_cmds.append(self)

    def logged_out(self):
        self._logged_in = False
        if self in self.ts.custom_cmds:
            del self.ts.custom_cmds[self.ts.custom_cmds.index(self)]


################################################################################
class proxy(object):
    '''These proxies are passed as "hosts" to the test() function.
    Each instance is another login to the target.'''
    def __init__(self, session_class, target_ops_class, target_state, s_args):
        self.__dict__['sc'] = session_class
        self.__dict__['tc'] = target_ops_class
        self.__dict__['ts'] = target_state
        self.__dict__['s_args'] = s_args
        #print '=== proxy.__init__ session_class:%s, target_ops_class:%s' % (self.sc, self.tc)
        s = session_class(**s_args)
        s.login()
        self.__dict__['s'] = s
        target_state.sessions.append(s)
        shops = shell_ops(s)
        self.__dict__['shops'] = shops
        tops = target_ops_class(shops, target_state)
        self.__dict__['tops'] = tops


    def custom_cmd(self, cls):
        class mixin(cls, custom_command):
            def __init__(self, s, ts):
                custom_command.__init__(self, s, ts)

        s = mixin(self.s, self.ts)
        if not hasattr(s, 'logout'):
            raise config_error('%s misses a logout function' % cls.__name__)
        s.login()
        return s


    def login(self):
        "Returns a second shell on the same target"
        s_args2 = self.s_args.copy()
        s_args2['relogin'] = True # (ugly hack to be removed)
        return proxy(self.sc, self.tc, self.ts, s_args2)


    def ipcom_shell(self, force_telnet = True):
        """Always returns an ipcom shell. this is needed for the
        socktest commands and anything ipcom-shell-specific.
        If you test linux/lkm, you need to have an ipout running,
        compiled with native stack. (i.e. ipcom without ipnet/iplite)
        The alternative to telnet is ssh."""
        if issubclass(self.tc, iptarget) or not force_telnet:
            return proxy(self.sc, ipcom_shell, self.ts,
                         self.s_args)

        s_args2 = self.s_args.copy()
        if self.type == 'fos_telnet':
            s_args2['port'] = 2324
        else:
            s_args2['port'] = 2323

        return proxy(telnet, ipcom_shell, self.ts, s_args2)

    def ipcom_nae(self, core):
        """Always returns an ipcom shell. this is needed for the
        socktest commands and anything ipcom-shell-specific.
        If you test linux/lkm, you need to have an ipout running,
        compiled with native stack. (i.e. ipcom without ipnet/iplite)
        The alternative to telnet is ssh."""

        vswitch = self.fos_vswitch[0]

        s_args2 = vswitch.s_args.copy()
        s_args2['port'] = 2323 + core
        s_args2['addr'] = self.s_args['addr']
        return proxy(telnet, ipcom_shell, vswitch.ts, s_args2)

    def __getattr__(self, x):
        if hasattr(self.shops, x):
            return getattr(self.shops, x) #hit step in pdb
        return getattr(self.tops, x) #hit step in pdb


    def _cleanup(self):
        '''this is only run by main(). meaning, it is run once per proxy Made Before Test Start.
        do NOT call any objects which use a proxy inside self.t.cleanup()'''
        self.s.log('cleaning up')
        #print '=== proxy : _cleanup()\n\n'
        while self.ts.sockets:
            safe(self.ts.sockets[0].close, cleanup = True)

        self.tops.cleanup()
        l = list(self.ts.netifs)
        for n in l:
            safe(n.destroy, cleanup=True)

        self.tops.cleanup2()
        while self.ts.custom_cmds:
            safe(self.ts.custom_cmds.pop().logout)

        while self.ts.sessions:
            safe(self.ts.sessions.pop().logout)
        self.s.log('cleanup done')


    def logout(self):
        "only needed if you know you would run out of number of allowed logins on the target"
        del self.ts.sessions[self.ts.sessions.index(self.s)]
        self.shops.s.logout()


    def pre_clean(self):
        #TODO: Ugly hack to avoid socktest on freebsd
        if self.tops.target_os_name != 'freebsd':
            try:
                s = self.ipcom_shell()
                s.send_and_wait_prompt('socktest flush')
                #s.send_and_wait_prompt('ttcp -t -n 1 localhost') # only works with ipappl. use 127.0.0.1?
                s.send_and_wait_prompt('ttcp -t -n 1 127.0.0.1') # only works with ipappl. use 127.0.0.1?
                s.logout()
            except: #!!!todo insert real exception
                pass


################################################################################
class engine_state(object):
    # engine state/bookkeeping
    # Only keep 1 global all the time (singleton)
    # This is so different targets dont select the same IP to add to an interface for example.
    def __init__(self):
        self.ip_count = 1
        self.net_count = 1
        self.ip_count6 = 1
        self.net_count6 = 1
        self.ips = {} #keep track of what ips have been used so we can alloc new ones.
        self.vlan_range = (3, 4094) #vlans_used = []
        self.vlan_count = 3


    def alloc_ip(self, v6='', net = None, addr = None, prefixlen=None):
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
            parts[index]     = str(self.ip_count6)

            #s = '%s:%X:%X' % (abnet6, net, self.ip_count6) #(2000:ln)::net:hostid
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
        addr=ip(addr)
        if addr in self.ips and self.ips[addr] > 1:
            self.ips[addr] = self.ips[addr] - 1
        else:
            self.ips.pop(addr)


    def alloc_vlan(self):
        self.vlan_count +=1
        if self.vlan_count > self.vlan_range[1]:
            self.vlan_count = self.vlan_range[0]
        return self.vlan_count


################################################################################
class target_state(object):
    '''Pure bookkeeping for state restoration of each target.
    No usage of pexpect here'''
    def __init__(self):
        self.sessions = []
        self.custom_cmds = []
        self.default_route = None
        self.routes = []
        self.arps = {} # (ip, mac, devname, vr)
        self.vrs = []
        self.sockets = []
        self.netifs = []
        self.ports = {}
        self.procs = {}
        self.primary_ip = None
        self.primary_ip6 = None
        self.state_restorers = []
        self.las_prefix = ''

    def add_vr(self, nr):
        self.vrs.append(nr)

    def del_vr(self, nr):
        self.vrs.remove(nr)

    def add_route(self, x):
        self.routes.append(x)

    def del_route(self, t):
        (dst,gw,dev,vr,family) = t
        if t in self.routes:
            self.routes.remove(t)
        else:
            for r in self.routes:
                if dst.addr == r[0].addr:
                    self.routes.remove(r)
                    return
            raise '%s not in list %s' % (dst, self.routes)

    def del_arps(self, vr):
        newarps = {}
        for a in self.arps.keys():
            (ip, mac, dev, v) = a
            if vr != v:
                newarps[a]=True
        self.arps = newarps

    def del_arp(self, x):
        try:
            self.arps.pop(x)
        except KeyError, msg:
            print "tried del", x
            print "had", self.arps
            raise


################################################################################
def netmask_to_prefixlen(m):
    d = {255:8, 0:0, 128:1, 128+64:2, 128+64+32:3, 128+64+32+16:4, 128+64+32+16+8:5, 128+64+32+16+8+4:6, 128+64+32+16+8+4+2:7}
    return sum([d[int(x)] for x in m.split(".")])


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

        if hasattr(addr, 'ip') and callable(addr.ip):
            #it's actually a host
            addr = addr.ip()

        if isinstance(addr, ip):
            self._addr = addr._addr
            self.prefixlen = addr.prefixlen
            self.v6 = addr.v6
            self.scope = addr.scope
            self._addrstr = addr._addrstr
            return

        if addr == 'localhost': #v6?
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
            ls = self._addr[middle+1:].split('.')
            ls = hex(int(ls[0])*256 + int(ls[1]))[2:] + ":" + hex(int(ls[2])*256 + int(ls[3]))[2:]
            self._addr = firsthalf + ":" + ls

        import socket
        family = IF(self.v6, socket.AF_INET6, socket.AF_INET)
        self._addrstr = socket.inet_ntop(family, socket.inet_pton(family, self._addr))

        def _tolist(s):
            if self.v6:
                if s == '::':
                    return [0]*8
                ls = s.split(':')
                if '::' not in s:
                    return [int(x,16) for x in ls]
                if s.startswith('::'):
                    ls = ls[1:]
                elif s.endswith('::'):
                    ls = ls[:-1]
                n = len(ls)-1
                pos = ls.index('')
                ls = ls[:pos] + ["0"]*(8-n) + ls[pos+1:]
                return [int(x,16) for x in ls]
            else: #v4
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

#     def _uniform(addr):
#         import socket
#         family = IF(addr.v6, socket.AF_INET6, socket.AF_INET)
#         return socket.inet_ntop(family, socket.inet_pton(family, addr._addrstr))
#     _uniform = staticmethod(_uniform)

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
        else: #prefixlen v6
            p = pfx = netmask_or_prefixlen
            nm = []
            while p > 0:
                nm.append((0xffff << (16-min(p,16))) & 0xffff)
                p -= 16
            nm = nm + [0]*(8 - len(nm))

        r = ip(self)
        r._addr = [a & b for a,b in zip(self._addr, nm)]
        r.prefixlen = pfx
        return r


    def broadcast(self, netmask_or_prefixlen):
        #!!! copy of mask() above. merge!
        def nm4str_to_nm(n):
            return [int(x) for x in n.split('.')]

        if isinstance(netmask_or_prefixlen, str):
            nm = nm4str_to_nm(netmask_or_prefixlen)
            pfx = netmask_to_prefixlen(netmask_or_prefixlen)
        elif not self.v6:
            nm = nm4str_to_nm(prefixlen_to_netmask(netmask_or_prefixlen))
            pfx = netmask_or_prefixlen
        else: #prefixlen v6
            p = pfx = netmask_or_prefixlen
            nm = []
            while p > 0:
                nm.append((0xffff << (16-min(p,16))) & 0xffff)
                p -= 16
            nm = nm + [0]*(8 - len(nm))

        r = ip(self)
        r._addr = [a | (~b & 0xff) for a,b in zip(self._addr, nm)]
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
        return '.'.join( [str(x) for x in self._addr] )
        
################################################################################
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
        netif.tun_count +=1
        #if netif.tun_count > netif.tun_range[1]:
        #    netif.tun_count = netif.tun_range[0]
        return netif.tun_count
    alloc_tun = staticmethod(alloc_tun)

    mpls_count = 0

    def alloc_mpls():
        netif.mpls_count +=1
        #if netif.mpls_count > netif.mpls_range[1]:
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
        if vr == None:
            vr = self.vr
        return self.t.las_prefix(vr)


    def from_existing(self, ifname, vr, addrs, mac, linktype, tunnel_local_ip = None,  tunnel_remote_ip = None,  tunnel_ttl = None):
        self.ifname = ifname
        self.vr = vr
        self.t.ts.netifs.append(self)
        self.addrs = addrs
        self.dont_remove_ips = dict(addrs)
        self.isup = vr == 0 #!!! wrong
        self.dont_destroy_me = True
        self.linktype = linktype # eth, loopback, vlan, tunnel
        self.local_ip = tunnel_local_ip
        self.remote_ip = tunnel_remote_ip
        self.tunnel_ttl = tunnel_ttl
        self.mac = mac
        for a in addrs:
            es.alloc_ip(addr=a)


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


    def new(self, addr = None, vr = 0, up = True,
            ifname = None, #only allowed for ipnet (if you want to specify a specific ifname)
            vlan = False, vlan_parent_netif = None,
            pppoe = False, pppoe_parent_netif = None,
            tunnel = False, tunnel_local_ip = None,  tunnel_remote_ip = None,  tunnel_ttl = None,
            mpls = False, mpls_key = None):
        '''vlan = ("new",  parent_netif) -> allocs new vlan id. number -> use this number. number may not be 0.
        tunnel = (ip|gre|min, local_ip, remote_ip, ttl)
        addr = None/"new"/ip[/prefixlen]
        '''
        self.mac = None
        self.isup = False
        if vlan:
            self.parent_netif = self.t._get_dev(vlan_parent_netif)
            self.mac = self.parent_netif.mac
        elif pppoe:
            self.parent_netif = self.t._get_dev(pppoe_parent_netif)

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

        #make a name
        if ifname:
            self.ifname = ifname
        else:
            if vlan:
                self.ifname = 'vlan'
                def is_ifname_taken(num):
                    for iff in self.t.ts.netifs:
                        if iff.vr == self.vr and iff.ifname == self.ifname + str(num):
                            return True
                    return False
                num = self.id #preferrably if possible
                while is_ifname_taken(num):
                    num += 1
                self.ifname += str(num) #!!!wont work on linux
            elif tunnel:
                #tuntype, local_ip, remote_ip, ttl = tunnel
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

        #create
        try:
            if self.linktype == 'mpls': #subclass?
                self.t.sh.expect_prompt(self.las_prefix() + 'mplsctl -a -I %s' % self.ifname)
                self.t.sh.expect_prompt(self.las_prefix() + 'mplsctl -b -I %s -n %s' % (self.ifname, self.mpls_key))
                if self.vr:
                    self.set_vr(self.vr)
            else:
                self._create()
        except:
            raise
        self.t.ts.netifs.append(self)

        #make type
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
            elif isinstance(addr,str) and addr == 'new':
                self.add_ip(up=False)
            #elif isinstance(addr, ip):
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
            safe(self.del_ip, addrs.pop(), cleanup = cleanup)
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


    def set_vlan(self, vlan, live = False):
        "if live = True, change vlan id tag on the fly without bringing it down first"
        wasup = self.isup
        if not live:
            self.down()
        self._set_vlan(vlan)
        if not live and self.wasup:
            self.up()


    def get_link_addr(self):
        raise test_fail('Must be implemented by subclass since it is target type specific')


    def add_ip(self, addr = None, v6='', net = None, up = True, tentative = False, cga = False, primary = False):
        """
        To primary ethernet test netif
        addr = None will allocate a new, previously unused ip-address. ipv6 if v6 != ''
        net = one of [1..254], to add the new ip to another subnet
        up: change to make the netif Not go up (if it already isn't)
        """
        #!!!todo add cleanup option
        if addr:
            addr = es.alloc_ip(addr=addr)
        else:
            addr = es.alloc_ip(v6, net)

        try:
            self._add_ip(addr, tentative, cga, primary)
            time.sleep(0.3)  # add ti avoid test_fail: expect_prompt: linux wanted nothing. got: "['sudo ip link set vlan5 up']"
        except:
            es.free_ip(addr)
            raise

        self.addrs[addr] = True #!!! +=1?
        if up:
            self.up()

        return addr


    def del_ip(self, addr, cleanup = False):
        addr=ip(addr)
        es.free_ip(addr)
        self.addrs.pop(addr)
        try:
            self._del_ip(addr)
        except TIMEOUT:
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
        self.t.sh.expect_prompt(s,cleanup)

    def _set_vlan(self):
        vr = IF(self.vr, "-V %s " % self.vr, "")
        parentvr = IF(self.vr != 0, "#%s" % self.parent_netif.vr, "")
        self.t.sh.expect_prompt('ifconfig %s%s vlan %s vlanif %s%s' % (vr, self.ifname, self.id, self.parent_netif.ifname, parentvr))
        # set mtu to 1496
        self.mtu('1496')


    def _make_tun(self):
        vr = IF(self.vr,"-V %s "%self.vr,'')
        self.t.sh.expect_prompt('ifconfig %s%s inet%s tunnel %s %s'
                                % (vr,
                                   self.ifname,
                                   self.local_ip.v6,
                                   self.local_ip.addr,
                                   self.remote_ip.addr))

        if self.ifname.find("gremin") != -1:
            self.t.sh.expect_prompt('ifconfig %s%s link0' % (vr, self.ifname))

    def _make_pppoe(self):
        vr = IF(self.vr,"-V %s "%self.vr,'')
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
        vr = IF(self.vr,"-V %s "%self.vr,'')
        t = IF(tentative, ' tentative', self.nodad_str(addr.v6))
        c = IF(cga, ' cga', '')
        a = IF(primary, '', 'add ')
        self.t.sh.expect_prompt('ifconfig %s%s inet%s %s%s%s%s' % (vr, self.ifname, addr.v6, a, addr, t, c))
        return addr

    def _del_ip(self, addr):
        vr = IF(self.vr,"-V %s "%self.vr,'')
        self.t.sh.expect_prompt('ifconfig %s%s inet%s delete %s' % (vr, self.ifname, addr.v6, addr))

    def up(self, cleanup=False, _state='up'):
        if self.isup and _state=='up':
            return
        vr = IF(self.vr,"-V %s "%self.vr,'')
        self.t.sh.expect_prompt('ifconfig %s%s %s' % (vr, self.ifname, _state))
        self.isup = _state=='up'

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
            m = re.match('.*?MTU:(\d+) ', line)
            if m:
                return m.group(1)
        raise engine_error('Cannot determine MTU for %s' % self.ifname)

    def get_link_addr(self):
        "returns link address of interface"
        for line in self.t.sh.send_and_return_all('ifconfig %s%s' %
                                                  (IF(self.vr, '-V %s ' % self.vr, ''),
                                                   self.ifname)):
            m = re.match('.*HWaddr (\S+)', line)
            if m:
                return m.group(1)
        return ''


class netif_ipnet(netif_iptarget):
    pass

class netif_iplite(netif_iptarget):
    pass


class netif_lkm(netif):
    def _create(self):
        #!!! ip(iproute2) or ifconfig(sys-apps/net-tools)
        if self.linktype == 'vlan':
            self.t.sh.send('vconfig add %s %s' % (self.parent_netif.ifname, self.id))
            i = self.t.sh.expect_exact(['Added VLAN with VID == %s to IF -:%s:-' % (self.id, self.parent_netif.ifname),
                                     'WARNING',
                                     'ERROR'])
            self.t.sh.wait_prompt(timeout=30)

            if i != 0:# and not self.s.dry:
                raise test_fail('add vlan: %s' % i)

            self.t.sh.expect_prompt(self.las_prefix(vr=0) + 'ip link set dev vlan%s name %s' % (self.id, self.ifname))

            # Always created in vr 0
            vr = self.vr
            self.vr = 0
            self.set_vr(vr)

            # set mtu to 1496
            self.mtu('1496')

        elif self.linktype == 'tunnel':
            s = self.las_prefix() + 'ifconfig %s create' % (self.ifname)
            self.t.sh.expect_prompt(s)



    def _destroy(self, cleanup):
        if self.linktype == 'vlan':
            #all = self.t.sh.send_and_return_all('vconfig rem ' + self.ifname)
            chvr = IF(self.vr, self.las_prefix() + 'chvr -n %s ' % self.vr, '')
            self.t.sh.send(chvr + 'vconfig rem ' + self.ifname)
            if not cleanup:
                self.t.sh.expect_exact('Removed VLAN -:%s:-' % self.ifname)
            self.t.sh.wait_prompt(timeout=30)

        elif self.linktype == 'tunnel':
            s = self.las_prefix() + 'ifconfig %s destroy' % (self.ifname)
            self.t.sh.expect_prompt(s,cleanup)
        else:
            raise ''


    def _set_vlan(self):
        pass # not possible on linux to change vlan id after creation


    def _make_tun(self):
        self.t.sh.expect_prompt(self.las_prefix() + 'ifconfig %s inet%s tunnel %s %s'
                                % (self.ifname, self.local_ip.v6, self.local_ip.addr, self.remote_ip.addr))
        if self.ifname.find("gremin") != -1:
            self.t.sh.expect_prompt(self.las_prefix() + 'ifconfig %s link0' % (self.ifname))


    def up(self, cleanup=False, _state='up'):
        s = self.las_prefix() + 'ip link set %s %s' % (self.ifname, _state)
        self.t.sh.expect_prompt(s,cleanup)
        self.isup = _state=='up'


    def down(self, cleanup=False):
        if not self.isup:
            return
        self.up(cleanup, _state='down')


    def _create_iproute_cmd(self, cmd):
        'Creates the full command line from a iproute2 command'
        return self.las_prefix() + 'ip ' + cmd


    def _set_vr(self, vr):
        self.t.sh.expect_prompt(self._create_iproute_cmd('vr change vr %s dev %s %s' % (self.vr, self.ifname, vr)))


    def get_link_addr(self):
        "returns link address of interface"
        for line in self.t.sh.send_and_return_all(self.las_prefix() + 'ifconfig %s' % self.ifname):
            m = re.match('.*HWaddr (\S+)\s', line)
            if m:
                return m.group(1)
        return ''


    def _add_ip(self, addr, tentative, cga, primary):
        if ip(addr).v6:
            self.t.sh.expect_prompt(self._create_iproute_cmd('addr add %s dev %s' % (addr, self.ifname)))
        else:
            self.t.sh.expect_prompt(self._create_iproute_cmd('addr add %s broadcast + dev %s' % (addr, self.ifname)))
        return addr


    def _del_ip(self, addr):
        self.t.sh.expect_prompt(self._create_iproute_cmd('addr del %s dev %s' % (addr, self.ifname)))


    def mtu(self, new_mtu):
        'set interface MTU'
        self.t.sh.expect_prompt(self._create_iproute_cmd('link set %s mtu %s' % (self.ifname, new_mtu)))


    def get_mtu(self):
        'get the current interface MTU'
        for line in self.t.sh.send_and_return_all(self._create_iproute_cmd('link show %s' % self.ifname)):
            m = re.match('.*? mtu (\d+) ', line)
            if m:
                return m.group(1)
        raise engine_error('Cannot determine MTU for %s' % self.ifname)


class netif_freebsd(netif):

    def _create(self):
        s = 'ifconfig %s create' % (self.ifname)
        self.t.sh.expect_prompt(s)

    def _destroy(self, cleanup):
        s = 'ifconfig %s%s destroy' % (self.ifname)
        self.t.sh.expect_prompt(s,cleanup)

    def _set_vlan(self):
        self.t.sh.expect_prompt('ifconfig %s vlan %s vlanif %s' % (self.ifname, self.id, self.parent_netif.ifname))
        # set mtu to 1496
        self.mtu('1496')

    def _make_tun(self):
        pass
    def up(self, cleanup=False, _state='up'):
        pass
    def down(self, cleanup=False):
        pass
    def _set_vr(self, vr):
        pass
    def get_link_addr(self):
        "returns link address of interface"
        for line in self.t.sh.send_and_return_all(self.las_prefix() + 'ifconfig %s' % self.ifname):
            m = re.match('.*HWaddr (\S+)\s', line)
            if m:
                return m.group(1)
        return ''

    def _add_ip(self, addr, tentative, cga, primary):
        print "Adding IP %s" % addr
        self.t.sh.expect_prompt('ifconfig %s add %s' % (self.ifname, addr))
        return addr

    def _del_ip(self, addr):
        print "DEELKTING IP %s" % addr
        self.t.sh.expect_prompt('ifconfig %s delete %s' % (self.ifname, addr))


    def _add_ip(self, addr, tentative, cga, primary):
        pass

    def _del_ip(self, addr):
        pass

    def mtu(self, new_mtu):
        pass

    def get_mtu(self):
        pass



################################################################################
#                       target superclass
#                    _                       _
#                   | |_ __ _ _ __ __ _  ___| |_
#                   | __/ _` | '__/ _` |/ _ \ __|
#                   | || (_| | | | (_| |  __/ |_
#                    \__\__,_|_|  \__, |\___|\__|
#                                 |___/
################################################################################
class target(object):
    '''Base class for all test targets. Make no direct instances of this class.
    Only one instance per target is allowed. The proxy will be used for multiple
    logins to the same target.'''
    #__metaclass__ = trace_metaclass

    def __init__(self, shops, ts):
        #no self.s exists at this point
        self.ts = ts
        self.sh = shops
        self.fips_state_restorer_pushed = False

    def init(self, opt):
        'this should only be run once per target_state'
        self.opt = opt
        self.flush_ipsec()

        self.versions = self.sh.send_and_return_all('ipversion')
        self.ipv4 = self.check_ip_v4()
        self.ipv6 = self.check_ip_v6()
        self.is_head = self.ipversion_is_head()

        self.ts.default_route = self.get_route('default', exp_gw = True).get('gw')
        if self.ts.default_route:
            self.del_route('default', accounting=False)
        self.ts.netifs = self._create_ifs_from_existing()


    def check_ip_v4(self):
        route = self.sh.send_and_return_all('ping')
        return re.match(r"(.*Unknown command: |Cmd: '\w+' not found)", route[0]) == None


    def check_ip_v6(self):
        route = self.sh.send_and_return_all('ping6')
        return re.match(r"(.*Unknown command: |Cmd: '\w+' not found)", route[0]) == None


    def las_prefix(self, vr=0):
        'Return the prefix for all LAS shell commands, subclasses may override this method'
        return ''

    def target_prefix(self):
        'Return the prefix for all TARGET shell commands, subclasses may override this method'
        return self.target_prefix

    def target_access(self):
        'Return the access for all TARGET access commands, subclasses may override this method'
        return self.target_access


    def version_gte(self, product_arg, ver_arg):
        try:
            return self.version_gte_b(product_arg, ver_arg)
        except:
            return True


    def version_gte_b(self, product_arg, ver_arg):
        'is the running ipnet version greater or equal to 6.5.0.9?'
        for version_line in self.versions:
            m = re.match('@\(#\) (.*?) \$Name', version_line)
            if m:
                product_name = m.group(1)
                if product_name.lower() == product_arg.lower():
                    v = re.match('.+?\$Name: .+?[rp]([\d_]+)', version_line)
                    if not v:
                        # Probably the CVS version, treat as newest version available
                        return True
                    v = v.group(1)
                    #6_5_0_9
                    return [int(x) for x in ver_arg.split('.')] <= [int(x) for x in v.split('_')]
        #product_arg not found
        return True

    def ipversion_is_head(self):
        for version_line in self.versions:
            if version_line.find('IPCOM $Name: HEAD') >= 0:
                return True
        return False

    def push_state_restorer(self, func, args):
        'Stores a function and its argument that will restore the target to the current state'
        self.ts.state_restorers.append((func, args))


    def cleanup(self):
        '''cleanup
        The order of things here is important.
        Removing IPs removes arp entries on the same net for example.
        '''

        while len(self.ts.state_restorers) > 0:
            (func, args) = self.ts.state_restorers.pop()
            safe(func(*args))

        while self.ts.arps:
            ((ip2,mac,dev,vr),_) = self.ts.arps.popitem()
            self.ts.arps[(ip2,mac,dev,vr)] = True
            safe(self.del_arp, ip2,mac,dev,vr, cleanup = cleanup)

        while self.ts.routes:
            (dst, gw, dev, vr, family) = self.ts.routes[0]
            safe(self.del_route, dst, gw, dev, vr, family, cleanup=True)


        if self.ts.default_route:
            safe(self.add_route, 'default', self.ts.default_route, accounting = False, cleanup = True)

        if True: #!!!todo not self.opt['fast']:
            for (p, vr) in self.ts.procs:
                if self.ts.procs[(p, vr)] == self.ts.procs_copy.get((p, vr), 'killed'):
                    continue
                if self.ts.procs_copy.get((p, vr),'killed') == 'started':
                    safe(self.start_proc, p, vr = vr, cleanup=True)
                else:
                    safe(self.stop_proc, p, vr = vr, cleanup=True)


    def cleanup2(self):
        while self.ts.vrs:
            safe(self.del_vr, self.ts.vrs[0], cleanup=True)


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

    def _add_netif_from_existing(self, *a, **k):
        x = self._create_netif()
        x.from_existing(*a, **k)
        return x


    def add_vlan(self, *a, **k):
        "shortcut for add_netif() with 'vlan' = 'new'"
        if not 'vlan' in k:
            k['vlan'] = 'new'
        return self.add_netif(*a, **k)


    def _intern_add_del_route(self, dst, gw, dev):
        if gw:
            gw=ip(gw)
        if dst == 'default':
            if gw and gw.v6:
                dst  = '::/0'
            else:
                dst = '0.0.0.0/0'
        dst=ip(dst)
        if dev:
            dev = self._get_dev(dev)
        return dst, gw, dev


    def add_route(self, dst, gw='', dev='', vr='', family='',
        cloning='', succeed=True, reject=False, accounting=True,
        cleanup=False, mpls_key='', blackhole=False, hopcount=None, down=False):
        "gw can be 'default' or '0.0.0.0' for default."
        dst, gw, dev = self._intern_add_del_route(dst, gw, dev)
        self._add_del_route(dst, gw, dev, vr, family, True,  cleanup,
                            cloning, succeed, reject, accounting,
                            mpls_key, blackhole, hopcount, down)


    def del_route(self, dst, gw = '', dev = '', vr = '', family='', cleanup = False, accounting = True):
        dst, gw, dev = self._intern_add_del_route(dst, gw, dev)
        self._add_del_route(dst, gw, dev, vr, family, False, cleanup,
                            '', True, False,  accounting, '', False, None)


    def _get_devname(self, dev):
        if not dev:
            devname = self.netif().ifname
        elif isinstance(dev, netif):
            devname = dev.ifname
        else: #str
            devname = dev
        return devname


    def _get_dev(self, devname, vr = 0):
        'gets the first in the list, no matter vr'
        if not devname:
            return self.netif(vr=vr)
        if isinstance(devname, netif):
            return devname
        if '#' in devname:
            devname, vr = devname.split('#')
        for d in self.ts.netifs:
            if d.ifname == devname and d.vr == vr:
                return d
        raise engine_error('not found')


    #!!!! move to metaclass
    def trace(self, msg = ""):
        t = traceback.extract_stack(None,2)[0][2] + '()'
        t = self.s.name + '.' + t
        if msg:
            t += ": " + msg
        self.sh.s.log(t)
        return self.s.dry


    def ip(self, v6=''):
        if v6 == '6':
            return self.ts.primary_ip6
        else:
            return self.ts.primary_ip


    def login_ip(self):
        "the ip as seen in the hosts.py file"
        return self.sh.s.login_ip


    def netifs(self, linktype='all', vr='all'):
        "returns all netifs matching linktype and vr"
        ifs = []
        for n in self.ts.netifs:
            if linktype in (n.linktype, 'all') and vr in (n.vr, 'all'):
                ifs.append(n)
        return ifs


    def netif(self, linktype='eth', vr=0, nth_not_login=0):
        '''
        First network interface of a certain kind (linktype) is returned.
        linktype can be eth, loopback, vlan, tunnel, mpls, etc.
        nth_not_login returns the nth interface of type linktype which is not carrying the login_ip. 1 = 1st'''
        ifs = self.netifs(linktype, vr)
        if nth_not_login == 0:
            for n in ifs:
                if [x for x in n.addrs if self.login_ip() == x]: #self.s.login_ip in n.addrs?
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
                return non_login_ifs[nth_not_login -1]
        raise engine_error('Non-existant netif requested')


    def alloc_ip(self, *a, **k):
        """
        v6='', net = None, addr = None, prefixlen=None
        Reserve a previously unused ip address. If none is given,
        a new one will be given to you with the properties of net/prefixlen specified.
        The parts are 10.luckynumber.<net or latest used net>.ip_count

        """
        #this just propagates to engine_state
        return es.alloc_ip(*a, **k)


    def alloc_vlan(self):
        'acquire new unique vlan ids'
        return es.alloc_vlan()


    def add_ip(self, *a, **k):
        '''usually you run some_netif.add_ip().
        however, if you run sometarget.add_ip() youll put it on the first eth'''
        return self.netif('eth').add_ip(*a, **k)
        #!!! probably [0] = loopback, [1] = eth0, etc


    def del_ip(self, *a, **k):
        self.netif('eth').del_ip(*a, **k)


    def netstat_list(self, vr = ''):
        if vr:
            vr = '-V %s' % vr
        self.sh.send('netstat %s -an' % vr)
        self.sh.wait_prompt()


    def ping(self, dst, succeed = True,
             src='', packetsize=64, timeout=1,
             count=1, bypass_route='', vr='',
             icmp_replyer='', require_ipping=False, retries=1,
             dont_frag=False, exp_ip=False, ttl=64,
             tos=0, timestamp='', interval=1000,
             at_least=False, interface=None, prefer_temporary_src_addr=False,
             hops=[]):
        """
        dst = another host or ip
        exp_ip can be the ip of whom you expect to answer
        icmp_replyer = ip of whoever sends icmp errors
        """
        if isinstance(dst, proxy): #so you can a.ping(b)
            dst = dst.ip()
        else:
            dst = ip(dst)

        if src:
            src=ip(src)

        if exp_ip:
            exp_ip = ip(exp_ip)

        if not at_least:
            at_least = count

        if interface != None:
            ifname = interface.ifname
        else:
            ifname = ''

        self._ping(dst, succeed, src,
                   packetsize, timeout, count,
                   bypass_route, vr, icmp_replyer,
                   require_ipping, retries, dont_frag,
                   exp_ip, ttl, tos,
                   timestamp, interval, at_least,
                   ifname, prefer_temporary_src_addr, hops)


    def list_addr(self, domain = '', vr = 0, dev = None, temporary = True, tentative = True):
        return self._list_addr(domain, vr, dev, temporary, tentative)

    def _ping_retrier(self, cmd, should_succeed, possible_results, retries, dst):
        'Performs the native ping command. If success is expected, it retries up to <retries> times if needed.'
        for _ in range(retries):
            lines = "".join(self.sh.send_and_return_all(cmd))
            if should_succeed:
                match = re.search(possible_results[0], lines)
                if match and ip(match.group(1)).addr == ip(dst).addr:
                    return
            else:
                if re.search(possible_results[0], lines):
                    raise test_fail('ping: ping test failed.')
                return

            if retries > 1:
                time.sleep(1)
        ###none of the retries succeeded
        raise test_fail('ping: ping test failed.')


    def ftp_get(self, filename, user = None, passwd = None):
        if not user:
            user = self.ftp_user
        if not user:
            user = 'ftp'
        if not passwd:
            passwd = self.ftp_passwd
        if not passwd:
            passwd = 'interpeak'

        import os
        if self.use_sftp == True:
            import paramiko

            #self.sh.log('using get via sftp')
            transport = paramiko.Transport((self.login_ip().addr,22))
            transport.connect(username = user, password = passwd)

            sftp = paramiko.SFTPClient.from_transport(transport)

            sftp.get(localpath=os.path.join('.', filename),remotepath=os.path.basename(filename))

            sftp.close()
            transport.close()
        else:
            import ftplib
            ftp = ftplib.FTP(self.login_ip().addr)
            ftp.login(user, passwd)
            ftp.retrbinary('RETR %s' % filename, open(os.path.basename(filename), 'wb').write)
            ftp.quit()


    def ftp_put(self, filename, dstdir = None, user = None, passwd = None):
        if not user:
            user = self.ftp_user
        if not user:
            user = 'ftp'
        if not passwd:
            passwd = self.ftp_passwd
        if not passwd:
            passwd = 'interpeak'

        import os

        if self.use_sftp == True:
            import paramiko

            #self.sh.log('using get via sftp')
            transport = paramiko.Transport((self.login_ip().addr,22))
            transport.connect(username = user, password = passwd)

            sftp = paramiko.SFTPClient.from_transport(transport)

            if dstdir:
                sftp.chdir(dstdir)

            sftp.put(localpath=os.path.join('.', filename),remotepath=os.path.basename(filename))

            sftp.close()
            transport.close()
        else:
            import ftplib
            ftp = ftplib.FTP(self.login_ip().addr)
            ftp.login(user, passwd)

            if dstdir:
                ftp.cwd(dstdir)

            (_, fn) = os.path.split(filename)

            data = open(filename)
            ftp.storbinary('STOR %s' % fn, data)
            data.close()
            ftp.quit()

    def ftp_transfer(self, dir, dstdir = None, user = None, passwd = None, skipbase = False):
        if not user:
            user = self.ftp_user
        if not user:
            user = 'ftp'
        if not passwd:
            passwd = self.ftp_passwd
        if not passwd:
            passwd = 'interpeak'

        normdir = os.path.normpath(dir)
        basedir = os.path.basename(normdir)
        tfiles = []

        if self.use_sftp == True:
            import paramiko

            #self.sh.log('using transfer via sftp')
            transport = paramiko.Transport((self.login_ip().addr,22))
            transport.connect(username = user, password = passwd)

            sftp = paramiko.SFTPClient.from_transport(transport)

            if dstdir:
                sftp.chdir(dstdir)

            sftp.chdir('.')
            pwd0 = sftp.getcwd()

            if not skipbase:
                try:
                    sftp.mkdir(basedir)
                except:
                    pass

                sftp.chdir(basedir)

            pwd = sftp.getcwd()

            for root, dirs, files in os.walk(normdir):
                cwd = root[len(normdir):].strip('/')

                # Unless its the root directory
                if len(cwd) > 0:
                    try:
                        sftp.mkdir(os.path.join(pwd, cwd))
                    except:
                        pass
                    sftp.chdir(os.path.join(pwd, cwd))

                for file in files:
                    fname = os.path.join(root, file)
                    tfiles.append(fname)
                    sftp.put(fname, file)

                sftp.chdir(pwd)

            sftp.chdir(pwd0)
            sftp.close()
            transport.close()
        else:
            import ftplib
            ftp = ftplib.FTP(self.login_ip().addr)
            ftp.login(user, passwd)

            if dstdir:
                ftp.cwd(dstdir)

            pwd0 = ftp.pwd()
            if not skipbase:
                try:
                    ftp.mkd(basedir)
                except ftplib.error_perm, resp:
                    pass

                ftp.cwd(basedir)

            pwd = ftp.pwd()
            for root, dirs, files in os.walk(normdir):
                cwd = root[len(normdir):].strip('/')

                # Unless its the root directory
                if len(cwd) > 0:
                    try:
                        ftp.mkd(os.path.join(pwd, cwd))
                    except ftplib.error_perm, resp:
                        pass
                    ftp.cwd(os.path.join(pwd, cwd))

                for file in files:
                    fname = os.path.join(root, file)
                    tfiles.append(fname)
                    data = open(fname)
                    ftp.storbinary('STOR %s' % file, data)
                    data.close()

                ftp.cwd(pwd)
            ftp.cwd(pwd0)
            ftp.quit()
        return tfiles


    def ftp_recursive_upload(self, dir, user=None, passwd=None):
        '''
        Will upload the local "dir" to the target using ftp.
        (Only one level of recursion for now)
        Works on ipappl.
        '''
        if not user:
            user = self.ftp_user
        if not passwd:
            passwd = self.ftp_passwd

        if self.use_sftp == True:
            import paramiko

            #self.sh.log('using recursive upload via sftp')
            transport = paramiko.Transport((self.login_ip().addr,22))
            transport.connect(username = user, password = passwd)

            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.chdir(self.las_prefix())

            import os
            for root, dirs, files in os.walk(dir):

                for fn in os.listdir(root):
                    if fn not in dirs:
                        sftp.put(localpath=os.path.join(root,fn),remotepath=fn)

                for d in dirs:
                    try:
                        sftp.mkdir(d)
                    except:
                        for x in sftp.listdir(sftp.normalize(d)):
                            sftp.remove(os.path.join(sftp.normalize(d),x))
                            pass

                    for fn in os.listdir(os.path.join(root,d)):
                        sftp.put(localpath=os.path.join(root, d, fn),remotepath=os.path.join(sftp.normalize(d),fn))

            sftp.close()
            transport.close()
        else:

            import ftplib
            ftp = ftplib.FTP(self.login_ip().addr)
            ftp.login(user, passwd)

            import os
            for root, dirs, files in os.walk(dir):
                cwd = root[len(dir):]
                ftp.cwd(cwd)
                for d in dirs:
                    try:
                        ftp.mkd(d)
                    except ftplib.error_perm, resp:
                        #resp is probably "550 File exists"
                        pass

                for fn in files:
                    data = open(os.path.join(root, fn))
                    ftp.storbinary('STOR %s' % fn, data)
                    data.close()

                if len(cwd) > 0:
                    ftp.cwd('..')
            ftp.quit()


    def scp_recursive_upload(self, dir, dstdir = ''):
        import subprocess
        subprocess.call(('scp -q -r %s %s@%s:%s' % (dir, self.sh.s.user, self.login_ip().addr, dstdir)).split())


    def sftp_recursive_upload(self, dir, user=None, passwd=None):
        pass


    def del_vr(self, nr, cleanup=False):
        # let ipnet do the actual moving of netifs to vr 0
        self.ts.del_vr(nr)
        self._del_vr(nr, cleanup)
        for n in self.ts.netifs:
            if n.vr == nr:
                n.vr = 0
        #for n in es.routes:
        #    n = (dst, gw, dev, vr, family)
        #    if n.vr = nr:


    def get_route(self, addr, exp_dst = None, exp_gw = None,
                  exp_nm = None, exp_ifp = None, exp_ifa = None,
                  exp_if = None, exp_flags = None,
                  exp_rtt_msec_rttvar_hopcount_mtu_expire = None, vr = '', resolve = False):
        """
        Returns a dict with everything you didn't expect.
        Set exp_XXX to True if you want it returned. This is needed cause
        some parameters aren't returned in certain cases.
        Set exp_XXX to a value that you want to match.
        """
        #!!! use ip()
        if isinstance(addr,str) and addr == 'default':
            if self.ipv4:
                addr = '0.0.0.0'
            else:
                addr = '-inet6 ::'

        return self._get_route(addr, exp_dst, exp_gw, exp_nm, exp_ifp, exp_ifa, exp_if, exp_flags, exp_rtt_msec_rttvar_hopcount_mtu_expire, vr, resolve)


    def add_arp(self, ip2, mac, dev = "", vr = 0):
        "Make an arp/ndp entry"
        ip2 = ip(ip2)
        mac = mac.lower()
        dev = self._get_dev(dev)
        self._add_arp(ip2,mac,dev.ifname,vr)
        self.ts.arps[(ip2.addr, mac, dev.ifname, vr)] = True


    def del_arp(self, ip2, mac = "", dev = "", vr = 0, cleanup = False):
        mac = mac.lower()
        devname = self._get_devname(dev)
        ip2 = ip(ip2)
        self.ts.del_arp((ip2.addr, mac, devname, vr))
        self._del_arp(ip2, mac, devname, vr, cleanup)


    def verify_arp(self, ip2, mac = '', vr = 0, succeed = True):
        ip2 = ip(ip2)
        mac = mac.lower()
        a = self._verify_arp(ip2.v6, vr, succeed)
        all = dict([(ip(i),m) for (i,m) in a]) # [1,2,3,4,5,6] -> [(1,2), (3,4), (5,6)]

        mac_listed = ''
        if ip2 in all:
            mac_listed = all[ip2]

        if succeed:
            if ip2 not in all:
                #didnt find ip
                raise test_fail('expected arp entry not found')
            #found ip
            if not mac:
                #no mac given, so mac_listed must be a valid mac to succeed
                if mac_listed == '00:00:00:00:00:00': #the only known bad value
                    raise test_fail('wanted arp entry gone')
                #other mac values are valid.
                return
            #a mac was given. must match it.
            if mac == mac_listed:
                return
            else:
                raise test_fail('bad arp found, ip=%s, expected mac=%s, gotten mac=%s' % (ip2.addr, mac, mac_listed))
        else:
            #if it's supposed to fail
            if ip2 not in all:
                #scanned for ip not found
                return
            #found ip
            if not mac:
                #no mac given
                if mac_listed == '00:00:00:00:00:00':
                    return
                #any other mac values are hits and thus bad.
                raise test_fail('found unwanted arp entry for ip=%s with mac=%s' % (ip2.addr, mac_listed))
            #a mac was given. must not match it.
            if mac == mac_listed:
                raise test_fail('found unwanted arp entry')
            else:
                return
        raise engine_error('test engine error')


    def _intern_proc_state(self, name, vr):
        if not self.ts.procs:
            self._proc_state()
            self.ts.procs_copy = self.ts.procs.copy()
        return self.ts.procs.get((name,vr), 'killed')


    def start_proc(self, name, vr = 0, cleanup=False):
        "ipd start someproduct"
        #if not self.opt['fast'] and
        if self._intern_proc_state(name,vr) == 'started':
            return
        self._start_proc(name,vr,cleanup)
        self.ts.procs[(name,vr)] = 'started'


    def stop_proc(self, name, vr = 0, cleanup=False, timeout = -1):
        #if not self.opt['fast'] and
        if self._intern_proc_state(name,vr) == 'killed':
            return
        self._stop_proc(name,vr,cleanup, timeout)
        self.ts.procs[(name,vr)] = 'killed'


    def reconfigure_proc(self, name, vr = 0):
        #if not self.opt['fast'] and
        if self._intern_proc_state(name,vr) == 'killed':
            raise engine_error('')
        self._reconfigure_proc(name,vr)

    def ping_proc(self, name, vr = 0):
        #if not self.opt['fast'] and
        if self._intern_proc_state(name,vr) == 'killed':
            raise engine_error('')
        self._ping_proc(name,vr)


    def restart_proc(self, name, vr = 0, timeout = -1):
        self.stop_proc(name, vr)
        try:
            self.start_proc(name,vr)
        except:
            if self._intern_proc_state(name, vr) == 'killed':
                # Supposedly killed; but seems to be started.
                # Some kind of bad race?
                self._stop_proc(name, vr, cleanup=True, timeout = timeout)
            self.start_proc(name,vr)

    def configure_seckeydb(self):
        self.sh.send_and_wait_prompt('cp /romfs/* /ram/')

        #self.sh.send_and_wait_prompt('keydb delete key 1') 
        #self.sh.send_and_wait_prompt('keydb delete key 2')
        self.sh.send('keydb delete key 1') 
        self.sh.wait_prompt(timeout=60)
        self.sh.send('keydb delete key 2') 
        self.sh.wait_prompt(timeout=60)
        
        self.sh.send_and_wait_prompt('keydb import key default_dsa /romfs/clt_dsa_key_1024-private')
        self.sh.send_and_wait_prompt('keydb import key default_rsa /romfs/clt_rsa_key_1024-private')
        
    def get_sysvar(self, name, vr=0):
        vr = IF(vr, '-V %s' % vr, '')

        self.sh.send(self.las_prefix() + 'sysvar get %s%s' % (name, vr))
        i, v = self.sh.expect_get([r"sysvar: '%s' not found" % name,
                                   r"sysvar: %s=([^\r]*)\r" % name])
        if i == 0:
            raise test_fail("sysvar: '%s' not found" % name) #mechanism used in set_sysvar
        #could cache
        if v == '':
            return ' ' #its not possible to set sysvars to '' with the ipcom shell
        return v

    def get_sysvar_dict(self, name, vr=0):
        rets = {}
        vr = IF(vr, '-V %s' % vr, '')

        lines = self.sh.send_and_return_all(self.las_prefix() + 'sysvar list %s%s' % (name, vr))
        if len(lines) == 1:
            return {}
        else:
            for line in lines[1:]:
                k, v = line.strip().split('=')
                rets[k] = v 
            return rets
        
    def unset_sysvar(self, name, vr=0, cleanup = False, las_prefix=None):
        vr2 = IF(vr, '-V %s ' % vr, '')
        if las_prefix is None:
            las_prefix = self.las_prefix()

        self.sh.send(las_prefix + 'sysvar unset %s%s' % (vr2, name))
        v = self.sh.expect_exact(["sysvar: unset failed: not found",
                               "sysvar: '%s' unset ok" % name])
        self.sh.wait_prompt()
        if v == 0 and not cleanup:
            raise test_fail("sysvar: '%s' not found" % name)

    def set_sysvar(self, name, value, vr=0, overwrite=True, create=True, readonly=False, cleanup=False, las_prefix=None):
        if value == '':
            value = ' '

        if las_prefix is None:
            las_prefix = self.las_prefix()

        if not cleanup:
            try:
                old_value = self.get_sysvar(name, vr)
            except test_fail:
                # Sysvar did not exist before
                self.push_state_restorer(self.unset_sysvar, (name, vr, True, las_prefix))
            else:
                self.push_state_restorer(self.set_sysvar, (name, old_value, vr, True, True, readonly, True, las_prefix))

        cmd = las_prefix + 'sysvar set '
        if vr:
            cmd += '-V %s ' % vr
        if overwrite:
            cmd += '-o '
        if create:
            cmd += '-c '
        if readonly:
            cmd += '-r '
        cmd += '%s "%s"' % (name, value)
        self.sh.send(cmd)
        #self.sh.wait_prompt()
        self.sh.expect_exact('sysvar: %s=%s ok' % (name, value))
        self.sh.wait_prompt()
        #pdb.set_trace()

    def get_sysctl(self, name, vr=None):

        cmd = 'sysctl '
        if vr is not None:
            cmd += '-V %s ' % vr
        cmd += name

        self.sh.send(cmd)
        # TODO: handle partial match that returns a subtree of results
        # TODO: indicate invalid subkey?
        i, v = self.sh.expect_get([r"sysctl: unknown key: %s" % name,
                                   r"%s=([^\r]*)\r" % name])
        if i == 0:
            raise test_fail("sysctl: '%s' not found" % name) #mechanism used in set_sysctl
        return v

    def set_sysctl(self, name, value, vr=None, cleanup=False):

        if not cleanup:
            try:
                old_value = self.get_sysctl(name, vr)
            except test_fail:
                # sysctl variable did not exist before; cannot create it! reraise exception.
                raise
            else:
                self.push_state_restorer(self.set_sysctl, (name, old_value, vr, True))

        cmd = 'sysctl '
        if vr is not None:
            cmd += '-V %s ' % vr
        cmd += '-w %s="%s"' % (name, value)
        self.sh.send(cmd);
        self.sh.expect_exact('%s=%s' % (name, value))
        self.sh.wait_prompt()


    def _start_proc(self, name, vr, cleanup):
        vrx = IF(vr, '-V %s ' % vr, '')
        cmd = ''
        if len(self.las_prefix()) > 0:
            cmd += 'PATH=${PATH}:%s %s' % (self.las_prefix(), self.las_prefix())
        cmd += 'ipd %sstart %s' % (vrx, name)
        self.sh.send(cmd)
        if not cleanup:
            self.sh.expect_exact('ipd: start %s ok' % name)
        self.sh.wait_prompt()


    def _stop_proc(self, name, vr, cleanup, timeout):
        vrx = IF(vr, '-V %s ' % vr, '')
        self.sh.send('%sipd %skill %s' % (self.las_prefix(), vrx, name))
        if not cleanup:
            self.sh.expect_exact("ipd: kill %s ok" % name, timeout = timeout)
        self.sh.wait_prompt()
        for _ in range(20):
            x = self._get_running_procs(name, vr, timeout = timeout)
            if (name,vr) in x and x[(name, vr)] == 'killed':
                break
            time.sleep(0.5)
        else:
            self.sh.s.log('!!! Problem killing %s.' % name, echo = True)


    def _get_running_procs(self, name = None, vr = 0, timeout = -1):
        vrx = IF(vr, '-V %s ' % vr, '')
        if name:
            all = self.sh.send_and_return_all(self.las_prefix() + 'ipd %slist %s' % (vrx, name), wait_timeout = timeout)
        else:
            all = self.sh.send_and_return_all(self.las_prefix() + 'ipd %slist' % vrx, wait_timeout = timeout)

        procs = {}
        for a in all[1:]:
            n,s = re.match(r'(\w+)\s+(started|killed)', a).groups()
            procs[(n,vr)] = s
        return procs


    def _proc_state(self):
        self.ts.procs = self._get_running_procs()

    # handle las
    def _reconfigure_proc(self, name, vr):
        vrx = IF(vr, '-V %s ' % vr, '')
        cmd = ''
        if len(self.las_prefix()) > 0:
            cmd += 'PATH=${PATH}:%s %s' % (self.las_prefix(), self.las_prefix())
        cmd += "ipd %sreconfigure %s" % (vrx, name)
        self.sh.send(cmd)
        self.sh.expect_exact("ipd: reconfigure %s ok" % name)
        self.sh.wait_prompt()

    # handle las
    def _ping_proc(self, name, vr):
        vrx = IF(vr, '-V %s ' % vr, '')
        cmd = ''
        if len(self.las_prefix()) > 0:
            cmd += 'PATH=${PATH}:%s %s' % (self.las_prefix(), self.las_prefix())
        cmd += "ipd %sping %s" % (vrx, name)
        self.sh.send(cmd)
        self.sh.expect_exact("ipd: ping %s ok" % name)
        self.sh.wait_prompt()


    def _create_ifs_from_existing(self, vr=0):
        ifs = self._gather_existing_ifs(vr)
        created_ifs = []
        for i in ifs:
            x = self._create_netif() # -> ipnet_netif or other type
            x.from_existing(*i)
            created_ifs.append(x)
        return created_ifs


    def issue_shellcmd(self, cmd, args, exp = None ,cleanup = False):
        if exp == None:
            self.sh.send_and_wait_prompt(self.las_prefix() + cmd + ' ' + args)
        else:
            self.sh.send(self.las_prefix() + cmd + ' ' + args)
            self.sh.expect(exp)
            self.sh.wait_prompt()


    def is_shellcmd_present(self, cmd):
        ls = self.sh.send_and_return_all(cmd)
        return re.match(r"(.*Unknown command: |Cmd: '\w+' not found)", ls[0]) == None


    def smptest(self, sink, threads, datasize, v6, istcp=True, timeout=60):
        options_string = ""
        if v6 == '6':
            options_string += " -6 "
        if istcp == False:
            options_string += " -u "
        sink.sh.send("smptest -s %s -l %s %s" % (threads, datasize, options_string))
        sink.sh.expect_exact("Ready.")
        self.sh.send("smptest -c -s %s -l %s %s %s" % (threads, datasize, options_string, ip(sink, v6)))
        sink.sh.expect_exact("Success.", timeout)
        self.sh.wait_prompt()
        sink.sh.wait_prompt()


    def snmp_get(self, var):
        #see getgen.py for example code (pysnmp package 4.1.8a)
        #how to update pysnmp in repo:
        #rm the pysnmp dir in the cvs repo on the server manually
        #emerge pysnmp
        #cp -r /usr/lib/python2.5/site-packages/pysnmp/v4/ thirdparty/pysnmp
        #build-pysnmp-mib -o thirdparty/pysnmp/smi/mibs/MIP-MIB.py /usr/share/mibs/ietf/MIP-MIB
        #build-pysnmp-mib -o thirdparty/pysnmp/smi/mibs/MOBILEIPV6-MIB.py /usr/share/mibs/ietf/MOBILEIPV6-MIB
        #build-pysnmp-mib -o IANAifType-MIB.py thirdparty/IANAifType-MIB
        #build-pysnmp-mib -o IF-MIB.py /usr/share/mibs/ietf/IF-MIB
        #build-pysnmp-mib -o IP-MIB.py /usr/share/mibs/ietf/IP-MIB
        #build-pysnmp-mib -o INET-ADDRESS-MIB.py /usr/share/mibs/ietf/INET-ADDRESS-MIB
        #build-pysnmp-mib -o MOBILEIPV6-MIB.py /usr/share/mibs/ietf/MOBILEIPV6-MIB
        #cd thirdparty
        #find pysnmp -type d -exec cp ../../config/.cvsignore '{}' ';'
        #cd pysnmp
        #find -name '*.py[co]'|xargs rm
        #cd ..
        #cvs add pysnmp
        #cd pysnmp
        #cvs import iptestengine/src/thirdparty/pysnmp n start
        #emerge -C pysnmp
        from pysnmp.entity.rfc3413.oneliner import cmdgen
        errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().getCmd(
            cmdgen.CommunityData('test-agent', 'public'),
            cmdgen.UdpTransportTarget((self.login_ip().addr, 161)),
            (('', var), 0),
        )

        if errorIndication:
            raise test_fail(errorIndication)
        else:
            if errorStatus:
                raise test_fail('%s at %s\n' % (errorStatus.prettyPrint(), varBinds[int(errorIndex)-1]))
            else:
                #for name, val in varBinds:
                #    print '%s = %s' % (name.prettyPrint(), val.prettyPrint())
                name, val = varBinds[0]
                try:
                    val = int(val)
                except ValueError:
                    pass
                return val


    def snmp_verify(self, var, want):
        got = self.snmp_get(var)
        if got != want:
            raise test_fail('snmp_verify failed. got "%s", expected "%s".' % (got, want))

    def fips_140_2_mode(self):
        self.sh.send("fips_ctrl mode show")
        i = self.sh.expect(["FIPS mode on",
                            "FIPS mode off",
                            "ipcom_shell : Unknown command: 'fips_ctrl'",
                            "Cmd: 'fips_ctrl' not found"])
        self.sh.wait_prompt()
        if i==0:
            return True

        return False

    def fips_140_2_mode_set(self, on_off):
        # Only push the initial FIPS 140-2 state. Switching to FIPS 140-2 mode is a CPU
        # intensive operation as many self tests are run.
        if not self.fips_state_restorer_pushed:
            self.push_state_restorer(self.fips_140_2_mode_restore, (self.fips_140_2_mode(),))
            self.fips_state_restorer_pushed = True
        if on_off:
            self.sh.send("fips_ctrl mode on")
        else:
            self.sh.send("fips_ctrl mode off")
        i = self.sh.expect(["FIPS mode on",
                            "FIPS mode off",
                            "Already in FIPS mode",
                            "Not in FIPS mode",
                            "ipcom_shell : Unknown command: 'fips_ctrl'",
                            "Cmd: 'fips_ctrl' not found"])
        self.sh.wait_prompt()

        if i==0 or i==1 or i==2 or i==3:
            return True
        else:
            raise test_fail("fips_ctrl shell command not included")


    def fips_140_2_build(self):
        self.sh.send("fips_ctrl mode show")
        i = self.sh.expect(["FIPS mode on",
                            "FIPS mode off",
                            "ipcom_shell : Unknown command: 'fips_ctrl'",
                            "Cmd: 'fips_ctrl' not found"])
        self.sh.wait_prompt()
        if i==0 or i == 1:
            return True

        return False

    def fips_140_2_mode_restore(self, on_off):
        if self.fips_140_2_mode() != on_off:
            self.fips_140_2_mode_set(on_off)

################################################################################
#
#       _       _                       _
#      (_)_ __ | |_ __ _ _ __ __ _  ___| |_
#      | | '_ \| __/ _` | '__/ _` |/ _ \ __|
#      | | |_) | || (_| | | | (_| |  __/ |_
#      |_| .__/ \__\__,_|_|  \__, |\___|\__|
#        |_|                 |___/
################################################################################
class iptarget(target):
    'Base class of ipnet and iplite.'
    def __init__(self, *args, **kwargs):
        target.__init__(self, *args, **kwargs)
        self.ftp_user = "ftp"
        self.ftp_passwd = "interpeak"
        self.use_sftp = False

    def init(self, *args, **kwargs):
        target.init(self, *args, **kwargs)
        target.configure_seckeydb(self)

        # Many VxWorks targets reset their clock to Jan 1 1970 at boot. The time
        # needs to be set to UTC (Greenwich Mean Time) since VxWorks has no
        # notion of timezones. We must not set the time on ipcom-unix's ipouts
        # since they use localized time (time zone and DST accounted for). If the
        # year differs on the target and host running iptestengine, we set the time
        # of the target.
        time_date_str = self.sh.send_and_return_all('date')
        (weekday, month, day, time_str, year) = time_date_str[0].split()
        t = time.gmtime()
        if year != str(t[0]):
            self.sh.send_and_wait_prompt('date %s-%s-%s' % (t[0], t[1], t[2]))
            #self.sh.expect_exact_and_wait_prompt('ok')
            self.sh.send_and_wait_prompt('time %s:%s:%s' % (t[3], t[4], t[5]))
            #self.sh.expect_exact_and_wait_prompt('ok')

        #syslog priority debug2
        ls = self.sh.send_and_return_all('syslog list')
        facilities = [l.split() for l in ls[1:]]
        self.sh.send("syslog priority all debug2")
        self.sh.wait_prompt()
        for [f,l] in facilities:
            if f in [ 'ipike', 'ipipsec', 'ipnet' ] and self.target_speed >= 100:
                self.sh.send("syslog priority %s warning" % f)
                self.sh.expect_exact_and_wait_prompt('syslog: facility %s priority set to warning' % f)

    def _gather_existing_ifs(self, vr=0):
        '''returns a list with netifs'''
        # works on ipnet and iplite
        vr2 = IF(vr, "-V %s " % vr, "")
        all = self.sh.send_and_return_all('ifconfig %s-a' % vr2, strip_lines=False)
        #group IF-lines in a list
        ifgroup = []
        lines = []
        lines.append(all[0].strip())
        for i in all[1:]:
            i_stripped = i.strip()
            if i.startswith("\t"):
                lines.append(i_stripped)
            elif i_stripped == '':
                continue
            else:
                ifgroup.append(lines)
                lines = [i_stripped]
        ifgroup.append(lines)

        ifs = []
        for i in ifgroup:
            tunnel_local_ip = None
            tunnel_remote_ip = None
            tunnel_ttl = None
            #ifname, linktype and mac
            ifname = re.match(r'(\w+)\s+Link type.*', i[0]).group(1)
            m = re.match(r'.*Link type:(\w+)\W*', i[0]).group(1)
            if m in ("Local","24"): #numbers are from iplite
                linktype = "loopback"
                mac = None
            elif m in ("Ethernet", "6"):
                linktype = "eth"
                mac = re.match(r'.*Link type:(?:Ethernet|6)\s+HWaddr (%s).*' % mac_re, i[0]).group(1) #\s+ Queue
            elif m == 'Tunnel':
                linktype = 'tunnel'
                m = re.match(r'.*Link type:Tunnel\s+Queue:\w+  (?:GRE|Minimal Encap|IPv\[4\|6\]-over-IPv\w) (\S+) --> (\S+)  ttl:(\w+).*', i[0])
                tunnel_local_ip, tunnel_remote_ip, tunnel_ttl = ip(m.group(1)), ip(m.group(2)), int(m.group(3))
                mac = None
            elif m in ('Point', '23', 'PPP'): #PPP
                continue
            else:
                raise '(%s) not a clean target: restart it. (%s)' % (self.sh.s.name, m) #!!!todo, session shouldnt hold name

            l = 1
            ips = {}
            if i[l].startswith('capabilities: '):
                l += 1
            while i[l].startswith('inet '):
                m = re.match(r"inet (%s)\s+mask (%s).*" % (ip_re, ip_re), i[l])
                ip2 = m.group(1)
                mask = m.group(2)
                m = re.match(r".*broadcast (%s)" % ip_re, i[l])
                bcast = None
                if m:
                    bcast = m.group(1)
                ips[ip(ip2 + '/%s' % netmask_to_prefixlen(mask))] = True
                #ips[ip2] = True
                l += 1

            while i[l].startswith('inet6 unicast'):
                if i[l].find('anycast') == -1:
                    m = re.match(r"inet6 unicast (%s)(?:%%\S+)?\s+prefixlen (\w+)" % ip6_re, i[l])
                    if m:
                        ip2 = m.group(1)
                        pfx = int(m.group(2))
                        ips[ip(ip2 +"/%s" % pfx)] = True
                        #ips[ip2] = True
                    else: #iplite doesnt always have a prefixlen apparently(?)
                        m = re.match(r"inet6 unicast (%s)(?:%%\S+)?" % ip6_re, i[l])
                        ip2 = m.group(1)
                        ips[ip(ip2)] = True
                        #ips[ip2] = True
                l += 1

            #nasty copy/paste
            while i[l].startswith('inet6 multicast'):
                m = re.match(r"inet6 multicast (%s)(?:%%\S+)?\s+prefixlen (\w+)" % ip6_re, i[l])
                if m:
                    ip2 = m.group(1)
                    pfx = int(m.group(2))
                    ips[ip(ip2 +"/%s" % pfx)] = True
                    #ips[ip2] = True
                else: #iplite doesnt always have a prefixlen apparently(?)
                    m = re.match(r"inet6 multicast (%s)(?:%%\S+)?" % ip6_re, i[l])
                    ip2 = m.group(1)
                    ips[ip(ip2)] = True
                    #ips[ip2] = True
                l += 1
            ifs.append((ifname, vr, ips, mac, linktype, tunnel_local_ip, tunnel_remote_ip, tunnel_ttl))
        return ifs


    def get_if_by_ip(self, ip2):
        'returns ifname string with ip "ip2"'
        ip2 = ip(ip2)
        self.sh.send('ifconfig -a')
        return self.sh.expect_get('(\w+)\s+Link type[^\n]+\n(?:\s+inet[^\n]+\n)*\s+inet6? %s' % re.escape(ip2.addr), 2)


    def empty_log(self):
        self.sh.send('rm syslog')
        self.sh.wait_prompt()
        self.sh.send('syslog log file syslog')
        #self.sh.expect_exact('syslog: logging to file')
        self.sh.wait_prompt()


    def add_vr(self, nr): #!!! add 127.0.0.1 and v6 (::?) and up() if some flag set, "setup=True"?
        "Add virtual router"
        self.sh.expect_prompt('route vr -add %s' % nr)
        self.ts.add_vr(nr)
        self.ts.netifs.extend(self._create_ifs_from_existing(vr=nr))


    def _del_vr(self, nr, cleanup=False):
        #!!! delete routes here?
        s = 'route vr -delete %s' % nr
        if cleanup:
            self.sh.send(s)
            self.sh.wait_prompt()
        else:
            self.sh.expect_prompt(s)


#     def _has_ipv6_support(self):
#         lines = self.sh.send_and_return_all('ndp')
#         for line in lines:
#             if 'Unknown command' in line or 'command not found' in line:
#                 return False
#         return True


    def list_arp(self, vr = 0):
        "(Only for logging)"
        if vr:
            vr = '-V %s' % vr
        else:
            vr=''
        self.sh.send('arp %s -a' % vr)
        self.sh.wait_prompt_not(['Unknown', 'SYNPOSIS', 'illegal'])
        #!!! only v6
        #if self._has_ipv6_support():
        self.sh.send('ndp %s -a' % vr)
        self.sh.wait_prompt()


    def list_arp_return_all(self, v6, vr = 0):

        if vr:
            vr = '-V %s' % vr
        else:
            vr=''

        if v6:
            return self.sh.send_and_return_all('ndp %s -a' % vr)
        else:
            return self.sh.send_and_return_all('arp %s -a' % vr)

    def _add_arp(self, ip2, mac, devname, vr):
        vr2 = IF(vr,'-V %s' % vr,'')
        self.sh.expect_prompt('%s %s -i %s -s %s %s' % (IF(ip2.v6, 'ndp', 'arp'), vr2, devname, ip2.addr, mac))


    def _verify_arp(self, v6, vr, succeed):
        'returns a list of (ip,mac)-pairs. (un-"ip"-fied)'
        vr2 = IF(vr, '-V %s' % vr, '')
        if v6:
            a = self.sh.send_and_return_all('ndp %s -a' % vr2)
            r = [re.match(r'(%s)(?:%%\w+)?\s+(\S+).+' % (ip6_re, ), line).groups() for line in a[1:]]
        else:
            a = self.sh.send_and_return_all('arp %s -a' % vr2)
            if self.is_head:
                r = []
                for line in a[1:]:
                    ip_addr, hw_addr = (line.split()[0], line.split()[1])
                    if ip_addr and hw_addr:
                        r.append((ip_addr, hw_addr))
            else:
                r = [re.match(r'(%s) at (%s).+' % (ip_re, mac_re), line).groups() for line in a]
        return r


    def del_arps(self, vr = 0, cleanup=False):
        "Remove all arp entries"
        self.ts.del_arps(vr)
        vr2 = ''
        if vr:
            vr2 = '-V %s' % vr
        #cmds = [ 'arp %s -A' % vr2 ]
        #if self._has_ipv6_support():
        #    cmds.append('ndp %s -A' % vr2)
        #for s in cmds:
        self.sh.expect_prompt('arp %s -A' % vr2, cleanup=cleanup)
        self.sh.expect_prompt('ndp %s -A' % vr2, cleanup=True)


    def list_route(self, vr = '', exp_entry = None, succeed = True):
        if vr:
            vr = '-V %s' % vr
        self.sh.send('route show %s' % vr)
        if exp_entry:
            if succeed:
                self.sh.expect_exact(exp_entry)
                self.sh.wait_prompt()
                return
            else:
                self.sh.wait_prompt_not(exp_entry)
                return
        self.sh.wait_prompt()


    def num_net_daemons(self):
        self.sh.send('netsmp -n')
        return int(self.sh.expect_get('network daemons : ([0-9]+)\r\n'))


    def _ping(self, dst, succeed, src, packetsize, timeout, count,
              bypass_route, vr, icmp_replyer, require_ipping, retries,
              dont_frag, exp_ip, ttl, tos, timestamp, interval,
              at_least, interface, prefer_temporary_src_addr,
              hops):
        'packetsize = icmp header size (8) + payload.'

        switches  = '-s %s ' % packetsize
        switches += '-c %s ' % count
        if src:
            switches += '-S ' + src.addr + ' '

        if bypass_route:
            switches += '-r '

        if dont_frag and not dst.v6:
            switches += '-D '

        if ttl != 64:
            if dst.v6:
                switches += '-h %s ' % ttl
            else:
                switches += '-t %s ' % ttl

        if tos != 0:
            switches += '-Q %s ' % tos

        if timestamp:
            switches += '-T %s ' % timestamp

        if interval != 1000:
            switches += '-w %s ' % interval

        if vr:
            switches += '-V %s ' % vr

        if prefer_temporary_src_addr:
            switches += '-T '

        if interface:
            switches += '-I %s ' % interface

        for hop in hops:
            switches += '%s ' % hop

        cmd  = 'ping%s -n %s %s' % (dst.v6, switches, dst.addr)

        if icmp_replyer:
            icmp_reply = r"92 bytes from %s: Destination Net Unreachable" % '\S+' #esc_ip(icmp_replyer) #!!!
        else:
            icmp_reply = r"Destination Net Unreachable"

        if exp_ip:
            expipstr = re.escape(exp_ip.addr)
        else:
            expipstr = IF(dst.v6, ip6_re, ip_re)

        lst = [r'Reply from (%s) .+' % expipstr + r'.*Reply from .+'*(at_least - 1),
               icmp_reply,
               r'(Request timed out)'+ r'.*\1'*(count - 1),
               r'Echo request operation failed: Network is unreachable',
               r'Echo request operation failed: No route to host',
               r'Echo request operation failed: .* \(1006\)', # IP_ERRNO_EFIREWALL
               r'Request timed out', #: Operation would block',
               r'Need frag received from',
               r'Host unreachable received from',
               r'Resource temporarily unavailable',
               r"operation failed: Can't assign requested address"]
        target._ping_retrier(self, cmd, succeed, lst, retries, IF(exp_ip, exp_ip, dst)) #!!!todo change

    def __prefix(self, netif):
        if netif == None:
            return "ipnet."
        return '%s.' % netif.ifname

    def configure_ipv4_auto_proxy_arp(self, netif, enable):
        self.set_sysvar(self.__prefix(netif) + 'inet.AutoProxyArp',IF(enable, '1', '0') )

    def configure_ipv4_delete_address_on_dup_detect(self, netif, enable):
        self.set_sysvar(self.__prefix(netif) + 'inet.DeleteAddressOnDuplicateDetect', IF(enable, '1', '0'))

    def configure_ipv4_dont_forward_broadcast(self, netif, enable):
        self.set_sysvar(self.__prefix(netif) + 'inet.DontForwardBroadcast', IF(enable, '1', '0'))

    def configure_ipv4_icmp_ignore_broadcast(self, netif, enable):
        self.set_sysvar(self.__prefix(netif) + 'inet.IcmpIgnoreBroadcast', IF(enable, '1', '0'))

    def configure_ipv4_network_proxy_arp(self, netif, enable):
        self.set_sysvar(self.__prefix(netif) + 'inet.EnableNetworkProxyArp', IF(enable, '1', '0'))

    def configure_ipv4_send_gratuitous_arp(self, netif, enable):
        self.set_sysvar(self.__prefix(netif) + 'inet.SendGratuitousArp', IF(enable, '1', '0'))

    def configure_ipv6_accept_ra(self, netif, enable):
        self.set_sysvar(self.__prefix(netif) + 'inet6.AcceptRtAdv', IF(enable, '1', '0'))

    def configure_ipv6_allow_rthdr0(self, netif, enable):
        self.set_sysvar(self.__prefix(netif) + 'inet6.RtHdr0', IF(enable, '1', '0'))

    def configure_ipv6_dup_addr_detect_transmits(self, netif, value):
        self.set_sysvar(self.__prefix(netif) + 'inet6.DupAddrDetectTransmits', value)

    def configure_ipv6_privacy_extensions(self, netif, enable, regen_advance):
        self.set_sysvar(self.__prefix(netif) + 'inet6.EnablePrivacyExtensions', IF(enable, '1', '0'))
        self.set_sysvar(self.__prefix(netif) + 'inet6.RegenAdvance', regen_advance)

    def configure_ipv6_rt_solicitation_count(self, netif, value):
        self.set_sysvar(self.__prefix(netif) + 'inet6.RtSolicitationCount', value)

    def configure_ipv6_rt_solicitation_max_interval(self, netif, value):
        self.set_sysvar(self.__prefix(netif) + 'inet6.RtSolicitationMaxInterval', value)

    def configure_mcast_min_report_delay(self, value):
        self.set_sysvar('ipnet.mcast.min_report_delay', value)

    def configure_neigh_linger_time(self, netif, value, v6):
        self.set_sysvar(self.__prefix(netif) + 'inet%s.LingerTime' % IF(v6, '6',''), value)

    def configure_neigh_max_unicast_solicit(self, netif, value, v6):
        self.set_sysvar(self.__prefix(netif) + 'inet%s.MaxUnicastSolicit' % IF(v6, '6',''), value)

    def configure_neigh_max_multicast_solicit(self, netif, value, v6):
        self.set_sysvar(self.__prefix(netif) + 'inet%s.MaxMulticastSolicit' % IF(v6, '6',''), value)

    def configure_neigh_max_application_solicit(self, netif, value, v6):
        self.set_sysvar(self.__prefix(netif) + 'inet%s.MaxApplicationSolicit' % IF(v6, '6',''), value)

    def configure_neigh_max_pending(self, netif, value, v6):
        self.set_sysvar(self.__prefix(netif) + 'inet%s.MaxPending' % IF(v6, '6',''), value)

    def configure_route_max_clone_count(self, value):
        self.set_sysvar('ipnet.route.MaxCloneCount', value)

    def configure_send_redirect(self, netif, value, v6):
        self.set_sysvar(self.__prefix(netif) + 'inet%s.IcmpRedirectSend' % IF(v6, '6',''), value)

    def configure_tcp_connection_timeout(self, timeout):
          self.set_sysvar('iptcp.ConnectionTimeout', timeout)

    def configure_tcp_allow_tiny_window(self, allow):
          self.set_sysvar('iptcp.AllowTinyWindow', IF(allow, 1, 0))

    def configure_tcp_disable_land_attack(self, value):
        self.set_sysvar('iptcp.DisableLandAttack', value)
        self.set_sysvar('iptcp.LandAttackProtection', value)

    def configure_tcp_max_retransmits(self, value):
        self.set_sysvar('iptcp.MaxRetransmits', value)

    def configure_tcp_timestamp(self, enable):
        self.set_sysvar('iptcp.opt.Timestamp', IF(enable, '1', '0'))

    def configure_tcp_urg_rfc1122(self, enable):
        self.set_sysvar('iptcp.urg.Rfc1122', IF(enable, '1', '0'))

    def flush_ipsec(self):
        'does a "keyadm flush"'
        self.sh.send(self.las_prefix() + 'keyadm flush')
        self.sh.wait_prompt()


    def n_ipsec_sa(self):
        'returns total number of SAs'
        self.sh.send('ipsecctrl sa')
        return int(self.sh.expect_get('Total of (\w+) SAs.'))


    def dns(self, nr=1, vr=0):
        "Returns primary or secondary (nr=2) dns"
        if nr == 1:
            return self.get_sysvar('ipdnsc.primaryns', vr)
        elif nr == 2:
            return self.get_sysvar('ipdnsc.secondaryns', vr)
        raise engine_error('nr=%s'%s)


    def domainname(self, vr=0): #!!!TODO for linux
        return self.get_sysvar('ipdnsc.domainname', vr)


    def ntpserver(self, vr=0): #!!!TODO for linux
        return ip(self.get_sysvar('ipsntp.client.primary.addr', vr))


    def syslog(self, msg):
        try:
            self.sh.send_and_wait_prompt('syslog echo warning "%s"' % msg)
        except:
            pass

    def reboot(self):
        self.sh.send('reboot')


################################################################################
#                   ipcom_shell
################################################################################
#  _                                   _          _ _
# (_)_ __   ___ ___  _ __ ___      ___| |__   ___| | |
# | | '_ \ / __/ _ \| '_ ` _ \    / __| '_ \ / _ \ | |
# | | |_) | (_| (_) | | | | | |   \__ \ | | |  __/ | |
# |_| .__/ \___\___/|_| |_| |_|___|___/_| |_|\___|_|_|
#   |_|                      |_____|
################################################################################

class ipcom_shell(iptarget):
    'Made for commands which only work on the ipcom shell such as socktest'

    def socket(self, *a, **k):
        return socktest(self, *a, **k)


    def socket_from_fileno(self, fileno):
        """
        Creates a socket object and attaches it to an already existing
        socket
        fileno:       The numerical value of the socket on the NUT
        """
        return self.socket(0, fileno)


    def create_connected_socket_pair(self, server, server_addr = None, v6 = '', sk_type = 'stream', sk_proto = 0):
        """
        Returns a pair of client/server tcp sockets.
        server:       The target to be used for the server and
                      accepted socket. Must not be 'self'
        server_addr:  The address the server should bind to and the client
                      connect to or None to use the loopback address.
        """
        if not server_addr:
            if v6:
                server_addr = '::1'
            else:
                server_addr = '127.0.0.1'

        ssock = server.socket('inet%s' % v6, sk_type, sk_proto)
        server_addr = ip(server_addr)
        bind_addr = server_addr.addr
        conn_addr = server_addr.addr

        if v6 and '%' in bind_addr:
            bind_addr = bind_addr[:bind_addr.find('%')+1] + server.netif().ifname

        if v6 and '%' in conn_addr:
            conn_addr = conn_addr[:conn_addr.find('%')+1] + self.netif().ifname

        ssock.bind(bind_addr)
        _, port = ssock.getsockname(v6)
        ssock.listen()
        csock = self.socket('inet%s' % v6, sk_type, sk_proto)
        csock.connect(conn_addr, port)
        asock = ssock.accept()
        ssock.close()
        return csock, asock

    def create_udp_socket_pair(self, server, server_addr = None, v6 = ''):
        """
        Returns a pair of client/server udp sockets.
        server:       The target to be used for the server and
                      socket. Must not be 'self'
        server_addr:  The address the server should bind to and the client
                      connect to or None to use the loopback address.
        """
        if not server_addr:
            if v6:
                server_addr = '::1'
            else:
                server_addr = '127.0.0.1'

        ssock = server.socket('inet%s' % v6, 'dgram', '17')
        server_addr = ip(server_addr)
        bind_addr = server_addr.addr
        conn_addr = server_addr.addr

        if v6 and '%' in bind_addr:
            bind_addr = bind_addr[:bind_addr.find('%')+1] + server.netif().ifname

        if v6 and '%' in conn_addr:
            conn_addr = conn_addr[:conn_addr.find('%')+1] + self.netif().ifname

        ssock.bind(bind_addr)
        _, port = ssock.getsockname(v6)

        csock = self.socket('inet%s' % v6, 'dgram', '17')
        csock.connect(conn_addr, port)

        return csock, ssock


    def create_flood_pair(self, server_session, server_addr = None, v6 = '', burst = False, burst_size = 10240):
        csock, ssock = self.create_connected_socket_pair(server_session, server_addr, v6)
        csock.fsock = ssock
        ssock.fsock = csock
        csock.flood_start(ssock, burst = burst, burst_size = burst_size)
        return csock, ssock


    def try_flood(self, server_session, timeout, server_addr = None, v6 = '', csock_op = None):
        csock, ssock = self.create_connected_socket_pair(server_session, server_addr, v6)
        if csock_op:
            csock_op(csock)
        csock.fsock = ssock
        ssock.fsock = csock
        csock.flood_start(ssock)
        time.sleep(timeout)
        # Close the flood
        csock.flood_stop()
        # Close the sockets
        csock.close()
        ssock.close()


    def echoserver(self, ip2 = None, proto = 'udp', bufsize = 8192, port = 7301, echo_once = False, reuse_addr = False, limit_recv = 0):
        'for ipcom shell'
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

        self.sh.send('echoserver -t %s -b %s -p %s -L %s %s %s %s' % (proto, bufsize, port, limit_recv, echo_once, reuse_addr, ip2.addr))
        if proto == 'raw':
            self.sh.expect_exact(['echoserver is now listening at %s.*' % (ip2.addr), 'echoserver is now listening at %s.*' % (ip2.addr.upper())])
        else:
            self.sh.expect_exact(['echoserver is now listening at %s.%s' % (ip2.addr, port), 'echoserver is now listening at %s.%s' % (ip2.addr.upper(), port)])
        self.sh.wait_prompt()


    def stop_echoserver(self):
        self.sh.send('echoserver -q')
        self.sh.expect_exact('Stopped')
        self.sh.wait_prompt()


    def echoclient(self, ip2, read_reply=True, connect_before_send=True, reuse_addr=False,
                   verify_data=False, succeed = True, proto = 'udp', connection_refused=False,
                   network_unreachable=False, bufsize = 8192, nbuf = 1, chunk_size = 4096,
                   timeout = -1, local_port = 0, port = 7301, limit_recv = 0):
        if read_reply:
            read_reply = '-r '
        else:
            read_reply = ''
        if connect_before_send:
            connect_before_send = '-c '
        else:
            connect_before_send = ''
        if verify_data:
            verify_data = '-v '
        else:
            verify_data = ''
        if reuse_addr:
            reuse_addr = '-k '
        else:
            reuse_addr = ''
        if connection_refused:
            succeed = False

        ip2 = ip(ip2)
        self.sh.send('echoclient %s %s %s -t %s -b %s -n %s -s %s -L %s %s -j %s -p %s %s '
                     % (verify_data, read_reply, connect_before_send,
                        proto, bufsize, nbuf, chunk_size, limit_recv, reuse_addr,
                        local_port, port, ip2.addr))
        if succeed == False:
            if connection_refused:
                self.sh.expect_exact(self.sh.ECONNREFUSED, timeout)
            elif network_unreachable:
                self.sh.expect_exact(self.sh.ENETUNREACH, timeout)
            else:
                self.sh.expect_exact(['Failed to recv data: ' + self.sh.EWOULDBLOCK,
                                      'Failed to recv data: ' + self.sh.EAGAIN], timeout)
        else:
            self.sh.expect_exact('Received %s bytes' % (nbuf * chunk_size,), timeout)
        self.sh.wait_prompt()


    def alloc_port(self, tcp=True, v6=''):
        'get a previously unused port number'
        import random
        while True:
            p = 3000 + random.randint(0,40000)
            if p not in self.ts.ports:
                self.ts.ports[p] = True
                break
        return p


    #(could have an option for ipcom shell or native on linux)
    def ttcp_sink(self, sockbufsize = 16384, v6 = None, perf = '', timeout = -1, vr='', udp='', port = 5001, force_v4 = False, sctp=''):
        'you must run ttcp_expect() afterwards'
        self._ttcp_sink(sockbufsize, v6, perf, timeout, vr, udp, port, force_v4, sctp)


    def ttcp_source(self, ip2, buflen = 8192, nbuf = 2048, sockbufsize = 16384, v6 = None, timeout = -1, vr='', udp='', port = 5001, force_v4 = False, sctp=''):
        'you must run ttcp_expect() afterwards'
        self._ttcp_source(ip2, buflen, nbuf, sockbufsize, v6, timeout, vr, udp, port, force_v4, sctp)


    def ttcp_expect(self, timeout = -1):
        """
        ttcp_expect must be run after both ttcp_sink and ttcp_source.
        Returns [X bytes in, Y seconds, Z KB/s, V B/msec]
        example:
            hostX.ttcp_sink()
            hostY.ttcp_source(hostX)
            hostX.ttcp_expect()
            hostY.ttcp_expect()
        """
        #!!! int() and float()
        return self._ttcp_expect(timeout)


    def _ttcp_sink(self, sockbufsize, v6, perf, timeout, vr, udp, port, force_v4, sctp):
        if force_v4 == True:
            v6 = ''
        elif v6 == None:
            v6 = IF(self.ip().v6,'-x ','')
        else:
            v6 = IF(v6,'-x ','')

        if sockbufsize != '':
            sockbufsize = '-b %s ' % sockbufsize
        if vr:
            vr = '-V %s ' % vr
        if udp:
            udp = '-u '
        elif sctp:
            sctp = '-c '

        if port:
            port = '-p %s ' % port
        self.sh.send(self.las_prefix() + 'ttcp -r ' + port + vr + v6 + sockbufsize + udp + sctp)
        if udp:
            self.sh.expect_exact('ttcp-r: opened', timeout)
        else:
            self.sh.expect_exact('ttcp-r: listen', timeout)


    def _ttcp_source(self, ip2, buflen, nbuf, sockbufsize, v6, timeout, vr, udp, port, force_v4, sctp):
        if force_v4 == True:
            v6 = ''
        elif v6 == None:
            v6 = IF(self.ip().v6,'-x ','')
        else:
            v6 = IF(v6,'-x ','')

        if sockbufsize != '':
            sockbufsize = '-b %s ' % sockbufsize
        if vr:
            vr = '-V %s ' % str(vr)
        if udp:
            udp = '-u '
        elif sctp:
            sctp = '-c '

        if port:
            port = '-p %s ' % port
        nbuf = '-n %s ' % nbuf
        buflen = '-l %s ' % buflen
        ip2=ip(ip2)
        x=5
        self.sh.send(self.las_prefix() + 'ttcp -t ' + port + vr + v6 + sockbufsize + udp + sctp + nbuf + buflen + ip2.addr)
        if udp:
            self.sh.expect_exact('ttcp-t: socket', timeout)
        else:
            self.sh.expect_exact('ttcp-t: connect', timeout)


    def _ttcp_expect(self, timeout):
        '''returns stats after a run of ttcp send or receive
        tuple of (bytes, ms, kB/s, B/ms)'''
        #-r on sink, -t on source
        return self.sh.expect_get(r'ttcp-[rt]: ([0-9]+) bytes in ([-0-9]+) milliseconds = ([0-9]+) KB/sec, ([0-9]+) B/msec', timeout)



################################################################################
#                       ipnet target
#                _                  _
#               (_)_ __  _ __   ___| |_
#               | | '_ \| '_ \ / _ \ __|
#               | | |_) | | | |  __/ |_
#               |_| .__/|_| |_|\___|\__|
#                 |_|
################################################################################
class ipnet(iptarget):
    'ipnet run with ipcom shell'
    def init_clean_vlan(self):
        ls = self.sh.send_and_return_all('ifconfig -a', wait_timeout=60, strip_lines=False)
        vlans = [re.match('(vlan\S+)\s', line).group(1) for line in ls if line[:4] == 'vlan']
        for vlan in vlans:
            #self.sh.send_and_wait_prompt('ifconfig %s down' % vlan)
            #self.sh.send_and_wait_prompt('ifconfig %s destroy' % vlan)
            self.sh.send('ifconfig %s down' % vlan)
            self.sh.wait_prompt(timeout=60)
            self.sh.send('ifconfig %s destroy' % vlan)
            self.sh.wait_prompt(timeout=60)


    def init(self, opt):
        self.type = 'ipnet'
        self.init_clean_vlan()
        iptarget.init(self, opt)
        self.stop_proc('ipmipha', cleanup=True)
        self.stop_proc('ipmipfa', cleanup=True)
        self.stop_proc('ipmipmn', cleanup=True)
        self.stop_proc('ipmip6mn', cleanup=True)
        self.set_sysvar('ipnet.inet.IcmpRedirectSend', 1) #!!! multiple mip apps ruin each others' settings

    def _add_netif(self, *a, **k):
        x = netif_ipnet(self)
        x.new(*a, **k)
        return x

    def _create_netif(self):
        return netif_ipnet(self)


    def _get_route(self, addr, exp_dst, exp_gw, exp_nm, exp_ifp, exp_ifa, exp_if, exp_flags, exp_rtt_msec_rttvar_hopcount_mtu_expire, vr, resolve):
        if vr:
            vr = '-V %s ' % vr
        self.sh.send('route %s%sget %s' % (vr, IF(resolve, '', '-n '), addr))
        r = {}
        x = 'route to            : '
        i = self.sh.expect_exact([x + addr, self.sh.ENETUNREACH])
        if i >= 1:
            self.sh.wait_prompt()
            return {}

        x = 'RTA_DST             : '
        if exp_dst:
            self.sh.expect_exact(x + exp_dst)
        else:
            r['dst'] = self.sh.expect_get(x + '(%s)' % ip_re, eat_prompt = False)

        x = 'RTA_GATEWAY         : '
        if exp_gw == True:
            try:
                r['gw'] = ip(self.sh.expect_get(x + r'(\S+)\s', eat_prompt = True))
            except test_fail, msg:
                r['gw'] = None
            return r
        elif exp_gw:
            self.sh.expect_exact(x + exp_gw)

        x = 'RTA_NETMASK         : '
        if exp_nm == True:
            r['nm'] = self.sh.expect_get(x + ip_re, eat_prompt = False)
        elif exp_nm:
            self.sh.expect_exact(x + exp_nm)

        x = 'RTA_IFP             : '
        if exp_ifp:
            #mac_re
            pass
        else:
            pass

        x = 'RTA_IFA             : '
        if exp_ifa:
            #eth0
            pass
        else:
            pass

        x = 'interface           : '
        if exp_if:
            pass
        else:
            pass

        x = 'flags               : <'
        if exp_flags:
            #UP DONE MASK CLONING STATIC >
            if isinstance(exp_flags, str):
                exp_flags = [exp_flags]
            flags = self.sh.expect_get(x + r'([\w ]+) >', eat_prompt = False).lower().split()
            for ef in exp_flags:
                if not ef.lower() in flags:
                    self.sh.wait_prompt()
                    raise 'get_route: flag %s missing' % ef
        else:
            pass

        x = 'rtt,msec    rttvar  hopcount       MTU    expire'
        if exp_rtt_msec_rttvar_hopcount_mtu_expire:
            #rtt,msec    rttvar  hopcount       MTU    expire
            #       0         0         0         0         0
            pass
        else:
            pass

        self.sh.wait_prompt()
        return r


    def _add_del_route(self, dst, gw, dev, vr, family, add, cleanup,
                       cloning, succeed, reject, accounting, mpls_key,
                       blackhole, hopcount, down=False):
        ''' ipnet
        Use gw XOR dev.
        Netmask/prefixlen is set with addr/prefixlen, i.e. 10.1.1.1/8.
        '''
        args = ''

        if vr:
            args += '-V %s ' % vr

        gw2=''
        if gw:
            gw2 = gw.addr
        args += IF(add, 'add ', 'delete ')

        if hopcount:
            args += '-hopcount %d ' % hopcount

        if cloning:
            args += '-cloning '

        if blackhole:
            args += '-blackhole '

        if reject:
            args += '-reject '

        if down:
            args += '-down '

        if (dst.v6 and dst.prefixlen == 128 or
            not dst.v6 and dst.prefixlen == 32):
            route_type = 'host'
            addr2 = '-host %s ' % dst.addr
        else:
            route_type = 'net'
            dst = dst.mask(dst.prefixlen) #!!!todo remove mask
            addr2 = '-net -prefixlen %s %s ' % (dst.prefixlen, dst.addr)

        #!!! move
        if accounting and not add:
            self.ts.del_route((dst, gw, dev, vr, family))

        if dev:
            args += '-dev %s ' % dev.ifname

        if dst.v6:
            args += '-inet6 '

        if mpls_key != '':
            args += "-mpls %s " % mpls_key

        #!!!todo add route -n here for ipnet only, not iplite
        s = 'route -n ' + args + addr2 + gw2
        lines = self.sh.send_and_return_all(s)
        if not cleanup:
            ret_line = lines[0]
            ipre = IF(dst.v6, ip6_re, ip_re)
            if add:
                if succeed:
                    regexp = 'add %s (%s)' % (route_type, ipre)
                    if route_type == 'net':
                        regexp = regexp + ': netmask (%s)' % ipre
                    if gw:
                        regexp = regexp + ': gateway (%s)' % ipre

                    matches = list(re.match(regexp, ret_line).groups())
                    matches.reverse()

                    ret_dst = matches.pop()
                    if route_type == 'net':
                        ret_mask = matches.pop()
                    if gw:
                        ret_gw = matches.pop()

                    if ip(ret_dst) != dst:
                        raise test_fail('Dst returned was %s, expected %s' % (ret_dst, dst))
                    if route_type == 'net':
                        expected_mask = ip(prefixlen_to_netmask(dst.prefixlen, dst.v6))
                        if ip(ret_mask) != expected_mask:
                            raise test_fail('Mask returned was %s, expected %s' % (ret_mask, expected_mask))
                    if gw and ip(ret_gw) != ip(gw):
                        raise test_fail('Gateway returned was %, expected %s' % (ret_gw, gw))
                    #if mpls_key:
                    #    pass
                else:
                    self.sh.expect_exact('route: failed: ' + self.sh.ENETUNREACH)
            else:
                ret_dst = re.match('delete %s (%s)' % (route_type, ipre), ret_line).group(1)
                if ip(ret_dst) != dst:
                    raise test_fail('Delete dst return was %d, expected %s' % (ret_dst, dst))
#         else:
#             self.sh.wait_prompt()

#             if add:
#                 s = 'add %s %s' % (route_type, dst.addr.upper())
#                 if route_type == 'net':
#                     s += ': netmask %s' % prefixlen_to_netmask(dst.prefixlen, dst.v6)
#                 if gw:
#                     s += ': gateway %s' % gw.addr.upper()
#                 if succeed:
#                     self.sh.expect_exact(s)
#                 else:
#                     self.sh.expect_exact('route: failed: ' + self.sh.ENETUNREACH)
#             else:
#                 self.sh.expect_exact('delete %s %s' % (route_type, dst.addr))
#         self.sh.wait_prompt()
        if accounting and add:
            self.ts.add_route((dst, gw, dev, vr, family))


    def _list_addr(self, domain = '', vr = 0, dev = None, temporary = True, tentative = True):
        if domain == '4':
            ipv    = ' -4'
            names  = [  r'inet (%s)\s+mask (%s).*' % (ip_re, ip_re) ]
        elif domain == '6':
            ipv    = ' -6'
            names  = [ r'inet6 unicast (%s)(?:%%\S+)?\s+prefixlen (\w+)' % ip6_re ]
        else:
            ipv    = ''
            names  = [ r'inet6 unicast (%s)(?:%%\S+)?\s+prefixlen (\w+)' % ip6_re, r'inet (%s)\s+mask (%s).*' % (ip_re, ip_re) ]

        if dev:
            dev = ' %s' % dev
        else:
            dev = ''

        vr = IF(vr, '-V %s ' % vr, '')

        addrs = self.sh.send_and_return_all('ifconfig %s%s' % (vr, dev))
        found = []
        for addr in addrs:
            for name in names:
                m = re.match(name, addr)
                if m:
                    if not tentative and 'tentative' in addr:
                        break
                    if not temporary and 'temporary' in addr:
                        break
                    a = ip(m.group(1), m.group(2))
                    found.append(a)
                    break
        return found

    def _del_arp(self, ip2, mac, devname, vr, cleanup):
        vr2 = ''
        if vr:
            vr2 = '-V %s' % vr
        if ip2.v6:
            self.sh.expect_prompt('ndp %s -d %s%%%s %s' % (vr2, ip2.addr, devname, mac))
        else:
            self.sh.send('arp %s -i %s -d %s %s' % (vr2, devname, ip2.addr, mac))
            x = 'arp: ' + ip2.addr + ' deleted.'
            if cleanup:
                #it's ok if it's already gone while cleaning up
                x = [x, 'arp: operation failed, errno: S_errno_EINVAL', 'arp: operation failed, errno: Invalid argument']
            self.sh.expect_exact(x)
            self.sh.wait_prompt()


################################################################################
#                       iplite target
#                   _       _ _ _
#                  (_)_ __ | (_) |_ ___
#                  | | '_ \| | | __/ _ \
#                  | | |_) | | | ||  __/
#                  |_| .__/|_|_|\__\___|
#                    |_|
################################################################################
class iplite(iptarget):
    'iplite run with ipcom shell'

    def init(self, opt):
        self.type = 'iplite'
        iptarget.init(self, opt)


    def _add_netif(self, *a, **k):
        return netif_iplite(self, *a, **k)


    def _create_netif(self):
        return netif_iplite(self)


    def _get_route(self, addr, exp_dst, exp_gw, exp_nm, exp_ifp, exp_ifa, exp_if, exp_flags, exp_rtt_msec_rttvar_hopcount_mtu_expire, vr, resolve):
        if addr not in ('default', '0.0.0.0'):
            raise engine_error('iplite')
        if vr:
            raise engine_error('iplite')
        self.sh.send('route get')
        r = {}
        r['gw'] = self.sh.expect_get("IPv4 default gateway: (%s)" % ip_re)
        return r


    def add_route(self, dst, gw = '', dev = '', vr = '', family='', cloning = '', succeed = True, reject = False, accounting = True, cleanup = False, mpls_key=''):
        if dst not in ('default', '0.0.0.0', '0.0.0.0/0'):
            raise engine_error('iplite')
        self.sh.send('route set %s' % gw)
        self.sh.expect_exact("route: ok")
        self.sh.wait_prompt() #but why?
        if accounting:
            self.ts.add_route(dst, gw, dev, vr, family)


    def del_route(self, dst, gw = '', dev = '', vr = '', family='', cleanup = False, accounting = True):#, succeed = True):
        if accounting:
            self.ts.del_route(dst, gw, dev, vr, family)
        if dst not in ('default', '0.0.0.0', '0.0.0.0/0'):
            raise engine_error('iplite')
        self.sh.send('route set 0.0.0.0')
        self.sh.expect_exact("route: ok")
        self.sh.wait_prompt() #but why?


    def _del_arp(self, ip2, mac, devname, vr, cleanup):
        'iplite'
        if vr:
            raise engine_error('iplite - no vr')
        if ip2.v6:
                #raise 'dev required for ipv6'
            self.sh.expect_prompt('ndp -i %s -d %s %s' % (devname, ip2.addr, mac))
        else:
            dev2 = '-i ' + devname + ' '
            s = 'arp %s -d %s %s' % (dev2, ip2.addr, mac)
            if cleanup:
                self.sh.send(s)
                self.sh.wait_prompt()
            else:
                self.sh.expect_prompt(s)

################################################################################
#                       rtnet target
################################################################################
class rtnet(object):
    'rtnet run with ipcom shell'
    def __init__(self, shops, ts):
        self.ts = ts
        self.sh = shops
        
    def init(self, opt):
        self.type = 'rtnet'
        self.ipv4 = self.check_ip_v4()
        self.ipv6 = self.check_ip_v6()
        
    def check_ip_v4(self):
        route = self.sh.send_and_return_all('C ping4')
        return re.search(r".*unknown symbol name 'ping4'.*", route[0]) == None

    def check_ip_v6(self):
        route = self.sh.send_and_return_all('C ping6')
        return re.search(r".*unknown symbol name 'ping6'.*", route[0]) == None
    
    def syslog(self, msg):
        pass

    def reboot(self):
        #print '=== rtnet : reboot() at %s ipv4=%s' % (self.login_ip(), self.ipv4)
        #self.sh.send('C reboot')
        pass
            
    def cleanup(self):
        pass

    def cleanup2(self):
        pass

    def ip(self, v6=''):
        if v6 == '6':
            return self.ts.primary_ip6
        else:
            return self.ts.primary_ip

    def login_ip(self):
        "the ip as seen in the hosts.py file"
        return self.sh.s.login_ip
            
################################################################################
#                       linux target
#                _ _
#               | (_)_ __  _   ___  __
#               | | | '_ \| | | \ \/ /
#               | | | | | | |_| |>  <
#               |_|_|_| |_|\__,_/_/\_\
################################################################################
#!!! split into baselinux --> linux
#                         `-> lkm
class linux(target):
    '''ipnet-lkm/uml or linux
    VR requires the ipnet-patched iproute2 package: http://developer.osdl.org/dev/iproute2/
    and our ifconfig to run gentoo.
     if you dont use these, set self.use_iptool = False
    '''

    def __init__(self, *args, **kwargs):
        target.__init__(self, *args, **kwargs)
        self.me = 'linux'

    def _add_netif(self, *a, **k):
        x = netif_lkm(self)
        x.new(*a, **k)
        return x


    def _create_netif(self):
        return netif_lkm(self)


    def las_prefix(self, vr=0):
        'Return the prefix for all LAS shell commands'
        las_prefix = self.ts.las_prefix
        if vr:
            return las_prefix + 'chvr -n %d %s' % (int(vr), las_prefix)
        return las_prefix


    def init_clean_vlan(self):
        ls = self.sh.send_and_return_all('ip -o link', strip_lines=False)

        vlans = [re.match('[0-9]+: (vlan\S+)+:\s', line).group(1) for line in ls if 'vlan' in line[:20]]

        for vlan in vlans:
            self.sh.send_and_wait_prompt('ip link set down dev %s' % vlan)
            self.sh.send_and_wait_prompt('vconfig rem %s' % vlan)


    def init(self, opt):
        self.init_clean_vlan()
        target.init(self, opt)
        self.type = 'linux'
        self.ftp_user = self.sh.s.user
        self.ftp_passwd = self.sh.s.passwd
        self.use_sftp = False
        self.use_iptool = True #!!! make global flag
        self.use_ipnet_ping = False #should be a las flag instead(?)
        #!!! use sysvars api
        self.sh.send('sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"')
        self.sh.wait_prompt()

        #only useful on native linux
        self.sh.send('vconfig set_name_type VLAN_PLUS_VID_NO_PAD')
        #Set name-type for VLAN subsystem. Should be visible in /proc/net/vlan/config
        self.sh.expect_re_and_wait_prompt('Set name-type for VLAN subsystem. Should be visible in ')
           

    def get_if_by_ip(self, ip2): #!!!todo add vr and wrap it up in a netif()
        ip2 = ip(ip2)
        self.sh.send(self.las_prefix() + 'ip addr')
        return self.sh.expect_get('\d+: (\w+): <[^\n]+\n(?:\s+(?:inet|link)[^\n]+\n)*\s+inet6? %s' % re.escape(str(ip2)))


    def add_vr(self, nr):
        self.sh.expect_prompt(self.las_prefix() + 'ip vr add ' + str(nr))
        self.ts.add_vr(nr)
        self.ts.netifs.extend(self._create_ifs_from_existing(vr=nr))
        netif = self.netif(linktype='loopback', vr = nr)
        netif.add_ip(addr = "127.0.0.1/8")


    def _del_vr(self, nr, cleanup=False):
        self.sh.send_and_wait_prompt(self.las_prefix(nr) + 'ip link set down dev lo')
        s = self.las_prefix() + 'ip vr del %s' % nr
        self.sh.expect_prompt(s,cleanup)


    def _gather_existing_ifs(self, vr=0):
        'see iptarget comments'
        n_ifs = len(self.sh.send_and_return_all(self.las_prefix(vr) + 'ip -o link'))

        time.sleep(1)

        all = self.sh.send_and_return_all(self.las_prefix(vr) + "ip -o addr")

        n=0
        line = all[0]
        ifgroup = [[line]]
        num = line[:line.index(":")]
        last = num
        for line in all[1:]:
            num = line[:line.index(":")]
            if num == last:
                ifgroup[n].append(line)
            else:
                n += 1
                ifgroup.append([line])
            last = num

        ifs = []
        for i in ifgroup:
            tunnel_local_ip = None
            tunnel_remote_ip = None
            tunnel_ttl = None
            mac = None

            ifname = re.match(r'\S+ (\S+):.*', i[0]).group(1)
            m = re.match(r'.* link/(ether|loopback|ipip|gre|sit|tunnel6|\[901\]|\[902\]|\[900\]|\[131\])', i[0]).group(1)
            if m  == "loopback":
                linktype = "loopback"
            elif m == "ether" and ifname != 'shaper0':
                linktype = "eth"
                mac = re.match(r'.*link/ether (%s) brd.*' % mac_re, i[0]).group(1)
            elif m == "ether" and ifname == 'shaper0':
                continue
            elif m in ('ipip','gre','sit','tunnel6','[900]','[901]','[902]','[131]'):
                linktype = 'tunnel'
            else:
                raise 'not a clean target: restart it. (%s)' % m

            l = 1
            ips = {}
            nl = r'\S+ \S+\s+inet'
            while l < len(i) and re.match(nl + ".*", i[l]):
                is_ipv6 = re.match(nl + "(6?) .*", i[l]).group(1)
                if not is_ipv6 or not re.match(nl + r"%s\s+any.*" % is_ipv6, i[l]):
                    m = re.match(nl + r"%s (%s)/(\w+) .*" % (is_ipv6, IF(is_ipv6, ip6_re, ip_re)), i[l])
                    ip_address = m.group(1)
                    prefix_len = m.group(2)
                    if is_ipv6 and ip_address.lower()[:4] in [ 'fe80', 'ff02' ]:
                        # The 'ip' tool does not include the scope_id in the link local addresses
                        ip_address += '%%%s' % ifname
                    ips[ip(ip_address + '/%s' % prefix_len)] = True
                l += 1

            ifs.append((ifname, vr, ips, mac, linktype, tunnel_local_ip, tunnel_remote_ip, tunnel_ttl))
        return ifs


    def _get_route(self, addr, exp_dst, exp_gw, exp_nm, exp_ifp, exp_ifa, exp_if, exp_flags, exp_rtt_msec_rttvar_hopcount_mtu_expire, vr, resolve):
        #this will soon be fixed in the lkm to output default instead of 0.0.0.0/0
        r = {}
        if addr == '0.0.0.0' and exp_gw == True:
            all = self.sh.send_and_return_all(self.las_prefix(vr) + 'ip %sroute' % IF(resolve, '-r ', ''))

            r['gw'] = None
            for line in all:
                m = re.match(r'(?:default|0\.0\.0\.0/0) via (\S+) dev', line)
                if m:
                    r['gw'] = m.group(1)
            return r

        raise 'x'
        self.sh.send(self.las_prefix(vr) + 'ip route get ' + addr)
        x = 'route to            : '
        self.sh.expect_exact(x + addr)

        x = 'RTA_DST             : '
        if exp_dst:
            self.sh.expect_exact(x + exp_dst)
        else:
            r['dst'] = self.sh.expect_get(x + '(%s)' % ip_re, eat_prompt = False)

        x = 'RTA_GATEWAY         : '
        if exp_gw == True:
            # need abstraction here
            r['gw'] = self.sh.expect_get(x + r'(\S+)\s', eat_prompt = False)
        elif exp_gw:
            # and here
            # link#2
            self.sh.expect_exact(x + exp_gw)

        x = 'RTA_NETMASK         : '
        if exp_nm == True:
            r['nm'] = self.sh.expect_get(x + ip_re, eat_prompt = False)
        elif exp_nm:
            self.sh.expect_exact(x + exp_nm)

        x = 'RTA_IFP             : '
        if exp_ifp:
            #mac_re
            pass
        else:
            pass

        x = 'RTA_IFA             : '
        if exp_ifa:
            #eth0
            pass
        else:
            pass

        x = 'interface           : '
        if exp_if:
            pass
        else:
            pass

        x = 'flags               : <'
        if exp_flags:
            #UP DONE MASK CLONING STATIC >
            if isinstance(exp_flags, str):
                exp_flags = [exp_flags]

            flags = self.sh.expect_get(x + r'([\w ]+) >', eat_prompt = False).lower().split()
            for ef in exp_flags:
                if not ef.lower() in flags:
                    raise 'get_route: flag %s missing' % ef
        else:
            pass

        x = 'rtt,msec    rttvar  hopcount       MTU    expire'
        if exp_rtt_msec_rttvar_hopcount_mtu_expire:
            #rtt,msec    rttvar  hopcount       MTU    expire
            #       0         0         0         0         0
            pass
        else:
            pass

        self.sh.wait_prompt()
        return r


    def _add_del_route(self, dst, gw, dev, vr, family, add, cleanup,
                       cloning, succeed, reject, accounting, mpls_key,
                       blackhole, hopcount, down=False):
        ''' linux
        Use gw XOR dev.
        Netmask/prefixlen is set with addr/prefixlen, i.e. 10.1.1.1/8.
        cloning is always True on linux.
        '''
        #dst = ip(ip_and(dst.addr, dst.prefixlen) + '/'+ str(dst.prefixlen))
        if accounting and not add:
            self.ts.del_route((dst,gw,dev,vr,family))
        cmd = self.las_prefix(vr) + 'ip route '
        if add:
            cmd += 'add '
        else:
            cmd += 'del '

        if blackhole:
            cmd += 'blackhole '
        elif reject:
            cmd += 'prohibit '
        else:
            cmd += 'unicast '

        cmd += str(dst.mask(dst.prefixlen)) + ' '
        if gw:
            if hopcount != None:
            #weight is really the inverse of hopcount
                cmd += 'nexthop via ' + gw.addr
                weight = 1 + hopcount
                cmd += ' weight %d ' % weight
            else:
                cmd += 'via ' + gw.addr
        if dev:
            cmd += 'dev ' + dev.ifname + ' '

        if mpls_key:
            cmd += 'nh_proto mpls %s ' % mpls_key

        if cleanup:
            self.sh.send(cmd)
            self.sh.wait_prompt()
        else:
            if add:
                if succeed:
                    #self.sh.expect_prompt(cmd)
                    self.sh.send(cmd)
                    self.sh.wait_prompt()
                else:
                    self.sh.send(cmd)
                    self.sh.expect_exact('RTNETLINK answers: Network is unreachable')
                    self.sh.wait_prompt()
            else:
                self.sh.send(cmd)
                #self.sh.wait_prompt_not(['invalid', 'specified', 'unknown'])
                self.sh.wait_prompt()


        if accounting and add:
            self.ts.add_route((dst,gw,dev,vr,family))


    def del_arps(self, vr = 0, cleanup=False):
        self.ts.del_arps(vr)
        for ipv in 4,6:
            for perm in '',' nud permanent':
                self.sh.send(self.las_prefix(vr) + 'ip -%s neigh flush all' % ipv)
                #can return "Nothing to flush." here sometimes. anything else is wrong.
                self.sh.wait_prompt()


    def _list_addr(self, domain = '', vr = 0, dev = None, temporary = True, tentative = True):
        if domain == '4':
            ipv    = ' -4'
            names  = [ r'inet (%s)/(\w+)' % ip_re  ]
        elif domain == '6':
            ipv    = ' -6'
            names  = [ r'inet6 (%s)/(\w+)' % ip6_re ]
        else:
            ipv    = ''
            names  = [ r'inet6 (%s)/(\w+)' % ip6_re, r'inet (%s)/(\w+)' % ip_re ]

        if dev:
            dev = ' dev %s' % dev
        else:
            dev = ''

        addrs = self.sh.send_and_return_all(self.las_prefix(vr) + 'ip%s addr show%s' % (ipv, dev))
        found = []
        for addr in addrs:
            for name in names:
                m = re.match(name, addr)
                if m:
                    a = ip(m.group(1), m.group(2))
                    found.append(a)
                    break
        return found








    def list_arp(self, vr=0):
        for ipv in 4,6:
            self.sh.send(self.las_prefix(vr) + 'ip -%s neigh' % ipv)
            self.sh.wait_prompt_not(['unknown', 'Usage'])


    def list_arp_return_all(self, v6, vr=0):
        return self.sh.send_and_return_all(self.las_prefix(vr) + 'ip -%s neigh' % IF(v6,6,4))


    def _add_arp(self, ip2, mac, devname, vr):
        cmd = self.las_prefix(vr) + 'ip neigh add ' + ip2.addr + ' lladdr ' + mac
        if devname:
            cmd += ' dev ' + devname
        self.sh.expect_prompt(cmd)


    def _del_arp(self, ip2, mac, devname, vr, cleanup):
        cmd = self.las_prefix(vr) + 'ip neigh del ' + ip2.addr
        if mac:
            cmd += ' lladdr ' + mac
        cmd += ' dev ' + devname
        self.sh.expect_prompt(cmd, cleanup)



    def _verify_arp(self, v6, vr, succeed):
        a = self.sh.send_and_return_all(self.las_prefix(vr) + 'ip -%s neigh' % IF(v6,6,4))
        if v6:
            r = [re.match(r'neighbor add (%s) dev \S+ lladdr (%s)' % (ip6_re, mac_re), line).groups() for line in a]
        else:
            r = [re.match(r'neighbor add (%s) dev \S+ lladdr (%s)' % (ip_re, mac_re), line).groups() for line in a]

        return r


    def _ping(self, dst, succeed, src, packetsize, timeout, count,
              bypass_route, vr, icmp_replyer, use_ipping, retries,
              dont_frag, exp_ip, ttl, tos, timestamp, interval,
              at_least, interface, prefer_temporary_src_addr,
              hops):
        'packetsize = icmp header size (8) + payload.'
        packetsize = packetsize - 8
        switches = '-s %s ' % packetsize
        switches += '-c %s ' % count
        if timeout:
            if use_ipping:
                switches += '-w %d ' % (int(timeout) * 1000)
            else:
                switches += '-W %s ' % timeout

        if src and not dst.v6:
            switches += '-I ' + src.addr + ' '

        if not dst.v6 and dont_frag:
            if use_ipping:
                switches += '-D '
            else:
                switches += '-M want '

        if bypass_route:
            switches += '-r '

        if ttl != 64:
            switches += '-t %s ' % ttl

        if tos != 0:
            switches += '-Q %s ' % hex(tos)

        if timestamp:
            switches += '-T %s ' % timestamp

        if interval != 1000:
            switches += '-i %s ' % (interval / 1000.0)

        if interface != '' :
            switches += '-I %s ' % interface
        elif '%' in dst.addr:
            # The linux native ping6 command cannot handle the scope_id field
            # from the socket address. Scope_id must be passed as interface via '-I'
            switches += '-I %s ' % dst.addr.split('%')[1]
            dst.scope = None

        if prefer_temporary_src_addr:
            switches += '-T '

        cmd = IF(use_ipping, self.las_prefix(vr), self.__chvr(vr)) + 'ping%s -n %s%s' % (dst.v6, switches, dst.addr)

        if exp_ip:
            expipstr = re.escape(exp_ip.addr)
        else:
            expipstr = IF(dst.v6, ip6_re, ip_re)

        if use_ipping:
            success_match = r'Reply from (%s) .+' % expipstr + r'.*Reply from .+'*(at_least - 1)
        else:
            success_match = r"\w+ bytes from (%s):.+?" % expipstr + (r'.*?\w+ bytes from %s:.+?' %  IF(dst.v6, ip6_re, ip_re))*(at_least - 1)

        lst = [success_match,
               r'From \S+ icmp_seq=\w+ Destination Host Unreachable',
               r'%s packets transmitted, 0 received, 100%% packet loss,' % count,
               r'Resource temporarily unavailable',
               r'No route to host',
               r'Echo request operation failed: .* \(1006\)', # IP_ERRNO_EFIREWALL
               'Destination unreachable']
        target._ping_retrier(self, cmd, succeed, lst, retries, IF(exp_ip, exp_ip, dst)) #!!todo


    def list_route(self, vr = '', exp_entry = None, succeed = True):
        self.sh.send(self.las_prefix(vr) + 'ip route list router %s' % vr)
        #!!!todo incomplete remove?
        self.sh.wait_prompt()


    def __chvr(self, vr):
        'Returns the prefix needed on the command prompt in order to execute the command in a specific VR'
        if vr:
            return self.las_prefix() + 'chvr -n %d ' % int(vr)
        return ''


    def __generate_cmd_line_for_vr(self, cmd, vr):
        'Wraps built in commands (like echo) so it will be executed in the specified VR'
        if vr:
            cmd = self.__chvr(vr) + 'sh -c "' + cmd + '"'
        return cmd


    def __write_proc_node(self, node, value, vr=0, restore_at_cleanup=True):
        if value in ['yes', 'true', 'enable', 'enabled']:
            value = '1'
        if value in ['no', 'false', 'disable', 'disabled']:
            value = '0'

        if restore_at_cleanup:
            self.push_state_restorer(self.__write_proc_node, (node, self.__read_proc_node(node, vr), vr, False))
        self.sh.expect_prompt(self.__generate_cmd_line_for_vr('echo %s > %s' % (value, node), vr))


    def __read_proc_node(self, node, vr=0):
        output = self.sh.send_and_return_all(self.__generate_cmd_line_for_vr('cat %s' % node, vr))
        return output[0].strip('\0')

    def __ifname(self, netif):
        if netif == None:
            return 'default'
        return netif.ifname

    def __ifvr(self, netif):
        if netif == None:
            return '0'
        return netif.vr

    def __write_neigh_proc_node(self, netif, name, value, v6):
        self.__write_proc_node('/proc/sys/net/%s/neigh/%s/%s' % (IF(v6, 'ipv6','ipv4'), self.__ifname(netif), name), value, self.__ifvr(netif))

    def __write_conf_proc_node(self, netif, name, value, v6):
        self.__write_proc_node('/proc/sys/net/%s/conf/%s/%s' % (IF(v6, 'ipv6','ipv4'), self.__ifname(netif), name), value, self.__ifvr(netif))

    def __write_icmp_proc_node(self, netif, name, value, v6):
        self.__write_proc_node('/proc/sys/net/%s/icmp/%s' % (IF(v6, 'ipv6','ipv4'), name), value, self.__ifvr(netif))

    def configure_ipv4_auto_proxy_arp(self, netif, enable):
        self.__write_conf_proc_node(netif,'auto_proxy_arp', IF(enable, '1', '0'), False)

    def configure_ipv4_delete_address_on_dup_detect(self, netif, enable):
        self.__write_conf_proc_node(netif,'delete_address_on_dup_detect', IF(enable, '1', '0'), False)

    def configure_ipv4_dont_forward_broadcast(self, netif, enable):
        self.__write_conf_proc_node(netif,'dont_forward_broadcast', IF(enable, '1', '0'), False)

    def configure_ipv4_icmp_ignore_broadcast(self, netif, enable):
        self.__write_conf_proc_node(netif,'icmp_ignore_broadcast', IF(enable, '1', '0'), False)

    def configure_ipv4_network_proxy_arp(self, netif, enable):
        self.__write_conf_proc_node(netif,'network_proxy_arp', IF(enable, '1', '0'), False)

    def configure_ipv4_send_gratuitous_arp(self, netif, enable):
        self.__write_conf_proc_node(netif,'send_gratuitous_arp', IF(enable, '1', '0'), False)

    def configure_ipv6_accept_ra(self, netif, enable):
        self.__write_conf_proc_node(netif, 'forwarding', IF(enable, '0', '1'), True)
        self.__write_conf_proc_node(netif, 'accept_ra', IF(enable, '1', '0'), True)

    def configure_ipv6_allow_rthdr0(self, netif, enable):
        self.__write_conf_proc_node(netif, 'allow_rthdr0', IF(enable, '1', '0'), True)

    def configure_ipv6_dup_addr_detect_transmits(self, netif, value):
        self.__write_conf_proc_node(netif, 'dad_transmits', value, True)

    def configure_ipv6_privacy_extensions(self, netif, enable, regen_advance):
        self.__write_conf_proc_node(netif, 'enable_privacy_extensions', IF(enable, '1', '0'), True)
        self.__write_conf_proc_node(netif, 'regenerate_advance', regen_advance, True)

    def configure_ipv6_rt_solicitation_count(self, netif, value):
        self.__write_icmp_proc_node(netif,'router_solicit_count',value, True)

    def configure_ipv6_rt_solicitation_max_interval(self, netif, value):
        self.__write_icmp_proc_node(netif, 'router_solicit_max_interval', value, True)

    def configure_mcast_min_report_delay(self, value):
        self.__write_proc_node('/proc/sys/net/ipnet/mcast_min_report_delay', value)

    def configure_neigh_linger_time(self, netif, value, v6):
        self.__write_neigh_proc_node(netif,'linger_time',value, v6)

    def configure_neigh_max_unicast_solicit(self, netif, value, v6):
        self.__write_neigh_proc_node(netif, 'ucast_solicit', value, v6)

    def configure_neigh_max_multicast_solicit(self, netif, value, v6):
        self.__write_neigh_proc_node(netif, 'mcast_solicit', value, v6)

    def configure_neigh_max_application_solicit(self, netif, value, v6):
        self.__write_neigh_proc_node(netif, 'app_solicit', value, v6)

    def configure_neigh_max_pending(self, netif, value, v6):
        self.__write_neigh_proc_node(netif,'max_pending',value, v6)

    def configure_route_max_clone_count(self, value):
        self.__write_proc_node('/proc/sys/net/ipnet/route_max_clone_count', value)

    def configure_send_redirect(self, netif, value, v6):
        self.__write_conf_proc_node(netif, 'send_redirects', value, v6)

    def configure_tcp_connection_timeout(self, timeout):
        self.__write_proc_node('/proc/sys/net/ipnet/tcp/connection_timeout', timeout)

    def configure_tcp_allow_tiny_window(self, allow):
        self.__write_proc_node('/proc/sys/net/ipnet/tcp/allow_tiny_window', IF(allow, '1', '0'))

    def configure_tcp_disable_land_attack(self, value):
        self.__write_proc_node('/proc/sys/net/ipnet/tcp/disable_LAND_attack', value)

    def configure_tcp_max_retransmits(self, value):
        self.__write_proc_node('/proc/sys/net/ipnet/tcp/max_retransmits', value)

    def configure_tcp_timestamp(self, enable):
        self.__write_proc_node('/proc/sys/net/ipnet/tcp/time_stamp', IF(enable, '1', '0'))

    def configure_tcp_urg_rfc1122(self, enable):
        self.__write_proc_node('/proc/sys/net/ipnet/tcp/rfc1122_urg_data', IF(enable, '1', '0'))

    def flush_ipsec(self):
        all = self.sh.send_and_return_all(self.las_prefix() + 'keyadm flush')
        if len(all) == 1: #command not found
            self.sh.expect_prompt(self.las_prefix() + 'setkey -F')

    def n_ipsec_sa(self):
        v = self.sh.send_and_return_all(self.las_prefix() + 'keyadm dump')
        if len(v) == 1: #command not found
            v = self.sh.send_and_return_all(self.lasprefix() + 'setkey -D')
            return len(v)/11
        return len(v)/6


    def dns(self, nr=1, vr=0):
        'nr=1 primary, 2=secondary'
        ns = self.sh.send_and_return_all('grep \^nameserver /etc/resolv.conf').split()
        if nr == 1:
            if len(ns) > 0:
                return ns[0]
            else:
                return ''
        elif nr == 2:
            if len(ns) > 1:
                return ns[1]
            else:
                return ''
        raise engine_error('nr=%s'%s)


    def syslog(self, msg):
        pass

    def reboot(self):
        pass


class lkm(linux):
    'LKM target'
    def init(self, opt):
        linux.init(self, opt)
        self.type = 'lkm'
        self.use_sftp = True

class fos(linux):
    def init (self, opt):
        linux.init(self, opt)
        ##
        self.fos_vswitch  = {}
        self.fos_vrs      = {}
        self.fos_netpairs = {}
        self.use_sftp = True

    def flush_ipsec(self):
        pass

    def add_vr(self, nr): #!!! add 127.0.0.1 and v6 (::?) and up() if some flag set, "setup=True"?
        "Add virtual router"
        raise engine_error('log.start: fos must have VRs pre-added')

    def _del_vr(self, nr, cleanup=False):
        raise engine_error('log.start: fos cant delete VR')

    def add_fos_vswitch(self, num, vswitch):
        self.fos_vswitch[num] = vswitch

    def get_fos_vswitch(self, num):
        return self.fos_vswitch[num]

    def add_fos_vr(self, vr, t):
        self.fos_vrs[vr] = t

    def get_fos_vr(self, vr):
        return fos_vrs[vr]

    def add_fos_netpair(self, proxy, local, remote):
        self.fos_netpairs[proxy] = (local, remote)

    def get_fos_netpair(self, proxy):
        return self.fos_netpairs[proxy]

    def netpair_peer_ip(self, proxy=None, v6=''):
        if not proxy:
            proxy = self.fos_netpairs.keys()[0]
        (_, remote) = self.fos_netpairs[proxy]
        return remote.ip(v6=v6)

    def netpair_local_ip(self, proxy=None, v6=''):
        if not proxy:
            proxy = self.fos_netpairs.keys()[0]
        (local, _) = self.fos_netpairs[proxy]
        return local.ip(v6=v6)

    def configure_ipv4_send_gratuitous_arp(self, netif, enable):
        pass


class fos_telnet(fos):
    'FOS target'
    def init(self, opt):
        fos.init(self, opt)
        self.type = 'fos_telnet'

class fos_main(fos):
    'FOS target'
    def init(self, opt):
        fos.init(self, opt)
        self.type = 'fos_main'

class fos_vr(fos):
    'FOS target'
    def init(self, opt):
        fos.init(self, opt)
        self.type = 'fos_vr'

class fos_vswitch(fos):
    'FOS VSWITCH target'
    def init(self, opt):
        fos.init(self, opt)
        self.type = 'fos_vswitch'


################################################################################
#                       freebsd target
################################################################################
class freebsd(linux):
    'FreeBSD target'

    def init_clean_vlan(self):
        ls = self.sh.send_and_return_all('ifconfig -a', strip_lines=False)
        vlans = [re.match('(vlan\S+):', line).group(1) for line in ls if line[:4] == 'vlan']
        for vlan in vlans:
            self.sh.send_and_wait_prompt('ifconfig %s down' % vlan)
            self.sh.send_and_wait_prompt('ifconfig %s destroy' % vlan)

    def init(self, opt):
        self.init_clean_vlan()
        target.init(self, opt)
        self.type = 'freebsd'
        self.use_sftp = False
        self.ftp_user = self.sh.s.user
        self.ftp_passwd = self.sh.s.passwd
        self.use_sftp = False

    def _add_netif(self, *a, **k):
        x = netif_freebsd(self)
        x.new(*a, **k)
        return x

    def _create_netif(self):
        return netif_freebsd(self)

    def _gather_existing_ifs(self, vr=0):
        'see iptarget comments'
        all = self.sh.send_and_return_all(self.las_prefix(vr) + "ifconfig -a")

        ifs = []
        if_name    = ''
        inet_addr  = ''
        inet_mask  = ''
        inet_bc    = ''
        inet6_addr = ''
        inet6_mask = ''
        inet6_bc   = ''
        mac        = ''
        media      = ''
        status     = ''
        ips = {}

        for line in all:
            #print line
            if_match     = re.match(r'(\S+): flags=[0-9]+<UP,([A-Z]+),', line)
            mac_match    = re.match(r'ether (\S+)', line)
            inet_match   = re.match(r'inet (\S+) netmask (\S+).*', line)
            inet6_match  = re.match(r'inet6 (\S+) prefixlen (\S+) .* (\S+)', line)
            media_match  = re.match(r'media: (\S+)', line)
            status_match = re.match(r'status: (\S+)', line)

            if if_match:

                if if_name:
                    if media == 'Ethernet':
                        media = 'eth'
                    if if_type == 'LOOPBACK':
                        media = 'loopback'

                    ifs.append((if_name, vr, ips, mac, media, None, None, None))

                    if_name    = ''
                    inet_addr  = ''
                    inet_mask  = ''
                    inet_bc    = ''
                    inet6_addr = ''
                    inet6_mask = ''
                    inet6_bc   = ''
                    mac        = ''
                    media      = ''
                    status     = ''
                    ips = {}

                if_name = if_match.group(1)
                if_type = if_match.group(2)


            if mac_match:
                mac = mac_match.group(1)

            #if line.find("inet") == 0:
            #    params = line.split(" ")
            #    for i in range(0:len(params)
            #        if params[i] == 'inet':
            #            inet_addr = params[i+1]
            #        if params[i] == 'netmask':
            #            inet_mask = params[i+1]
            #        if params[i] == 'broadcast':
            #            inet_bc = params[i+1]

            if inet_match:
                inet_addr = inet_match.group(1)
                inet_mask = inet_match.group(2)
                #inet_bc   = inet_match.group(3)
                ips[ip(inet_addr + '/%s' % 16)] = True
            if inet6_match:
                inet6_addr   = inet6_match.group(1)
                inet6_prefix = inet6_match.group(2)
                inet6_bc     = inet6_match.group(3)
                ips[ip(inet6_addr + '/%s' % inet6_prefix)] = True
            if media_match:
                media = media_match.group(1)
            if status_match:
                status = status_match.group(1)

        #Add the final interface
        if if_name:
            if media == 'Ethernet':
                media = 'eth'
            if if_type == 'LOOPBACK':
                media = 'loopback'

            ifs.append((if_name, vr, ips, mac, media, None, None, None))

        return ifs

    def list_route(self, vr = '', exp_entry = None, succeed = True):
        self.sh.send('netstat -r')
        #!!!todo incomplete remove?
        self.sh.wait_prompt()

################################################################################
#    the ipcom shell "socktest" command made to look like an object
#    (the more like python sockets the better)
#                                _    _            _
#                 ___  ___   ___| | _| |_ ___  ___| |_
#                / __|/ _ \ / __| |/ / __/ _ \/ __| __|
#                \__ \ (_) | (__|   <| ||  __/\__ \ |_
#                |___/\___/ \___|_|\_\\__\___||___/\__|
#
################################################################################
class socktest(object):
    """
    Instances of sockettest are returned from target.ipcom_shell().socket()
    This requires ipout running in userspace on the lkm or the userspace ipnet ipout on unix/linux
    """
    def __init__(self, a_target, domain, type, proto=0, succeed = True):
        self.t = a_target
        if domain == 0:
            # 'type' contains the socket file descriptor. This use to
            # create multiple socket instances that map against the
            # same underlying socket on the target.
            self.sock = type
        else:
            lines = self.t.sh.send_and_return_all('socktest open -d %s -t %s -p %s' % (domain, type, proto))
            m = re.match(r'Socket = ([0-9]+)', lines[-1])

            if m == None:
                # Socket creation failed
                if succeed:
                    raise test_fail("sock_open didn't succeed even though it should have: domain %s, type %s, proto %s." % (domain, type, proto))
                return
            self.sock = int(m.group(1))

        self.t.ts.sockets.append(self)
        if succeed:
            return
        self.close()
        raise test_fail("sock_open succeeded when it shouldn't have: socknr %s, domain %s, type %s, proto %s." % (sock, domain, type, proto))


    def close(self, cleanup = False):
        'close socket. runs a "socktest close -s <sockno>"'
        retval = 0
        try:
            self.t.ts.sockets.remove(self)
        except ValueError:
            self.sh.s.log('X'*80, True)
            self.sh.s.log(self.t.sh.s.name + ': _sock_close() broken: %s not in list containing: %s' % (self.sock, self.t.ts.sockets), True)
            self.sh.s.log('X'*80, True)

        try:
            if self.fsock:
                try:
                    self.fsock._flood_stop()
                except:
                    pass
                try:
                    self._flood_stop()
                except:
                    pass
        except:
            pass

        response = 'Socket %s closed' % self.sock

        if cleanup:
            try:
                self.setsockopt('socket', 'linger', 0, cleanup)
            except KeyboardInterrupt:
                raise
            except:
                pass
            response = [ response, 'Failed, bad socket number']

        self.t.sh.send('socktest close -s %s' % self.sock)
        try:
            self.t.sh.expect_exact(response)
            self.t.sh.wait_prompt()
        except TIMEOUT:
            if cleanup:
                pass
            else:
                raise

        return retval


    def bind(self, addr='', port=None, devname='', succeed = True, error = None):
        """If no addr/port specified, these will be allocated for you.
        If succeed=False and error is specified, this error must match."""
        #!!need vr here. do it with setopt
        if addr:
            addr=ip(addr)
            addr = ' -a %s' % addr.addr
        if port == None:
            port = ''
        else:
            port = ' -p %s' % str(port)
        if devname:
            devname = ' -i %s' % devname
        sh = self.t.sh
        sh.s.log('sock_bind: expecting ' + ('failure', 'success')[int(succeed)])
        sh.send('socktest bind -s %s%s%s%s' % (self.sock, addr, port, devname))
        ls = ['Socket %s bound' % self.sock,
              sh.EADDRINUSE,
              sh.EOPNOTSUPP,
              sh.EINVAL,
              sh.EADDRNOTAVAIL
              ]
        i = sh.expect_exact(ls)
        sh.wait_prompt()
        if (succeed ^ i == 0) or ((not succeed) and error and (ls[i] != error)):
            raise test_fail('%s.sock_bind: "%s%s"' % (sh.s.name, ls[i], sh.s.s.before))


    def listen(self, backlog = ''):
        if backlog != '':
            backlog = ' -b %s' % backlog
        self.t.sh.send('socktest listen -s %s%s' % (self.sock, backlog))
        self.t.sh.expect_exact('Socket %s listens' % self.sock)
        self.t.sh.wait_prompt()


    def select(self, msocks, repeat='', timeout=''):
        """Runs select on the msocks argument which can be either
        a socket.fileno() number or a list of these. either will be treated
        as read-sets for select.
        A dict can also be specified with 'r','w','x' as keys and value as socketlist
        'repeat' is standard socktest argument
        (the self.fileno() is NOT included)"""
        if isinstance(msocks,dict):
            rset = msocks.get('r', ())
            wset = msocks.get('w', ())
            xset = msocks.get('x', ())
        elif isinstance(msocks,list) or isinstance(msocks,tuple):
            rset = msocks
            wset = ()
            xset = ()
        else:
            rset = (msocks,)
            wset = ()
            xset = ()

        socks = ''
        for r in rset:
            socks = socks + ' -r %s' % r
        for w in wset:
            socks = socks + ' -w %s' % w
        for x in xset:
            socks = socks + ' -x %s' % x
        if repeat != '':
            repeat = ' -N %s' % repeat
        if timeout != '':
            timeout = ' -t %s' % timeout
        self.t.sh.send('socktest select' + socks + repeat + timeout)


    def _select_verify_ready_fd(self, etype, msocks):
        "etype: 'R', 'W' or 'X' for read-set, write-set or exception-set"
        num = 0
        estr = etype + ':'
        if msocks:
            # msocks must be sorted since the stack will always return
            # the ready sockets in numerical order
            msocks = list(msocks)
            msocks.sort()
            for fd in msocks:
                estr += str(fd) + ','
                num += 1
        if estr[-1] == ',':
            estr = estr[:-1]
        estr += '-'
        self.t.sh.expect_exact(estr)
        return num


    def select_post(self, msocks):
        "Verify sockets 'msocks' are ready."
        num = 0
        num += self._select_verify_ready_fd('R', msocks.get('r'))
        num += self._select_verify_ready_fd('W', msocks.get('w'))
        num += self._select_verify_ready_fd('X', msocks.get('x'))
        self.t.sh.expect_exact('Returned %d' % num)
        self.t.sh.wait_prompt()


    def accept_pre(self):
        'listens'
        self.t.sh.send('socktest accept -s %s' % self.sock)


    def accept_post(self):
        'returns a new socket'
        s = int(self.t.sh.expect_get(r'Socket = ([0-9]+)[^0-9]', eat_prompt = False)) # if failure here, its probably "Failed, socktest socket list full"
        self.t.sh.expect_exact('Socket %s accepted' % self.sock)
        self.t.sh.wait_prompt()
        import copy
        ss = copy.copy(self)
        ss.sock = s
        self.t.ts.sockets.append(ss)
        return ss


    def accept(self):
        self.accept_pre()
        return self.accept_post()


    def connect_pre(self, addr, port, domain='', flowinfo=None):
        'tries to connect to addr/port'
        addr = ip(addr)
        if domain:
            domain = ' -d ' + domain
        if flowinfo == None:
            fli = ''
        else:
            fli = ' -F %d' % flowinfo
        self.t.sh.send('socktest connect -s %s -a %s -p %s%s%s' % (self.sock, addr.addr, port, domain, fli))


    def connect_post(self, succeed=True, error=None):
        'checks for success'
        if error:
            i = self.t.sh.expect_exact([error])
        else:
            i = self.t.sh.expect_exact(["Socket %s connected" % self.sock,
                                        self.t.sh.EINPROGRESS,
                                        self.t.sh.ETIMEDOUT,
                                        self.t.sh.ECONNREFUSED,
                                        self.t.sh.EHOSTUNREACH,
                                        self.t.sh.EINVAL])
        if succeed and i not in (0, 1):
            raise test_fail('sock_sock_connected: succeed/non-succeed')
        self.t.sh.wait_prompt()


    def connect(self, addr, port, domain='', succeed=True, flowinfo=None, error=None):
        self.connect_pre(addr, port, domain, flowinfo)
        self.connect_post(succeed, error)


    def connect_and_accept(self, ssocket, sip, sport):
        '''
        "self" connects to the ip at the server address "sip" at port sport.
        returns the new socket as accepted by the server "ssocket"
        '''
        sip = ip(sip)
        self.connect_pre(sip, sport)
        ssocket.accept_pre()
        self.connect_post()
        return ssocket.accept_post()


    def send(self, data, addr='',
             port='', flags='', succeed=True,
             oob = '', more = '', error = None,
             send_data_count = 1, hw_addr='',
             ancillary_data=None, zerocopy = False,
             sctp_mode = '', flowinfo=None):
        '''
        send data on the socket
        "data" is a string.
        addr/port is useful for unconnected sockets.
        oob and more can be set to True
        flags socktest standard
        error: what to expect in case of succeed=False
        send_data_count: repeat n times
        '''
        switches = ''
        if flags:
            switches += ' -f %s' % flags
        if addr:
            addr = ip(addr)
            switches += ' -a ' + addr.addr
        if hw_addr:
            switches += ' -a ' + hw_addr
        if port:
            switches += ' -p %s' % port
        if oob:
            switches += ' -o'
        if more:
            switches += ' -m'
        if sctp_mode:
            switches += ' -c %s' % sctp_mode
        if flowinfo:
            switches += ' -F %d' % flowinfo
        if data[:2] == '0x':
            data_len = len(data[2:]) / 2
        else:
            data_len = len(data)
        if ancillary_data:
            if ancillary_data.has_key('packetinfo'):
                # Packet info is a list of [<ifname>,<src_addr>] where
                # an empty string ifname or source address means: not
                # specified
                pktinfo = ancillary_data['packetinfo']
                switches += ' -P {%s,%s}' % (IF(pktinfo[0], pktinfo[0], ''),
                                             IF(pktinfo[1], pktinfo[1], ''))
            if ancillary_data.has_key('sndrcvinfo'):
                sndrcvinfo = ancillary_data['sndrcvinfo']
                switches += ' -i {%s,%s,%s,%s,%s,%s,%s,%s,%s,%s}' % \
                            (IF(sndrcvinfo[0], sndrcvinfo[0], '0'),
                             IF(sndrcvinfo[1], sndrcvinfo[1], '0'),
                             IF(sndrcvinfo[2], sndrcvinfo[2], '0'),
                             IF(sndrcvinfo[3], sndrcvinfo[3], '0'),
                             IF(sndrcvinfo[4], sndrcvinfo[4], '0'),
                             IF(sndrcvinfo[5], sndrcvinfo[5], '0'),
                             IF(sndrcvinfo[6], sndrcvinfo[6], '0'),
                             IF(sndrcvinfo[7], sndrcvinfo[7], '0'),
                             IF(sndrcvinfo[8], sndrcvinfo[8], '0'),
                             IF(sndrcvinfo[9], sndrcvinfo[9], '0'))
        sendcmd = IF(zerocopy, "zerocopy_send", "send")

        self.t.sh.send('socktest %s -s %s -r %d -d "%s"' % (sendcmd, self.sock, send_data_count, data) + switches)
        if error:
            if isinstance(error, list):
                expect_list = ['this wont match'] + error
            else:
                expect_list = ['this wont match', error]
            i = self.t.sh.expect_exact(expect_list)
        else:
            i = self.t.sh.expect_exact(['Sent %d bytes' % (int(data_len) * send_data_count),
                                        self.t.sh.EDESTADDRREQ,
                                        self.t.sh.EISCONN,
                                        self.t.sh.ECONNREFUSED])
        self.t.sh.wait_prompt()
        if (i == 0) ^ succeed:
            raise test_fail('')


    def recv_pre(self, max_len='', waitall=False, oob=False, show_from_addr=False, peek=False,
                 dont_wait=False, zerocopy=False, sctp=False, split_buffer=False):
        """waits for receive
        see socktest help for -l, -w, -o, -A"""
        if max_len != '':
            max_len = ' -l %s' % max_len
        waitall = IF(waitall, ' -w', '')
        oob = IF(oob, ' -o', '')
        peek = IF(peek, ' -P', '')
        dont_wait = IF(dont_wait, ' -N', '')
        show_from_addr = IF(show_from_addr, ' -A', '')
        recvcmd = IF(zerocopy, "zerocopy_recv", "receive")
        sctp = IF(sctp, ' -c', '')
        split_buffer = IF(split_buffer, ' -S', '')
        self.t.sh.send('socktest %s -s %s%s%s%s%s%s%s%s%s'
                       % (recvcmd, self.sock, max_len, waitall, oob, show_from_addr, peek, dont_wait, sctp, split_buffer))
        self.t.sh.expect_exact('Waiting to receive')


    def recv_post(self, exp_len = None, exp_type = None, exp_code = None, exp_data = None,
                  succeed = True, error = 'timeout',
                  ancillary_data=None,
                  exp_pattern=None, icmpv6=None):
        """Parses the output.
        For succeed = False, the type of "error" can be 'timeout', 'silence', 'eagain' or an errno
        All exp_ values will (if set) be matched against output.
        exp_len: nr of bytes must be received
        exp_type/code: for ICMP match
        exp_data: needs this exact data.
        ancillary_data: 3 values for level=%s type=%s data=%s
        exp_pattern: weaker version of exp_data, can be RE"""
        if not succeed:
            if error == 'timeout':
                self.t.sh.expect_exact('Failed, errno: ' + self.t.sh.ETIMEDOUT)
                self.t.sh.wait_prompt()
                return
            elif error == 'silence':
                self.t.sh.expect_not("Received")
                return
            elif error == 'eagain':
                self.t.sh.expect_exact(['Failed, errno: ' + self.t.sh.EAGAIN,
                                        'Failed, errno: ' + self.t.sh.EWOULDBLOCK])
                self.t.sh.wait_prompt()
                return
            else: #all errno crap
                self.t.sh.expect_exact('Failed, errno: ' + error)
                self.t.sh.wait_prompt()
                return

        got = ''
        if self.t.sh.s.dry:
            return got

        if ancillary_data:
             self.t.sh.expect_exact('Ancillary data')
             self.t.sh.expect_re('level=%s, type=%s, data=%s' % tuple(ancillary_data))

        if exp_data == None:
            if exp_len == None:
                got = int(self.t.sh.expect_get('Received ([0-9]+) bytes', eat_prompt = False))
            else:
                self.t.sh.expect_exact('Received %s bytes' % exp_len)
        else:
            self.t.sh.expect_exact('Received %s bytes' % len(exp_data))

        if exp_type != None and exp_code != None:
            while True:
                if icmpv6:
                    self.t.sh.expect_exact('ICMPv6 HEADER')
                else:
                    self.t.sh.expect_exact('ICMP HEADER')
                i = self.t.sh.expect_re([r'Type\s*: 0x%02x\s+Code\s*: 0x%02x' % (exp_type, exp_code),
                                         r'Type\s*: 0x[0-9a-f][0-9a-f]\s+Code\s*: 0x[0-9a-f][0-9a-f]'],
                                        timeout = 3)
                if i == 0:
                    break

        if exp_pattern == None:
            exp_pattern = exp_data

        if exp_pattern != None:
            self.t.sh.expect_re(exp_pattern)
        self.t.sh.wait_prompt()
        return got


    def recv(self, exp_len=None, exp_type=None,
             exp_code=None, max_len='', exp_data=None,
             succeed=True, waitall=False, error='timeout',
             oob=False, show_from_addr=False, ancillary_data=None,
             peek=False, dont_wait=False, exp_pattern=None,
             sctp=False, split_buffer=False, icmpv6=None):
        'receive data on socket and returns amount of data gotten'
        self.recv_pre(max_len, waitall, oob, show_from_addr, peek, dont_wait, sctp=sctp, split_buffer=split_buffer)
        return self.recv_post(exp_len, exp_type, exp_code, exp_data, succeed, error=error, ancillary_data=ancillary_data, exp_pattern=exp_pattern, icmpv6=icmpv6)


    def getpeername(self, v6='', succeed=True):
        "returns ip and port"
        self.t.sh.send('socktest getpeername -s %s' % self.sock)
        if succeed:
            m = self.t.sh.expect_get(r'Peer: (%s)\.([0-9]+)[^0-9]' % IF(v6, ip6_re, ip_re))
            return ip(m[0]), int(m[1])
        else:
            self.t.sh.expect_exact(self.t.sh.ENOTCONN)
            self.t.sh.wait_prompt()


    def getsockname(self, v6=''):
        "returns (ip,port) of socket address"
        self.t.sh.send('socktest getsockname -s %s' % self.sock)
        m = self.t.sh.expect_get(r'Name: (%s)\.([0-9]+)[^0-9]' % IF(v6, ip6_re, ip_re)) #'[0-9A-Fa-f:]+(%\w+)?'
        return ip(m[0]), int(m[-1])


    def setsockopt(self, level, option, data, cleanup = False, timeout = -1, error = None):
        """
        Just like socktest socktest command except the
        'add_membership', 'drop_membership', 'join_group', 'leave_group' options require
        data members which are tuples of 2 values
        """
        if option in ['add_membership', 'drop_membership', 'join_group', 'leave_group']:
            x, y = data
            if isinstance(x,ip):
                x = x.addr
            if isinstance(y,ip):
                y = y.addr
            if level == 'ip':
                strdata = '{%s,%s,0,0}' % (x, y)
            else:
                strdata = '{%s,%s}' % (x, y)
        elif option in ['mrt_add_vif', 'mrt_del_vif']:
            strdata = '%d,%s,%s' % data
        elif option in ['mrt6_add_mif', 'mrt6_del_mif']:
            strdata = '%d,%s' % data
        elif option in ['mrt_add_mfc', 'mrt_del_mfc', 'mrt6_add_mfc', 'mrt6_del_mfc']:
            saddr, maddr, invif, outvifs = data
            strdata = '%s,%s,%d' % (saddr, maddr, invif)
            for outvif in outvifs:
                strdata += ',%d' % outvif
        elif isinstance(data, bool):
            strdata = IF(data, '1', '0')
        else:
            strdata = data

        self.t.sh.send('socktest setopt -s %s -l %s -o "%s=%s"' % (self.sock, level, option, strdata))
        e = 'Socket %s options set' % self.sock
        if cleanup:
            e = [e, 'Failed, errno: S_errno_EOPNOTSUPP', 'Failed, errno: Operation not supported', 'Failed, bad socket number']
        if error:
            e = [e, 'Failed, errno: ' + error ]
        self.t.sh.expect_exact(e, timeout)
        self.t.sh.wait_prompt()


    def getsockopt(self, level, option, exp_data = None):
        "if exp_data given, require this to match, else the sockopt value is returned"
        self.t.sh.send('socktest getopt -s %s -l %s -o %s' % (self.sock, level, option))
        if exp_data != None:
            self.t.sh.expect_re(exp_data)
            self.t.sh.wait_prompt()
            return
        return self.t.sh.expect_get('\r\n\s+(\S+)\s*\r\n')


    def shutdown(self, shut_read=True, shut_write=True):
        "socket shutdown"
        if shut_read == True and shut_write == True:
            how = ""
        else:
            how = '%s%s' % (IF(shut_read, ' -r', ''), IF(shut_write, ' -w', ''))
        self.t.sh.send('socktest shutdown -s %s%s' % (self.sock, how))
        self.t.sh.expect_exact("Success")
        self.t.sh.wait_prompt()


    def ioctl(self, option, value = '', netif = None, succeed = True):
        "see socktest ioctl for options"
        if netif:
            iff = ' -i %s' % netif.ifname
        else:
            iff = ''

        ioctl_str_with_val = 'socktest ioctl -s %s -o %s=%s' % (self.sock, option, value)

        if option == 'siocgifconf':
            ifconf = {}
            for line in self.t.sh.send_and_return_all(ioctl_str_with_val):
                ifname, addr_type, addr = line.split(' ')
                if not ifconf.has_key(ifname):
                    ifconf[ifname] = {}
                if not ifconf[ifname].has_key(addr_type):
                    ifconf[ifname][addr_type] = []
                ifconf[ifname][addr_type].append(addr)
            return ifconf

        if option in ('siocgetvifcnt', 'siocgetsgcnt', 'siocgetmifcnt_in6', 'siocgetsgcnt_in6'):
            res = self.t.sh.send_and_return_all(ioctl_str_with_val)[0]
            if res.find('Failed') >= 0:
                return res.strip()
            return dict(reduce(lambda acc, pair: acc + [pair.split('=')], res.split(' '), []))

        if option in ('siocatmark', 'siocinq', 'siocoutq', 'siocgpgrp', 'siocgdebug', 'fionread'):
            # ioctls which return an int
            self.t.sh.send('socktest ioctl -s %s -o %s' % (self.sock, option))
            return int(self.t.sh.expect_get('.*?    ([0-9]+)\s'))

        if option in ('siocxdscreate'):
            self.t.sh.send(ioctl_str_with_val)
            return int(self.t.sh.expect_get('.*?    ([0-9]+)\s'))

        if option in ('fionbio', 'siocxdsdestroy', 'siocxadsmap', 'siocxddsmap', 'siocsintr', 'siocsdebug'):
            # ioctl:s that takes an integer
            self.t.sh.send_and_wait_prompt(ioctl_str_with_val)
        elif option not in ('siocgarp', 'siocgifbrdaddr', 'siocgifaddr', 'siocgifnetmask'):
            self.t.sh.expect_prompt('socktest ioctl -s %s%s -o %s=%s' % (self.sock, iff, option, value))
        else:
            if option == 'siocgarp':
                i = 1 # Which means 'matched Failed'
                for line in self.t.sh.send_and_return_all('socktest ioctl -s %s%s -o %s=%s' % (self.sock, iff, option, value)):
                    m = re.match(r'\{%s,(%s),\d+\}' % (re.escape(value), mac_re), line)
                    if m:
                        return m.group(1)

            if option in ('siocgifbrdaddr', 'siocgifaddr', 'siocgifnetmask'):
                lines = self.t.sh.send_and_return_all('socktest ioctl -s %s -i %s -o %s' % (self.sock, netif.ifname, option))
                # The ioctl will always return one line
                line = lines[0]

                m = re.match(r'(%s)' % ip_re, line)
                if m:
                    i = 0
                else:
                    m = re.match(r'Failed(.*)', line)
                    i = 1
                v = m.group(1)

            if i == 0 and succeed:
                return v
            if (i == 0 and not succeed) or (i == 1 and succeed):
                raise test_fail('sock_ioctl: s %s, o %s, v %s, iff %s, succeed %s' % (self.sock, option, value, netif.ifname, succeed))


    def flood_start(self, ssock, burst = False, burst_size = 10240):
        ssock.t.sh.expect_prompt('socktest flood sink -s %s' % (ssock.sock))
        if burst:
            self.t.sh.expect_prompt('socktest flood burst -s %s -b %d' % (self.sock, burst_size))
        else:
            self.t.sh.expect_prompt('socktest flood source -s %s -b %d' % (self.sock, burst_size))


    def _flood_stop(self):
        self.fsock = None
        self.t.sh.send('socktest flood stop -s %s -w 180' % (self.sock))
        byte = self.t.sh.expect_get(r'Success, (\d+) bytes processed', timeout = 200)
        return byte


    def flood_stop(self):
        fsock = self.fsock

        # Close down the sender first.
        cbyte = self._flood_stop()
        sbyte = fsock._flood_stop()

        if int(sbyte) == 0 or int(cbyte) == 0:
            raise test_fail('sock flood no data sent')

        if cbyte != sbyte:
            raise test_fail('sock flood bytes mismatch %s vs %s' % (cbyte, sbyte))

        return cbyte


    def flood_verify(self, burst_size = 10240):
        self.t.sh.send('socktest flood verify -s %s -w 180 -b %d' % (self.sock, burst_size))
        byte = self.t.sh.expect_get(r'Success, (\d+) bytes processed', timeout = 200)
        return byte


    def fileno(self):
        "the socket fd number"
        return self.sock

    def get_shell_session(self):
        return self.t


    def sctp_bindx(self, addrs='', port=None, flag='A', succeed = True, error = None):
        """Must specified addr/port.
           If succeed=False and error is specified, this error must match."""
        #!!need vr here. do it with setopt

        if addrs: # split with ','
            if ':' in addrs: # IPv6
                addrs = ' -A %s' % addrs
            else:
                addrs = ' -a %s' % addrs
        else:
            self.t.sh.s.log('sctp_bindx: expecting address.')
            return

        if port == None:
            self.t.sh.s.log('sctp_bindx: expecting port.')
            return
        else:
            port = ' -p %s' % str(port)

        flag = ' -f %s' % flag

        self.t.sh.s.log('sctp_bindx: expecting ' + ('failure', 'success')[int(succeed)])
        self.t.sh.send('socktest sctp_bindx -s %s%s%s%s' % (self.sock, addrs, port, flag))
        ls = ['Socket %s bound' % self.sock,
              'Address already in use',
              'Operation not supported',
              'Invalid argument',
              "Can't assign requested address"]
        i = self.t.sh.expect_exact(ls)
        self.t.sh.wait_prompt()
        if (succeed ^ i == 0) or ((not succeed) and error and (ls[i] != error)):
            raise test_fail('%s.sctp_bindx: "%s%s"' % (self.t.sh.s.name, ls[i], self.t.sh.s.s.before))


    def sctp_connectx_pre(self, addrs, port):
        'tries to sctp_connectx to addrs/port'
        if ':' in addrs:
            v6 = '-A'
        else:
            v6 = '-a'

        self.t.sh.send('socktest sctp_connectx -s %s %s %s -p %s' % (self.sock, v6, addrs, port))


    def sctp_connectx_post(self, succeed = True):
        'checks for success'
        i = self.t.sh.expect_exact(["Socket %s associate id" % self.sock,
                                    self.t.sh.EINPROGRESS,
                                    self.t.sh.ETIMEDOUT,
                                    self.t.sh.ECONNREFUSED])
        if succeed and i not in (0, 1):
            raise test_fail('sctp_connectx: succeed/non-succeed')
        self.t.sh.wait_prompt()


    def sctp_connectx(self, addrs, port, succeed = True):
        self.sctp_connectx_pre(addrs, port)
        self.sctp_connectx_post(succeed)


    def sctp_peeloff_pre(self, assoc_id=None):
        'sctp_peeloff'
        if assoc_id != None and assoc_id != 0:
            self.t.sh.send('socktest sctp_peeloff -s %s -a %s' % (self.sock, str(assoc_id)))


    def sctp_peeloff_post(self):
        'returns a new peeled off socket'
        s = int(self.t.sh.expect_get(r'Peel off socket = ([0-9]+)[^0-9]', eat_prompt = False)) # if failure here, its probably "Failed, socktest socket list full"
        self.t.sh.expect_exact('Socket %s peels off' % self.sock)
        self.t.sh.wait_prompt()
        import copy
        ss = copy.copy(self)
        ss.sock = s
        self.t.ts.sockets.append(ss)
        return ss


    def sctp_peeloff(self, assoc_id=None):
        'sctp_peeloff'
        if assoc_id != None and assoc_id != 0:
            self.sctp_peeloff_pre(assoc_id=assoc_id)
            return self.sctp_peeloff_post()

    def sctp_getpaddrs(self, assoc_id=None, succeed=True):
        "returns address pointer"
        if assoc_id == None:
            assoc_id = ''
        else:
            assoc_id = ' -a %s' % str(assoc_id)

        self.t.sh.send('socktest sctp_getpaddrs -s %s%s' % (self.sock, assoc_id))
        if succeed:
            r = self.t.sh.expect_get(r'Peer address list 0x([0-9A-Fa-f]+) are:')
            #self.t.sh.wait_prompt()
            return r
        else:
            self.t.sh.expect_exact(self.t.sh.ENOTCONN)
            self.t.sh.wait_prompt()


    def sctp_getladdrs(self, assoc_id=None):
        "returns address pointer"
        if assoc_id == None:
            assoc_id = ''
        else:
            assoc_id = ' -a %s' % str(assoc_id)

        self.t.sh.send('socktest sctp_getladdrs -s %s%s' % (self.sock, assoc_id))
        r = self.t.sh.expect_get(r'Local address list 0x([0-9A-Fa-f]+) are:')
        #self.t.sh.wait_prompt()
        return r

    def sctp_freeaddrs(self, mem_addr='', local=False):
        "free address pointer"
        if mem_addr and mem_addr != 'null' and mem_addr != '0':
            if local:
                self.t.sh.send('socktest sctp_freeladdrs -a 0x%s' % mem_addr)
            else:
                self.t.sh.send('socktest sctp_freepaddrs -a 0x%s' % mem_addr)

            self.t.sh.expect_exact("address list 0x%s is freed" % mem_addr)
            self.t.sh.wait_prompt()

    def sctp_freepaddrs(self, mem_addr=''):
        "free peer address pointer"
        self.sctp_freeaddrs(mem_addr)

    def sctp_freeladdrs(self, mem_addr=''):
        "free local address pointer"
        self.sctp_freeaddrs(mem_addr, local=True)

    def sctp_getaddrlen(self, v6=False):
        "free address pointer"
        self.t.sh.send('socktest sctp_getaddrlen -d inet%s' % ('6' if v6 else ''))
        self.t.sh.expect_exact("Getaddrlen is")
        self.t.sh.wait_prompt()

    def sctp_recv(self, max_len='', waitall=False,
                  oob=False, show_from_addr=False,
                  peek=False, dont_wait=False):
        'receive data on socket and returns the associate ID'
        self.recv_pre(max_len, waitall, oob, show_from_addr, peek, dont_wait, sctp=True)
        return int(self.t.sh.expect_get(r'sinfo_assoc_id = ([0-9]+)\s'))


################################################################################
#                       Test-superclass with defaults
################################################################################
class default_test(object):
    def __init__(self):
        self.v4 = True
        self.v6 = True
        self.v4andv6 = False
        self.hosts = 1
        self.doc = ''
        self.eta = 1
        self.eta6 = -1
        self.flags = ()
        self.net_layout = 'default'
        self.will_fail = False
        self.might_fail = False
        self.retries    = 0
        #stacks / shell commands
        self.works_on_ipnet = True
        self.works_on_lkm = True
        self.works_on_fos = True
        self.works_on_iplite = False
        #OS ports
        self.works_on_unix = True
        self.works_on_ose5 = True
        self.works_on_vxworks = True
        self.works_on_gpp = True
        self.required_product_versions = { }
        self.require_types = ()


    def config(self):
        pass


    def required_product_version(self, product, version):
        self.required_product_versions[product] = version


    def pause(self):
        'press enter to continue. good for telnetting to target and check things out then continue. do NOT commit to cvs. use it in your test app during development.'
        import time
        print
        print 'paused, press enter to continue'
        raw_input()


    def breakpoint(self):
        'you will be dropped into the python debugger, press "n" to go to the code line after the "breakpoint()" statement'
        import pdb
        pdb.set_trace()


def pause():
    print
    print 'paused, press enter to continue'
    raw_input()


def breakpoint():
    import pdb
    pdb.set_trace()



################################################################################
#                       Main
################################################################################
class cleanupproc(Thread):
    def __init__(self, host):
        Thread.__init__(self)
        self.host = host

    def run(self):
        try:
            self.host.wait_prompt(1, cleanup=True)
        except:
            pass
        try:
            #could do a test here to see if relogin is needed first. like a simple "pwd"
            if self.host.s.shelltype == 'rtnet':
                self.host.logout()
                # rtnet does not need cleanup
            else:
                tl = self.host.login()
                tl._cleanup()
        except config_error, msg:
            print msg


def cleanup(targets):
    '''make sure all target session spawns empties their output streams so old output
    doesnt interfere with any cleanup'''
    if not targets:
        return
    if not isinstance(targets, list):
        targets = [targets]

    procs = [cleanupproc(t) for t in targets]
    [p.start() for p in procs]
    [p.join() for p in procs]

    #for target in targets:
    #    target.wait_prompt(1, cleanup=True)
    #for t in targets:
    #    try:
            #could do a test here to see if relogin is needed first. like a simple "pwd"
    #        tl = t.login()
    #        tl._cleanup()
    #    except config_error, msg:
    #        print msg


class loginproc(Thread):
    def __init__(self, log, logverbose, opt, host):
        Thread.__init__(self)
        self.host       = host
        self.log        = log
        self.logverbose = logverbose
        self.opt        = opt
        self.proxied    = None
        self.error      = None


    def run(self):
        try:
            target_name = self.host.get('name', 'unnamed')
            target_type_name = self.host.get('type', 'ipnet')
            session_type_name = self.host.get('login')
            if not session_type_name:
                if target_type_name in ('linux', 'lkm', 'freebsd'):
                    session_type_name = 'ssh'
                elif target_type_name in ('ipnet', 'iplite', 'rtnet'):
                    session_type_name = 'telnet'
                elif target_type_name in ('fos_telnet'):
                    session_type_name = 'utelnet'
                else:
                    self.error = 'Unknown target type: %s. (name: %s)' % (target_type_name, target_name)
                    return
                    #raise config_error('Unknown target type: %s. (name: %s)' % (target_type_name, target_name))

            #port = 2323
            port = self.host.get('port', 2323)

            if target_type_name in ('linux', 'lkm', 'freebsd', 'fos_telnet'):
                if session_type_name == 'telnet' or session_type_name == 'utelnet':
                    port = self.host.get('port', 23)
                else:
                    port = self.host.get('port', 22)
            if target_type_name in ('ipnet', 'iplite'):
                if session_type_name == 'ssh':
                    session_type_name = 'ipcom_ssh'
                    port = self.host.get('port', 22)
                elif self.host.get('os', 'unix') == 'vxworks':
                    port = self.host.get('port', 23)

            login_ip = self.host.get('ip')
            if not session_type_name in ('command'):
                if not login_ip:
                    self.error = 'No ip given for: %s' % target_name
                    return
                    #raise config_error('No ip given for: %s' % target_name)
            import getpass
            user     = self.host.get('user', getpass.getuser())
            passwd   = self.host.get('passwd')
            native   = self.host.get('native')
            target_access  = self.host.get('target-access', '')
            target_prefix  = self.host.get('target-prefix')

            #iff = h.get('if')
            target_type = globals()[target_type_name] #target_type = {'ipnet': ipnet, 'linux': linux}[target_type_name]
            session_type = globals()[session_type_name]
            #print '=== target_type:', target_type
            self.log('Logging in to "%s", ip: %s' % (target_name, login_ip))
            #a_session = session_type(log, logverbose, login_ip, port, user, passwd, target_name, opt['dry'])
            #!!!todo the session login could examine the prompt or run some command to figure out target type

            #a_host = target_type()
            #a_host.session_type_name = session_type_name
            #a_host.target_type_name = target_type_name
            #a_host.target_os_name = h.get('os', 'unspecified')
            #a_host.target_speed = h.get('speed', 1)

            #las_prefix = h.get('las-prefix')
            #if las_prefix:
            #    a_host._las_prefix = las_prefix
            #proxied = proxy(a_host, a_session)

            ts = target_state()
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
            self.proxied = proxy(session_type, target_type, ts, s_args)
            self.proxied.tops.session_type_name = session_type_name
            self.proxied.tops.target_type_name = target_type_name
            self.proxied.tops.target_os_name = self.host.get('os', 'unix')
            self.proxied.tops.target_speed = self.host.get('speed', 1)
            las_prefix = self.host.get('las-prefix')
            if las_prefix:
                if las_prefix[-1] != '/':
                    las_prefix += '/'
                ts.las_prefix = las_prefix
            self.proxied.tops.init(self.opt) # only once per target_state
        except Exception,e:
            traceback.print_exc()
            self.error = "Exception occured, exception:" + str(e)
            pass

def login_to_n_targets(log, logverbose, opt, n, hostlist):
    #!!! n number of the right kind. if test demands 1 ipnet + 1 linux and they exist in the hostlist
    # but perhaps not at slot 0 and 1
    if n > len(hostlist):
        raise net_setup_error('Not enough hosts given. %s required, %s given.' % (n, len(hostlist)))
    targets = []
    try:
        hosts = [loginproc(log, logverbose, opt, h) for h in hostlist[:n]]
        [h.start() for h in hosts]
        [h.join() for h in hosts]

        for h in hosts:
            if h.proxied:
                targets.append(h.proxied)

        for h in hosts:
            if h.error:
                raise config_error(h.error)
    except:
        for t in targets:
            t.logout()
        raise
    return targets


def gather_tests(what_to_test, listing = False):
    #check for bad names
    # adds e.g. '../../ipnet-2.6.7/test' to the pythonpath
    product = what_to_test.split('.')[0]
    if product not in config.productpath:
        print 'No product named "%s" (from %s), skipping...' % (product, what_to_test)
        return []
    productpath = os.path.join(config.productroot, config.productpath[ product ], 'test')
    if not os.access(productpath, os.F_OK):
        #print 'No dir named "%s" (from %s), skipping...' % (productpath, what_to_test)
        return []
    if productpath not in sys.path:
        sys.path.append(productpath)
    if '.' in what_to_test:
        modules_to_import = [what_to_test.split('.')[1]]
    else:
        modules_to_import = [x[:-3] for x in os.listdir(productpath) if x.endswith('.py') and not x.startswith('.')]
    modules = []
    for m in modules_to_import[:]:
        # inject things from here in each test so they need not import iptestengine
        #'all' must be something not ''
        try:
            moo = __import__(m, globals(), locals(), ['all'])
        except ImportError, msg:
            modules_to_import.remove(m)
            print msg
            print 'importing', m, 'sys.path is ', sys.path
            continue
        except SyntaxError, msg:
            modules_to_import.remove(m)
            print msg
            continue

        moo.test_fail = test_fail
        moo.engine_error = engine_error
        moo.pause = pause
        moo.breakpoint = breakpoint
        moo.ip = ip
        moo.custom_cmd = custom_command
        modules.append(moo)


    def all_tests_in(mod):
        class someclass:
            pass
        return [mod.__dict__[x] for x in dir(mod) if type(someclass) == type(mod.__dict__[x]) and hasattr(mod.__dict__[x], 'test') and callable(mod.__dict__[x].test)]


    testclasses = []
    if what_to_test.count('.') == 2:
        # specified product, file and testclass. get it.
        for t in all_tests_in(modules[0]):
            if t.__name__ == what_to_test.split('.')[2]:
                testclasses = [(modules_to_import[0], t)]
                break
        if not testclasses:
            print 'No testclass named "%s"' % what_to_test.split('.')[2]
            return []
    else:
        #specified product (and possibly file). get all testclasses in file.
        for x in range(len(modules)):
            modname = modules_to_import[x]
            for t in all_tests_in(modules[x]):
                testclasses.append((modname, t))
    tests = []
    for t in testclasses:
        class mixin(t[1], default_test):
            pass
        inst = mixin()
        inst.doc      = t[1].__doc__
        inst.config()
        inst.prodname = product
        inst.modname  = t[0]
        inst.testname = t[1].__name__
        tests.append(inst)
    return tests


def list_prods(o):
    tests = []
    flags = {}
    for k in config.productpath.keys():
        tests += gather_tests(k, listing=True)
        for test in tests:
            flags.update(test.flags)

    if o.com:
        n = 1
        for t in tests:
            print '%02d %s' % (n, t.doc)
            n += 1
        return

    maxwidth = 0
    for t in tests:
        if len(t.prodname + '.' + t.modname + '.' + t.testname) > maxwidth:
            maxwidth = len(t.prodname + '.' + t.modname + '.' + t.testname)
    def p(t, v46, h, nll, eta, bad, f, d):
        print t.ljust(maxwidth), v46.center(7), h.center(5), nll.center(12), eta.center(7), bad.center(3), f
        if d:
            print ' '*4 + d
            print
    print 'Below is a table describing available tests, if they are made for ipv4 and ipv6,'
    print 'how many target hosts are required to run the test and if the test in question'
    print 'has its own set of flags. These were found in "%s/*/test/*.py".' % config.productroot
    print
    p('testname', 'ipv4/6', 'hosts', 'net/lkm/lite', 'eta', 'bad', 'flags', '')
    for t in tests:
        #only list those specified with -t
        if (o.what_to_test
            and o.what_to_test not in (t.prodname,
                                       t.prodname + '.' + t.modname,
                                       t.prodname + '.' + t.modname + '.' + t.testname)):
            continue

        if hasattr(t, 'initialize') and callable(t.initialize):
            t.initialize(o)

        flags = ''
        if t.flags:
            flags = str(t.flags).replace('{', '').replace('}', '')
        p(t.prodname + '.' + t.modname + '.' + t.testname,
          IF(t.v4,'4','_') + "/" + IF(t.v6,'6','_'),
          str(t.hosts),
          "%s/%s/%s/%s" % tuple([IF(x,'Y','n') for x in (t.works_on_ipnet, t.works_on_lkm, t.works_on_iplite, t.works_on_fos)]),
          _eta_str(t.eta),
          IF(t.will_fail, 'f', ''),
          flags,
          IF(o.verbose, t.doc, ''))
    return


def all_user_flags():
    ls = []
    #import pdb
    #pdb.set

    for k in config.productpath.keys():
        tests = gather_tests(k)
        for test in tests:
            for f,more in test.flags:
                if not [True for x,y in ls if x == f]: #dont add dupe flags
                    ls.append((f,more))
    return ls


# support to replace vxsim image before running test case
# only for SNTP_SERVER, SNTP_CLIENT
def restart_vxsim(vxsim_name, old_image_type, image_type):
    assert vxsim_name in ('vxsim0', 'vxsim1', 'vxsim2', 'vxsim3', 'vxsim4', 'vxsim5', 'vxsim6')
    
    vxsim_name = 'rs_' + vxsim_name
    time.sleep(1)
    cmd = find_vxsim(vxsim_name)
    kill_vxsim(vxsim_name)
    time.sleep(1)
    wait_vxsim(vxsim_name, action='stop')
    if cmd:
        new_cmd = cmd.replace(old_image_type + '/vxsim_linux_vip/default/vxWorks', 
                              image_type + '/vxsim_linux_vip/default/vxWorks') # make directory unique
        new_image = get_image_name(new_cmd)
        if os.path.exists(new_image):
            time.sleep(2)
            sudovoid(new_cmd + ' 2>&1 > /dev/null &')
            time.sleep(2)
            wait_vxsim(vxsim_name, action='start')
        else:
            raise config_error('cannot find image %s' % new_image)


def find_vxsim(vxsim_name):
    # return a command line for the vxsim name
    ret = ''
    # pgrep has different version, one version has to use "-a" to list full name
    try_cmds = ('pgrep -l -f', 'pgrep -a -f')
    for cmd in try_cmds:
        lines = getoutput(cmd + ' %s' % vxsim_name).strip().split('\n')
        for line in lines:
            if line.split(' ')[1] == 'sudo':
                ret = ' '.join( line.split(' ')[2:] )
                if ret:
                    return ret
                else:
                    continue
    raise config_error('cannot find vxsim %s' % vxsim_name)
    return ''


def kill_vxsim(vxsim_name):
    sudovoid('pkill -f %s' % vxsim_name)


def wait_vxsim(vxsim_name, action, timeout=20):
    assert action in ('start', 'stop')
    ptn = '(?s)sudo .*? -p .*? LM_LICENSE_FILE=.*? vxsim -d simnet -e .*? -memsize .*? -s startup.cfg -f .*? -p \d -tn %s -lc -l vxsimlog' % (vxsim_name)
    start_time = time.time()

    # pgrep has different version, one version has to use "-a" to list full name
    while True:
        res1 = getoutput('pgrep -l -f %s' % vxsim_name)
        res2 = getoutput('pgrep -a -f %s' % vxsim_name)
        if action == 'start':
            if re.search(ptn, res1) is not None:
                break
            if re.search(ptn, res2) is not None:
                break
        if action == 'stop':
            if re.search(ptn, res1) is None:
                break
            if re.search(ptn, res2) is None:
                break
        if (time.time() - start_time) >= timeout:
            raise config_error('%s cannot %s after %s seconds' % (vxsim_name, action ,timeout))
            break
        time.sleep(1)
                
        
def sudovoid(cmd):
    return os.popen('sudo ' + cmd)


def get_image_name(cmd):
    words = filter(lambda x: x.strip() != '', cmd.split(' '))
    return words[ words.index('-f') + 1 ]

def get_num(result, test_results):
    # test_results is a list, each element is (test_name, test_result)
    assert result in ('pass', 'fail', 'skip')
    return len([x for x in test_results if x[1].lower() == result])

def main(args):     # ./iptestengine.py -t ipipsec.ipipsec.esp_transport_aesctr_none
    try:
        os.mkdir(config.logpath)
    except OSError:
        pass

    print '=== pexpect version:', pexpect.__version__
    
    opt = {'fast'       : False,
           'dry'        : False,
           'permute'    : False }

    import optparse
    p = optparse.OptionParser()
    p.add_option('-b', '--break-on-error', dest = 'break_on_fail', action="store_true", default = False, help = '''Exit the test script as soon as there is an error. Otherwise, remaining tests will be run anyways but a report in the end will show the number of failures''')
    p.add_option('-v', '--verbose', action="store_true", default = False, help = 'Everything that would have been written to the log is printed to screen')
    #p.add_option('-q', '--quiet',  help = 'Be more quiet')
    quiet = True
    p.add_option('-l', '--list', dest = 'list_prods', action="store_true", default = False, help = 'List available tests. Combine with -v to see descriptions. Add -t prodname[.modulename[.testname]] to list specific products and their tests.')
    p.add_option('-L', '--loop', dest = 'loop_forever', action="store_true", default = False, help = 'Loop all selected tests forever until you press ctrl-c or until one fails if you specified -b/--break-on-error.')
    p.add_option('-4', '--only-ipv4', dest = 'test_v6', action="store_false", default = True, help = 'Only run IPv4 versions of tests.')
    p.add_option('-6', '--only-ipv6', dest = 'test_v4', action="store_false", default = True, help = 'Only run IPv6 versions of tests.')
    p.add_option('-f', '--fast', action="store_true", default = False, help = 'Tests with support for this flag will not be run as thoroughly. This also skips process accounting.')
    p.add_option('-d', '--dry-run', action="store_true", default = False, help = "Don't actually do anything, just log what would've been done to screen. This is only useful sometimes when debugging the test engine. The output looks similar to the old tcl expect engine.")
    p.add_option('-t', '--test', dest = 'what_to_test', default = None, help = 'Run the tests found in product TEST. TEST is chosen as either by its fully qualified name or a set of tests. E.g: ipnet or ipnet.tcp or ipnet.tcp.accept. TEST can also be a comma-separated list without whitespace, e.g.: ipnet.icmp.echo,ipnet.arp (mixing single and sets of tests is ok).')
    p.add_option('--log-path', help = 'Where log files will be stored. Default from config.py')
    p.add_option('--productroot', help = 'The top path from where the productpaths begin. Default from config.py')
    p.add_option('--debug', dest = 'debugme', action="store_true", default = False, help = './iptestengine.py -t ipnet.neigh.dynamic --debug and then hit "s" to step into your specific test. OR just import pdb; pdb.set_trace() whereever you want.')
    p.add_option('--com', help = 'commercial advertising output')
    p.add_option('-H', '--hostgroup', default = 'default', help = 'Name of the group of hosts in config/hosts.py you want to use. Default group is "default"')
    p.add_option('--will-fail', action="store_true", default = False, help = 'Allow running of tests that are known to fail.')
    p.add_option('--min-time', default = 0, help = 'HhMmSs. The testing should loop until at least this time has passed. examples: 1h20m13s, 4m, 5h8s.')
    p.add_option('--permute', default = False, action="store_true", help = 'The script should permute and run internally over the hosts that has been specified')
    p.add_option('--timeout', default = 30, dest = 'timeout', help = 'Set up telnet timeout, it shall be longer for simics (60) or code coverage (600)')
    
    # Since all_user_flags() needs to know config.productroot root before the options
    # have been parsed (in order to collect additional test options from all tests),
    # we have to get any --productroot specially.
    # Count backwards to get the last --productroot argument...

    for ix in xrange(len(args) - 1, 0, -1):
        arg = args[ix]
        if arg == '--productroot':
            if ix >= len(args) - 1:
                print "Expected additional argument after '--productroot'"
                return
            config.productroot = args[ix+1]
            args[ix:ix+2] = []
            break
        if not arg.startswith('--productroot='):
            continue
        config.productroot = arg[len('--productroot='):]
        args[ix:ix+1] = []
        break

    # Accumulate all import paths, so that individual test modules
    # do not have to extend sys.path themselves.
    for k, d in config.productpath.iteritems():
        impath = os.path.join(config.productroot, d, 'test')
        if impath not in sys.path:
            sys.path.append(impath)
        
    for f,more in all_user_flags():
        p.add_option('--' + f, **more)

    (o, _) = p.parse_args(args)      # '-t', '--test', dest = 'what_to_test'
    logverbose = None
    if o.verbose:
        logverbose = sys.stdout
    if o.permute:
        opt['permute'] = True
    opt['timeout'] = 30
    if o.timeout:
        opt['timeout'] = int(o.timeout)
    if o.fast:
        opt['fast'] = True
    if o.dry_run:
        opt['dry'] = True
    if o.log_path:
        config.logpath = o.log_path
    if o.min_time:
        a = o.min_time
        mintime = 0
        if 'h' in a:
            mintime = 3600*int(a[:a.index('h')])
            a = a[a.index('h')+1:]
        if 'm' in a:
            mintime += 60*int(a[:a.index('m')])
            a = a[a.index('m')+1:]
        if 's' in a:
            mintime += int(a[:a.index('s')])
        o.min_time = mintime
    #if o in ('-q', '--quiet'):
    #    quiet = False

    #mangle the user flag input to the old getopt format. (only ike using it?)
    opt["flags"] = o
    opt.update(config.misc)
    if not o.what_to_test and not o.list_prods:
        print '-t/--test required. Use -l/--list to see available tests. -h/--help for help.'
        return

    if o.list_prods:
        list_prods(o)
        return

    import hosts
    if o.hostgroup not in hosts.groups:
        raise config_error(o.hostgroup + " not found in config/hosts.py")
    hostlist = hosts.groups[o.hostgroup]
    hostcfg = None
    if hostlist[-1]['type'] == 'config':
        hostcfg = hostlist[-1]
        hostlist = hostlist[:-1]

    rounds = 0
    tests_ok = 0
    tests_fail = 0
    tests_skipped = 0
    tests = []      # xiaozhan

    #fail on badly specified tests
    for what in o.what_to_test.split(','):        # xiaozhan   '-t', '--test', dest = 'what_to_test'
        tests_ = gather_tests(what)       # xiaozhan
        if not tests_:
            print "No such test: " + what
            return
        tests += tests_

    logfile = open(config.logpath + os.path.sep + 'test.log' + '_' + localtime_str(), 'w')
    if not logverbose:
        logverbose = logfile
    runlog = _log(logfile, o.verbose)    # xiaozhan, capture log, an log instance of class _log,

    class testscript_logger(object):
        def __init__(self, l):
            self.l = l
        def __call__(self, t, *a, **k):
            self.l('')
            self.l('DOC: ' + t, *a, **k)

    #remove unwanted tests
    for _ in range(len(tests)):
        for test in tests:
            tname = test.prodname + '.' + test.modname + '.' + test.testname
            if test.hosts > len(hostlist):
                runlog('Skipping test %s since it requires %s hosts and you only have %s configured.' % (tname, test.hosts, len(hostlist)), echo = True)
                tests.remove(test)
                tests_skipped += 1
                break

            if not o.will_fail:
                if test.will_fail:
                    runlog('Skipping test %s which would have failed.' % (tname,), echo = True)
                    tests.remove(test)
                    tests_skipped += 1
                    break
                if test.might_fail:
                    runlog('Skipping test %s which has been disabled for stability rework.' % (tname,), echo = True)
                    tests.remove(test)
                    tests_skipped += 1
                    break

                remove = False
                for h in hostlist:
                    # Native hosts must be requested in order to be seen.
                    native = h.get('native')
                    if not native:
                        ht = h['type']
                        if ((ht == 'ipnet' and not test.works_on_ipnet)
                            or (ht == 'iplite' and not test.works_on_iplite)
                            or (ht in [ 'fos_main', 'fos_telnet' ] and not test.works_on_fos  )
                            or (ht in [ 'linux', 'lkm', 'fos_main' ] and not test.works_on_lkm)):
                            runlog('Skipping test %s since it doesnt work on %s.' % (tname, ht), echo = True)
                            remove = True
                            break
                        ostype = h.get('os')
                        if ((ostype == 'ose5' and not test.works_on_ose5)
                            or (ostype == 'vxworks' and not test.works_on_vxworks)
                            or (ostype == 'unix' and not test.works_on_unix)):
                            runlog('Skipping test %s since it doesnt work on %s.' % (tname, ostype), echo = True)
                            remove = True
                            break
                        feature_set = h.get('feature_set', 'msp')
                        if feature_set == 'gpp' and not test.works_on_gpp:
                            runlog('Skipping test %s since it doesnt work on GPP.' % tname, echo = True)
                            remove = True
                            break
                if remove:
                    tests.remove(test)
                    tests_skipped += 1
                    break

    eta = 0
    for t in tests:
        if hasattr(t, 'initialize') and callable(t.initialize):
            t.initialize(opt)
        extra = 9
        if o.test_v4 and t.v4:
            eta += t.eta + extra
        if o.test_v6 and t.v6:
            if t.eta6 != -1:
                eta += t.eta6
            else:
                eta += t.eta
            eta += extra

    if not o.verbose:
        print '%s%s%s' % (IF(o.loop_forever,'','Total ETA: '), _eta_str(eta), IF(o.loop_forever,' per round','')),
        if o.loop_forever:
            print _eta_str(eta), 'per round'
        else:
            print 'Total ETA: %s (will finish at %s)' % (_eta_str(eta), time.ctime(time.time() + eta))


    def print_res(rounds, tests_ok, tests_fail, tests_skipped):
        runlog("rounds: %s.  tests_ok: %s.  tests_fail: %s.  tests_skipped: %s." % (rounds, tests_ok, tests_fail, tests_skipped), echo=True)


    fail_list = {}
    def print_fail_list():
        if fail_list:
            runlog('', echo=True)
            runlog("Failed tests:", echo=True)
        for a in sorted(fail_list.keys()):
            runlog(a, echo=True)
        runlog('', echo=True)


    test_start_time = time.time()
    #main loop
    wants_to_quit = False
    while True:
        for test in tests:
            time.sleep(0.5)
            try_again = True
            test_run  = 0
            while try_again and not wants_to_quit:
                try_again = False
                global es
                es = engine_state()
                v4v6 = ()
                if test.v4 and o.test_v4:
                    v4v6 += '',
                if test.v6 and o.test_v6:
                    v4v6 += '6',
                if test.v4andv6:
                    v4v6 = ('4and6',)
                for ipv in v4v6:
                    targets = []
                    try:
                        runlog('-'*30 + ' Login to targets ' + '-'*30)
                        try:
                            localhost   = None
                            try:
                                # new feature : support one vxsim to restart using a new vxworks image
                                # restart one vxsim
                                if hasattr(test, 'restart_vxsim'):
                                    runlog('restart %s to use %s image' % (test.restart_vxsim[0][0], test.restart_vxsim[0][2]))
                                    restart_vxsim(test.restart_vxsim[0][0], test.restart_vxsim[0][1], test.restart_vxsim[0][2])
                                    
                                use_hosts = list(hostlist)
                                for h in use_hosts:
                                    if h.get('type', None) == 'localhost':
                                        localhost = h
                                        use_hosts.remove(h)
                                        break

                                filter_hosts = []
                                # Add the required types in the correct order
                                if test.require_types:
                                    for req in test.require_types:
                                        for h in use_hosts:
                                            if req == h.get('type', None):
                                                # This host has been required; add it in the
                                                # filter host list
                                                filter_hosts.append(h)
                                                use_hosts.remove(h)
                                                break
                                        else:
                                            # An asked for host type was not availble.
                                            raise net_setup_error('unable to locate required type %s' % req)

                                # Remove any host tagged as native from the use hosts.
                                for h in use_hosts:
                                    native = h.get('native')
                                    if native:
                                        use_hosts.remove(h)

                                # Extend filter hosts with the use hosts.
                                filter_hosts.extend(use_hosts)
                                # Setup the network.
                                targets = login_to_n_targets(runlog,
                                                             logverbose,
                                                             opt,
                                                             max(test.hosts, hosts_per_net_layout.get(test.net_layout, 1)),
                                                             filter_hosts)

                                # Check if target support this ip version
                                if (not targets[0].ipv6 and ipv == '6') or (not targets[0].ipv4 and ipv == ''):
                                    runlog('Skipping test %s since it requires ipv%s on target which are not available' % (test.prodname + '.' + test.modname + '.' + test.testname + ' ' + ipv, ipv if ipv == '6' else 4), echo = True)

                                    tests_skipped += 1
                                    continue

                            except net_setup_error, desc:
                                runlog('Skipping test %s since it requires %s specific hosts which are not available (%u)' % (test.prodname + '.' + test.modname + '.' + test.testname + ' ' + ipv, test.hosts, len(filter_hosts)), echo = True)
                                tests_skipped += 1
                                continue
                            except:
                                wants_to_quit = True
                                runlog('A target is dead', echo=True)
                                traceback.print_exc()
                                raise test_fail('A target is dead')

                            # Specify localhost
                            for t in targets:
                                t.localhost = localhost
                                # t.pre_clean()

                            if hasattr(test, 'parse_console'):
                                # disable a.b.c output for later test result analysis
                                old_runlog_verbose = runlog.verbose
                                runlog.verbose = False
                                runlog.start(test, quiet, ipv, echo=False)
                                runlog.verbose = old_runlog_verbose
                            else:
                                runlog.start(test, quiet, ipv, echo=True)

                            for t in targets:
                                t.syslog('test %s starts' % (test.prodname + '.' + test.modname + '.' + test.testname + ' ' + ipv))
                            skip_this_test = False
                            for target in targets:
                                for product in test.required_product_versions.keys():
                                    version = test.required_product_versions[product]
                                    if not target.version_gte(product, version):
                                        skip_this_test = True

                            if skip_this_test:
                                # Skipped since the target is running a too old version
                                r = 'skipped'
                            else:
                                targets_and_more = layout_net(test.net_layout, targets, ipv)
                                if isiterable(targets_and_more) and len(targets_and_more) == 1:
                                    targets_and_more = targets_and_more[0]
                                if o.debugme:
                                    import pdb
                                    pdb.set_trace()
                                # run run run run run run run run run run run      # xiaozhan this is to run real test case
                                r = test.test(testscript_logger(runlog), targets_and_more, ipv, opt)

                                for t in targets:
                                    t.syslog('test %s stops' % (test.prodname + '.' + test.modname + '.' + test.testname + ' ' + ipv))

                            if r == 'skipped':
                                raise config_error('')
                            
                            if hasattr(test, 'parse_console') and test.parse_console:
                                runlog.stop(success=r)
                            else:
                                runlog.stop()
                        finally:
                            import signal
                            old = signal.getsignal(signal.SIGINT)
                            def handler(sig, frame):
                                global wants_to_quit
                                wants_to_quit = True
                            signal.signal(signal.SIGINT, handler)
                            cleanup(targets)

                            # restore one vxsim
                            if hasattr(test, 'restart_vxsim'):
                                runlog('restore %s to use %s image' % (test.restart_vxsim[1][0], test.restart_vxsim[1][2]))
                                restart_vxsim(test.restart_vxsim[1][0], test.restart_vxsim[1][1], test.restart_vxsim[1][2])

                            signal.signal(signal.SIGINT, old)

                        runlog('-'*30 + ' Logged out from targets ' + '-'*30)
                        if wants_to_quit:
                            raise KeyboardInterrupt

                    except KeyboardInterrupt:
                        runlog('int', echo=True)
                        runlog('\n' + 'x'*80 + '\n' + 'x'*80  + '\n' + 'x'*80, True)
                        runlog('User interruption (ctrl-c). Please wait a few seconds for cleanup.', True, True, context = False)
                        runlog('\n' + 'x'*80 + '\n' + 'x'*80  + '\n' + 'x'*80, True)
                        for t in targets:
                            t.syslog('test interrupted')
                        print_res(rounds, tests_ok, tests_fail, tests_skipped)
                        print_fail_list()
                        return
                    except config_error, msg:
                        tests_skipped += 1
                        runlog.stop(success = 'skipped %s' % msg)
                        for t in targets:
                            t.syslog('test skipped')
                    except:
                        if test_run < test.retries:
                            runlog(traceback.format_exc(), True)
                            for t in targets:
                                t.syslog('retry test')
                                # Reboot target to clean up after failed test cases.
                                t.reboot()
                            test_run += 1
                            traceback.print_exc()
                            time.sleep(1)
                            runlog.stop(success = 'restart')
                            try_again = True
                        else:
                            tests_fail += 1
                            fail_list[test.prodname + '.' + test.modname + '.' + test.testname + ' ' + ipv] = True
                            runlog('\n' + 'x'*80 + '\n' + 'x'*80  + '\n' + 'x'*80, True)
                            #traceback.print_exc(None, logfile)
                            runlog(traceback.format_exc(), True)
                            runlog.stop(success = False)
                            for t in targets:
                                t.syslog('test stops with error')
                                # Reboot target to clean up after failed test cases.
                                t.reboot()
                            if o.break_on_fail:
                                raise

                            traceback.print_exc()
                            #can do print traceback.format_exc() in python 2.4 instead
                            runlog('\n' + 'x'*80 + '\n' + 'x'*80  + '\n' + 'x'*80, True)
                            time.sleep(1)
                            runlog.stop(success = False)
                    else:
                        if hasattr(test, 'parse_console') and test.parse_console:
                            tests_ok += get_num('pass', r)
                            tests_fail += get_num('fail', r)
                            tests_skipped += get_num('skip', r)
                        else:
                            tests_ok += 1
                    runlog('', printtime=True)
                if wants_to_quit:
                    break
        rounds += 1
        print_res(rounds, tests_ok, tests_fail, tests_skipped)

        if (test_start_time + o.min_time > time.time() or
            o.loop_forever and not wants_to_quit):
            continue

        print_fail_list()
        break


if __name__ == '__main__':
    main(sys.argv[1:])

################################################################################
#                       End of file
################################################################################
