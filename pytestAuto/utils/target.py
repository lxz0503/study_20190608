import logging
import os
import re
import time
import pexpect
# Here intend to use pexpect instead of telnetlib to avoid the issue of 'connection reset by peer' 
# refer to https://mail.python.org/pipermail/python-list/2004-August/263556.html
from abc import ABCMeta, abstractmethod
from io import IOBase
import sys

sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.testEngine import ip, ShellOperations
from utils.util import readYaml, checkPath, copyTree, shellCmd, run_cmd

vlmTargetConfigFile = 'config/vlmTargetConfig.yaml'
log = logging.getLogger('vlmTarget')


class VLMException(Exception): pass


class ConfigError(Exception): pass


def createBridgeName(ip):
    return 'br-vm-%s' % ip.get_raw_addr()[2]


def createTapName(board):
    return 'tap-%s' % board


def createNetDevId(ip):
    prefix = 'mynet'
    return '%s%s' % (prefix, ip.get_raw_addr()[3])


def createMacAddr(ip):
    a, b, c, d = ip.get_raw_addr()
    macPrefix = '52:55'
    return '%s:%02x:%02x:%02x:%02x' % (macPrefix, a, b, c, d)


class Image(metaclass=ABCMeta):  # python 3.0 syntax, abstract class, template
    def __init__(self, bin, dtb=None, user=None, passwd=None, debug=False):
        self.bin = bin
        self.dtb = dtb
        self.user = user
        self.passwd = passwd
        self.debug = debug
        # checkPath(self.bin)   # xiaozhan, debug remove
        if self.dtb is not None:
            checkPath(self.dtb)

    @abstractmethod
    def run(self, command, logfile=None):
        pass

    def getBin(self):
        return self.bin

    def getDtb(self):
        return self.dtb


class VxWorksImage(Image):   # check if vxworks image is loaded or not
    def run(self, console):
        if self.debug:
            print('=== VxWorksImage.run()')
        expect_array = [
            '-> ',  # 0
            'assword: ',  # 1
            'ogin: ',  # 2
        ]

        for _ in range(3):
            try:
                i = console.expect(expect_array)
                if i == 2:  # 'ogin: ',
                    if self.debug:
                        print('=== found vxworks login:')
                    if not self.user:
                        raise ConfigError('%s\nA user was required but none configured for target: %s at %s:%s\n%s' % (
                            'x' * 79, self.name, self.addr, self.port, 'x' * 80))
                    console.sendline(self.user)
                if i == 1:  # 'assword: '
                    if self.debug:
                        print('=== found vxworks password:')
                    if not self.passwd:
                        raise ConfigError(
                            '%s\nA password was required but none configured for target: %s at %s:%s\n%s' % (
                                'x' * 79, self.name, self.addr, self.port, 'x' * 80))
                    console.sendline(self.passwd)
                if i == 0:  # '-> '
                    if self.debug:
                        print('=== found vxworks C interpreter ->')
                    break
            except pexpect.TIMEOUT:
                console.send('\r')
        else:
            raise ConfigError('Failed to start vxworks image')


# xiaozhan debug for Linux Image
class LinuxImage(Image):
    def __init__(self, bin, dtb=None, user=None, passwd=None, debug=False, prompt=None, device=None):
        super().__init__(bin, dtb, user, passwd, debug)
        # if self.bin == 'default':
        self.configYaml = 'config/qemuTargetConfig.yaml'
        print('=============using config========== %s' % self.configYaml)
        # checkPath(self.configYaml)   # xiaozhan  debug
        self.config = readYaml(self.configYaml, key='LINUX-IMAGE')
        self.bin = self.config['image']  # xiaozhan debug, this is the linux bin
        self.prompt = self.config['prompt']
        self.device = self.config['device']
        self.user = self.config['user']
        self.passwd = self.config['passwd']
        # else:
        #     self.user = 'ubuntu' if user is None else user
        #     self.passwd = 'ubuntu' if passwd is None else passwd
        #     self.prompt = 'ubuntu@ubuntu:~$ ' if prompt is None else prompt
        #     self.device = 'ens3' if device is None else device

    def run(self, console):
        print('================LinuxImage.run()===============')
        expect_array = [
            self.prompt,  # 0
            'Password: ',  # 1
            'ubuntu login: ',  # 2
        ]

        for _ in range(3):
            try:
                i = console.expect_exact(expect_array)
                if i == 2:  # 'ogin: ',
                    log.debug('found Ubuntu login:')
                    if not self.user:
                        raise ConfigError('%s\nA user was required but none configured for target: %s at %s:%s\n%s' % (
                            'x' * 79, self.name, self.addr, self.port, 'x' * 80))
                    console.sendline(self.user)
                if i == 1:  # 'assword: '
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


class Target(metaclass=ABCMeta):  # python 3.0 syntax. Define abstract class for target template
    def __init__(self, board, configYaml=None, logFile=None, timeout=20):
        self._checkPexpectVersion()
        self.board = board  # xiaozhan, board is the key in yaml file
        self.configYaml = configYaml
        self.timeout = timeout
        # xiaozhan, add below
        self.console = None
        self.bridge = None
        self.image = None
        self.ip = None
        self.hostIp = None

        if logFile is not None:
            if type(logFile) == str:
                self.logFile = open(logFile, 'wb')
            elif isinstance(logFile, IOBase):  # tips: python 3
                self.logFile = logFile
            else:
                raise ConfigError('incorrect logFile %s' % logFile)

    @abstractmethod   # must implement it in child class
    def setup(self, image, targetIp=None, bridge=None, hostIp=None):
        pass

    @abstractmethod   # must implement it in child class
    def start(self):
        pass

    @abstractmethod   # must implement it in child class
    def cleanup(self):
        pass

    def send(self, cmd):
        if self.console:
            log.debug('\n--- send="%s"' % cmd)
            self.console.sendline(cmd)
        else:
            raise VLMException('self.console not set up')

    def expect(self, expect, timeout=20):
        if self.console is not None:
            log.debug('\n--- expect="%s" within %s seconds' % (expect, timeout))
            print('\n--- expect="%s" within %s seconds' % (expect, timeout))
            print('=====xiaozhan=====', self.console.before.decode('utf-8'))
            return self.console.expect(expect, timeout=timeout)
        else:
            raise VLMException('self.console not set up')

    def sendAndExpect(self, cmd, expect, timeout=20):
        if self.console is not None:
            log.debug('\n--- send="%s" and expect="%s" within %s seconds' % (cmd, expect, timeout))
            self.console.sendline(cmd)
            return self.console.expect(expect, timeout=timeout)
        else:
            raise VLMException('self.console not set up')

    def sendAndReturnAll(self, cmd, expect, timeout=20):
        """return the lines not empty, each line gets stripped"""
        if self.console is not None:
            # log.debug('\n--- send="%s" and expect="%s" within %s seconds' % (cmd, expect, timeout))
            print('\n------- send="%s" and expect="%s" within %s seconds' % (cmd, expect, timeout))
            self.console.sendline(cmd)
            self.console.expect(expect, timeout=timeout)
            # lines = self.console.before.split(b'\n')

            ret = self.console.before.decode("utf-8")
            print('=====xiaozhan======ret====', ret)
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

    def _readConfig(self):
        cfg = readYaml(self.configYaml)
        return cfg[self.board]

    def _checkPexpectVersion(self):
        if pexpect.__version__ < '4.2.1':
            print('pexpect version %s not supported, should be 4.2.1 or later' % pexpect.__version__)
            sys.exit(1)


def readVlmTargetConfig(boardId):
    vlmTargetConfigs = readYaml(vlmTargetConfigFile)
    try:
        config = vlmTargetConfigs[boardId]
        return config
    except KeyError:
        print('ERROR: board %s not existed in vlm target config file %s' % (boardId, vlmTargetConfigFile))


class VlmTarget(Target):  # inherit from Target
    def __init__(self, board, configYaml=None, logFile=None, timeout=20):
        super().__init__(board, configYaml, logFile, timeout)  # reuse
        self.output = None
        self.cmdStatus = None
        self.configYaml = 'config/vlmTargetConfig.yaml' if configYaml is None else configYaml

        self.config = self._readConfig()
        self.bootLoader = self.config['bootLoader']
        self.autoBootFlag = self.config['autoBootFlag']
        self.bootPrompt = self.config['bootPrompt']
        self.osPrompt = self.config['osPrompt']
        self.imageStartAddr = self.config['imageStartAddr']
        self.dtbStartAddr = self.config['dtbStartAddr']
        self.netDriver = self.config['netDriver']
        self.user = 'target'
        self.password = 'vxTarget'
        self.vlmTool = '/folk/vlm/commandline/vlmTool'
        self.getAttrOnReserve = True
        self.bootTimeout = 300
        self.bootRetryTime = 2
        self.status = None
        self.debug = True

    def reserve(self, user=None):
        log.info('reserve %s' % self.board)
        self.cmdStatus, self.output = self.__vlmToolCmd('reserve', self.board)

        self.status = 'UNKNOWN'

        if self.board in self.output:
            self.status = 'RESERVED'
            if self.getAttrOnReserve:
                self.getAttr(self.output)

        return self.status == 'RESERVED'

    def unreserve(self):
        """ unreserve a target through the VLM CLI command (vlmTool) """
        log.info('unreserve %s' % self.board)
        self.cmdStatus, self.output = self.__vlmToolCmd('unreserve', self.board)

        self.status = 'UNKNOWN'

        if self.output[0] == '1':
            self.status = 'UNRESERVED'

        return self.status == 'UNRESERVED'

    def getAttr(self, output=''):
        log.info('getAttr %s' % self.board)
        if not output:
            _, self.output = self.__vlmToolCmd('getAttr', self.board)

        for line in [x for x in self.output.split('\n') if x.strip()]:
            k, v = line.split(': ', 1)
            k = k.replace(' ', '_').replace('\t', '')
            setattr(self, k, v.strip())
            log.debug('DEBUG target attribute  "%s" : "%s"\n' % (k, v))

    def reboot(self):
        log.info('reboot %s' % self.board)
        self.status = 'UNKNOWN'
        self.cmdStatus, self.output = self.__vlmToolCmd('reboot', self.board)
        self.status = 'REBOOTED'
        return self.status == 'REBOOTED'

    def load(self, hostIp, imagePath, dtbPath):
        # load image to the target
        self.status = 'UNKNOWN'
        return

    def loaded(self, delay=0):
        self.connOpen()
        if not delay:
            self.console.write('\n')

        stuff = self.console.read_until(self.bootPrompt.encode(), delay)
        print(stuff)

        self.status = 'LOADED'
        return stuff.endswith(self.bootPrompt.encode())

    def setup(self, image, targetIp=None, bridge=None, hostIp=None):
        return self.status == 'SETUP'

    def connOpen(self, timeout=20):
        log.info('connOpen %s' % self.board)
        if self.console:
            return self.console

        status = self.__connect(self.bootPrompt)
        return status

    def connClose(self):
        log.info('connClose %s' % self.board)
        self.__disconnect()

    def __connect(self, prompt, timeout=60):  # private method, can not be directly used outside of the class
        try:
            tcmd = "telnet %s %s" % (self.Terminal_Server, int(self.Terminal_Server_Port) + 2000)
            self.console = pexpect.spawn(tcmd, echo=False, timeout=timeout)
            if self.logFile is not None:
                self.console.logfile = self.logFile
            connectFlag = str('Connected to %s.' % self.Terminal_Server)

            expect_array = [r"scape character is '^]'.",  # connected
                            connectFlag,  # connected
                            prompt,  # connected and at boot loader
                            '->',  # connected and at vxworks C interpreter
                            pexpect.EOF,  # disconnected
                            pexpect.TIMEOUT,  # time out
                            ]

            for _ in range(1):
                i = self.console.expect(expect_array, timeout)
                if i in (0, 1):
                    return 'T_CONNECTED'
                elif i == 2:
                    return 'T_BOOTLOADER'
                elif i == 3:
                    return 'T_VXWORKS'
                elif i == 4:
                    return 'T_EOF'
                elif i == 5:
                    return 'T_TIMEOUT'

            else:
                raise VLMException('\nFailed to login using telnet: %s %s\n' % (
                    self.Terminal_Server, int(self.Terminal_Server_Port) + 2000))
        except VLMException as e:
            print(e)
            print(self.console.before)

    def __disconnect(self):
        if self.console is not None:
            self.console.sendcontrol(']')
            self.console.expect('telnet> ')
            self.console.sendline('q')
            self.console.expect('Connection closed.')
            self.console = None
        return

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

        cmd = '%s %s %s' % (self.vlmTool, cmd, params)

        return run_cmd(cmd)


class VlmUbootTarget(VlmTarget):  # this is for ARM board using uboot
    def setup(self, image, targetIp=None, bridge=None, hostIp=None):
        self.bridge = bridge
        self.image = image
        self.ip = targetIp
        self.hostIp = hostIp

    def __setupBootArg(self):
        ''' set up boot parameters: bootargs, bootcmd
        a) reboot
        b) go to uboot command line
        c) set up boot parameters
        d) saveenv
        '''
        log.info('setup')

        self.reboot()
        time.sleep(1)
        self.connOpen()

        self.expect(self.autoBootFlag, timeout=self.bootTimeout)
        self.sendAndExpect('\n', self.bootPrompt)  # send enter key

        lines = self.sendAndReturnAll('printenv',
                                      'Environment size: .*? bytes.*?%s' % self.bootPrompt)  # not work using self.bootPrompt

        saveFlag = False
        if not self.__setParameter('ipaddr=%s' % self.IP_Address, lines):
            # set up ipaddr
            self.sendAndExpect('setenv ipaddr %s' % self.IP_Address, self.bootPrompt)
            saveFlag = True

        if not self.__setParameter('netmask=%s' % self.IP_Mask, lines):
            # set up net mask
            self.sendAndExpect('setenv netmask %s' % self.IP_Mask, self.bootPrompt)
            saveFlag = True

        if not self.__setParameter('serverip=%s' % self.hostIp, lines):
            # set up serverip
            self.sendAndExpect('setenv serverip %s' % self.hostIp, self.bootPrompt)
            saveFlag = True

        if not self.__setParameter('gatewayip=%s' % self.Gateway, lines):
            # set up gatewayip
            self.sendAndExpect('setenv gatewayip %s' % self.Gateway, self.bootPrompt)
            saveFlag = True

        if not self.__setParameter('bootcmd=tftp %s %s; tftp %s %s; bootm %s - %s' % (
                self.imageStartAddr, self.image.getBin(), self.dtbStartAddr, self.image.getDtb(), self.imageStartAddr,
                self.dtbStartAddr), lines):
            # set up bootcmd
            bootCmd = 'tftp %s %s; tftp %s %s; bootm %s - %s' % (
                self.imageStartAddr, self.image.getBin(), self.dtbStartAddr, self.image.getDtb(), self.imageStartAddr,
                self.dtbStartAddr)
            bootCmd = 'setenv bootcmd \'%s\'' % bootCmd
            print('=== bootcmd=%s' % bootCmd)
            self.sendAndExpect(bootCmd, self.bootPrompt)
            saveFlag = True

        if saveFlag:
            self.sendAndExpect('saveenv', 'Erasing SPI flash...Writing to SPI flash...done')
            self.expect(self.bootPrompt)

        self.sendAndExpect('printenv', 'Environment size: .*? bytes.*?%s' % self.bootPrompt)

        self.status = 'SETUP'
        return self.status == 'SETUP'

    def __setParameter(self, parameter, contentList):
        """ check if the parameter already in the content list """
        return parameter in contentList

    def start(self):
        """ load image to the target """
        for num in range(self.bootRetryTime):
            try:
                self.status = 'UNKNOWN'
                self.unreserve()  # force existing console telnet to disconnect itself

                self.reserve()
                if self.status != 'RESERVED':
                    raise VLMException('failed to reserve the target %s' % self.board)

                self.ip = ip(self.IP_Address, self.IP_Mask)

                self.__setupBootArg()
                if self.status != 'SETUP':
                    raise VLMException('failed to setup the target %s' % self.board)

                self.status = 'LOADING'
                self.send('boot')
                self.image.run(self.console)
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

        return self.console

    def cleanup(self):
        self.connClose()


class VlmVxbootTarget(VlmTarget):  # this is for IA target using bootrom
    def setup(self, image, targetIp=None, bridge=None, hostIp=None):
        log.info('setup %s' % self.board)
        self.bridge = bridge
        self.image = image
        self.ip = targetIp
        self.hostIp = hostIp

    def __setupBootArg(self):
        ''' set up boot parameters for vxboot image
        a) reboot
        b) set up boot parameters
        c) load image automatically
        '''
        log.info('setup %s boot args' % self.board)

        self.reboot()
        time.sleep(3)

        status = self.connOpen()
        log.debug('=== connOpen() status:%s' % status)
        self.expect(self.autoBootFlag, timeout=self.bootTimeout)

        self.send('\n')  # send return key
        self.expect(self.bootPrompt, 10)

        # set up vxboot boot parameters, e.g.
        # @gei(0,0)pek-cc-pb02l:/view_test/lchen3/vxcert/tftpboot/vxWorks 
        # h=128.224.160.44 e=128.224.167.56:fffffe00 g=128.224.166.1 u=target tn=itl_64 pw=vxTarget     
        bootArgs = '@%s%s:%s h=%s e=%s:%s g=%s u=%s tn=%s pw=%s' % (
            self.netDriver, self.hostIp, self.image.getBin(), self.hostIp, self.IP_Address, toHexStr(self.IP_Mask),
            self.Gateway, self.user, 'itl_64', self.password)
        self.sendAndExpect(bootArgs, self.osPrompt)

        self.status = 'SETUP'
        return self.status == 'SETUP'

    def start(self):
        """ load image to the target """
        for num in range(self.bootRetryTime):
            try:
                self.status = 'UNKNOWN'
                self.unreserve()  # force existing console telnet to disconnect itself

                self.reserve()
                if self.status != 'RESERVED':
                    raise VLMException('failed to reserve the target %s' % self.board)

                self.ip = ip(self.IP_Address, self.IP_Mask)

                self.__setupBootArg()
                if self.status != 'SETUP':
                    raise VLMException('failed to setup the target %s' % self.board)

                self.status = 'LOADING'
                self.sendAndExpect('\n', self.osPrompt)
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

        return self.console

    def cleanup(self):
        self.connClose()


def toHexStr(ip4Mask, prefix=''):
    return prefix + ''.join(['{:02x}'.format(int(x)) for x in ip4Mask.split('.')])


def loadImageToTarget(target, image, hostIp):
    checkPath(image.getBin())
    if image.getDtb() is not None:
        checkPath(image.getDtb())

    target.setup(image, targetIp=None, bridge=None, hostIp=hostIp)
    return target.start()


class QemuTarget(Target):
    def __init__(self, board, configYaml=None, logFile=None, timeout=20, debug=False):
        super().__init__(board, configYaml, logFile, timeout)
        if configYaml is None:
            self.configYaml = 'config/qemuTargetConfig.yaml'  # xiaozhan, debug
        self.debug = debug    # xiaozhan, you can change it to None
        self.config = self._readConfig()
        self.tapName = None   # xiaozhan, new var for class qemutarget

    def setup(self, image, targetIp=None, bridge=None, hostIp=None):
        self.bridge = bridge
        self.image = image
        self.ip = targetIp
        if self.bridge is not None:
            # xiaozhan, debug
            print('=======start to create====vxworks bridge====')
            self.tapName = createTapName(self.board)
            shellCmd('sudo tunctl -u $USER -t %s' % self.tapName, debug=self.debug)
            shellCmd('sudo brctl addif %s %s' % (self.bridge, self.tapName), debug=self.debug)
            shellCmd('sudo ifconfig %s up' % self.tapName, debug=self.debug)
            return self.tapName
        else:
            return None

    def start(self):  # xiaozhan, debug---self.image --image is from Image class
        cmd = self.__createQemuCmd(self.image, self.ip, self.tapName)
        if self.debug:
            print(cmd)
        if isinstance(self.image, LinuxImage):
            self.timeout = 180
        self.console = pexpect.spawn(cmd, timeout=self.timeout)  # xiaozhan, this is similar with telnet session
        if self.logFile is not None:      #
            self.console.logfile = self.logFile     # xiaozhan, store test log for each target console
        self.image.run(self.console)  # xiaozhan  debug, it is to check the console status after pexpect.spawn
        # return ShellOperations(self.console, prompt='-> ')   # xiaozhan, remove
        # xiaozhan, debug, add----Linux qemu   ---TODO
        if isinstance(self.image, LinuxImage):
            print('======Linux qemu=====debug====')
            prompt = self.image.prompt
            device = self.image.device
            ip = self.ip.get_addr_str()
            prefixlen = self.ip.prefixlen
            self.console.sendline(f'sudo ip addr add {ip}/{prefixlen} dev {device}')
            self.console.expect_exact(prompt)
            self.console.sendline(f'sudo ip link set dev {device} up')   # xiaozhan, debug Linux return
            self.console.expect_exact(prompt)
            self.console.sendline(f'sudo ip addr add 2000::2/64 dev ens3')  # xiaozhan, add
            self.console.expect_exact(prompt)

        # xiaozhan, debug
        #     return ShellOperations(self.console, prompt='ubuntu@ubuntu:~$ ')   # xiaozhan, remove

    def cleanup(self):
        if self.console is not None:
            if self.debug:
                print('=== quit target %s' % self.board)
            if not self.console.terminate(force=True):
                if self.debug:
                    print('use ctrl+c to quit target')
                self.console.sendcontrol('c')   # xiaozhan, debug
                self.console.expect(pexpect.EOF)

        if self.bridge is not None:
            shellCmd('sudo ifconfig %s down' % self.tapName, debug=self.debug)
            shellCmd('sudo brctl delif %s %s' % (self.bridge, self.tapName), debug=self.debug)
            shellCmd('sudo tunctl -d  %s' % self.tapName, debug=self.debug)

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
        print(f'=======create qemu cmd is==========\n{cmd}')
        return cmd


class NetworkBuilder(object):  # xiaozhan,debug, this is for 6 qemu
    def __init__(self, targets, images, ips, bridge=None):
        self.bridge = bridge
        self.outsideBridge = None
        self.tapNames = []
        self.targets = targets
        self.images = images
        self.ips = ips
        self.singleBoard = False
        self.__checkConfig()

    def setup(self):
        if not self.singleBoard:
            if self.bridge is None:
                self.__setupBridge()    # xiaozhan, create bridge
                self.outsideBridge = False
            else:
                self.outsideBridge = True
            for t in self.targets:
                print('\n')
                i = self.targets.index(t)
                self.tapNames.append(t.setup(self.images[i], targetIp=self.ips[i], bridge=self.bridge))
            netId = self.ips[0].get_networkid_str()
            shellCmd('sudo ifconfig %s inet %s up' % (self.bridge, netId))
        else:
            self.targets[0].setup(None, self.images[0], self.ips[0])

    # xiaozhan, debug
    def start(self):
        consoles = []
        for t in self.targets:
            console = t.start()  # xiaozhan debug, start vxworks console for each target
            consoles.append(console)
        return consoles

    def cleanup(self):
        if not self.singleBoard:
            for t in self.targets:
                print('\n')
                t.cleanup()
            print('\n')
            self.__cleanupBridge()
        else:
            self.targets[0].cleanup()

    def __checkConfig(self):
        print(len(self.targets), len(self.images), len(self.ips))
        assert len(self.targets) == len(self.images) == len(self.ips)
        if len(self.targets) == 1:
            self.singleBoard = True

    def __setupBridge(self):
        self.bridge = createBridgeName(self.ips[0])   # xiaozhan, get bridge name
        shellCmd('sudo brctl addbr %s' % self.bridge)
        shellCmd('sudo brctl sethello %s 10' % self.bridge)
        shellCmd('sudo brctl setfd %s 0' % self.bridge)

    def __cleanupBridge(self):
        if self.bridge is not None and not self.outsideBridge:  # xiaozhan,ע������outsiderBridge
            shellCmd('sudo ip link set %s down' % self.bridge)
            shellCmd('sudo brctl delbr %s' % self.bridge)


# xiaozhan, add, this is for qemu Linux, the bridge is using the already created, bridge should not be None
class NetworkBuilderLinux(NetworkBuilder):
    def setup(self):   # xiaozhan, debug and modify its function, it should rename to add
        # self.outsideBridge = False    # xiaozhan, debug, checke its usage???
        for t in self.targets:
            print('\n')
            i = self.targets.index(t)
            self.tapNames.append(t.setup(self.images[i], targetIp=self.ips[i], bridge=self.bridge))
        # netId = self.ips[0].get_networkid_str()
        # shellCmd('sudo ifconfig %s inet %s up' % (self.bridge, netId)) # this should already exist




