#! /usr/bin/env python3
import os
import re
import sys
import tempfile
import time
import pexpect
import pandas as pd

# Here intend to use pexpect instead of telnetlib to avoid the issue of 'connection reset by peer'
# refer to https://mail.python.org/pipermail/python-list/2004-August/263556.html
# import telnetlib

from shellUtils import run_cmd
from parser_iperf import parser_iperf

debugFlag = True

fsl_imx6_common_config = {'bootLoader': 'uboot',
                          'autoBootFlag': 'Hit any key to stop autoboot:',
                          'bootPrompt': 'U-Boot >',
                          'osPrompt': '-> ',
                          'osInitDone': '-> ',
                          'netDriver': 'enet(0,0)',
                          'imageStartAddr': '0x15000000',
                          'dtbStartAddr': '0x14000000',
                          }

fsl_imx6_common_config2 = {'bootLoader': 'uboot',
                           'autoBootFlag': 'Hit any key to stop autoboot:',
                           'bootPrompt': '=>',
                           'osPrompt': '-> ',
                           'osInitDone': '-> ',
                           'netDriver': 'enet(0,0)',
                           'imageStartAddr': '0x15000000',
                           'dtbStartAddr': '0x14000000',
                           }

vxboot_common_config_16278 = {'bootLoader': 'vxboot',
                              'autoBootFlag': 'Press any key to stop auto-boot...',
                              'bootPrompt': 'VxWorks Boot]:',  # the string of "[VxWorks Boot]:" not work
                              'osPrompt': '-> ',
                              'osInitDone': '-> ',
                              'netDriver': 'gei(4,0)',
                              'imageStartAddr': None,
                              'dtbStartAddr': None,
                              }

vxboot_common_config_18290 = {'bootLoader': 'vxboot',
                              'autoBootFlag': 'Press any key to stop auto-boot...',
                              'bootPrompt': 'VxWorks Boot]:',  # the string of "[VxWorks Boot]:" not work
                              'osPrompt': '-> ',
                              'osInitDone': '-> ',
                              'netDriver': 'gei(1,0)',
                              'imageStartAddr': None,
                              'dtbStartAddr': None,
                              }

vxboot_common_config_916620 = {'bootLoader': 'vxboot',
                               'autoBootFlag': 'Press any key to stop auto-boot...',
                               'bootPrompt': 'VxWorks Boot]:',  # the string of "[VxWorks Boot]:" not work
                               'osPrompt': '-> ',
                               'osInitDone': '-> ',
                               'netDriver': 'gei(0,0)',
                               'imageStartAddr': None,
                               'dtbStartAddr': None,
                               }

ls1046_pb_common_config = {'bootLoader': 'uboot',
                           'autoBootFlag': 'Hit any key to stop autoboot:',
                           'bootPrompt': '=>',
                           'osPrompt': '\r\n-> ',
                           'osInitDone': '\r\n-> ',
                           'netDriver': 'memac(1,0)',
                           'imageStartAddr': '0x85000000',
                           'dtbStartAddr': '0x84000000',
                           }

zcu102_pb_common_config = {'bootLoader': 'uboot',
                           'autoBootFlag': 'Hit any key to stop autoboot:',
                           'bootPrompt': 'ZynqMP> ',
                           'osPrompt': '\r\n-> ',
                           'osInitDone': '\r\n-> ',
                           'netDriver': 'gem(0,0)',
                           'imageStartAddr': '0x01000000',
                           'dtbStartAddr': '0x0f000000',
                           }

vlmTargetConfigs = {
    # itl_generic
    '16278': vxboot_common_config_16278,  # zone: BeijingVxNwkPerfTest
    '18290': vxboot_common_config_18290,  # zone: BeijingVxNwkPerfTest
    '916620': vxboot_common_config_916620,  # zone: BeijingVxNwkPerfTest
    # zcu_102
    '28572': zcu102_pb_common_config,  # zone: BejingVxWorksNetworkingDev
    # fsl_imx6
    '21896': fsl_imx6_common_config,  # zone: BeijingCertPlat
    '22478': fsl_imx6_common_config,  # zone: BeijingCertPlat
    '22479': fsl_imx6_common_config,  # zone: BeijingCertPlat
    '25002': fsl_imx6_common_config2,  # zone: BeijingVxNwkPerfTest
    '25003': fsl_imx6_common_config2,  # zone: BeijingVxNwkPerfTest

    # helix boards
    '28593': ls1046_pb_common_config,  # zone: BeijingVxNwkPerfTest
    '28610': zcu102_pb_common_config,  # zone: BeijingVxNwkPerfTest
    '28623': zcu102_pb_common_config,  # zone: BeijingVxNwkPerfTest
}

debugFlag = True  # boolean to turn on/off debug log
shcmdIndicator = '===='


class build_exception(Exception):
    pass


def sudovoid(cmd):
    if debugFlag:
        print('%s %s' % (shcmdIndicator, 'sudo ' + cmd))
    os.popen('sudo ' + cmd)


def sudo(cmd):
    if debugFlag:
        print('%s %s' % (shcmdIndicator, 'sudo ' + cmd))
    return os.popen('sudo ' + cmd).readlines()


def shcmdvoid(cmd):
    if debugFlag:
        print('%s %s' % (shcmdIndicator, cmd))
    os.system(cmd)


def shcmd(cmd):
    if debugFlag:
        print('%s %s' % (shcmdIndicator, cmd))
    return os.popen(cmd)


class VLMException(Exception):
    pass


WR_VLM_CLASS = 'Wind River VLM'
VLMTOOL_CMD_DEVICE_RESERVE = 'reserve'
VLMTOOL_CMD_DEVICE_UNRESERVE = 'unreserve'
VLMTOOL_CMD_DEVICE_REBOOT = 'reboot'
VLMTOOL_CMD_DEVICE_GETATTR = 'getAttr'


def VlmCmdRun(cmd, barcode, *args):
    vlmTool = args[0]
    getAttrOnReserve = args[1]

    print(cmd, vlmTool, getAttrOnReserve, args)

    if cmd == VLMTOOL_CMD_DEVICE_RESERVE:
        params = ' -t %s' % (barcode)
        if getAttrOnReserve:
            params += ' -l'

    elif cmd == VLMTOOL_CMD_DEVICE_UNRESERVE:
        params = '-t %s' % (barcode)

    elif cmd == VLMTOOL_CMD_DEVICE_REBOOT:
        params = '-t %s' % (barcode)

    elif cmd == VLMTOOL_CMD_DEVICE_GETATTR:
        params = '-t %s all' % (barcode)

    cmd = '%s %s %s' % (vlmTool, cmd, params)

    return run_cmd(cmd)


class VlmArgs:
    pass


class Vlm(object):
    vlmTool = '/folk/vlm/commandline/vlmTool'


class VlmTarget(Vlm):

    def __init__(self, id):
        assert id in vlmTargetConfigs.keys()
        self.__checkPexpectVersion()
        self.deviceClass = WR_VLM_CLASS
        self.id = id
        self.user = 'wrsadmin'
        self.password = 'kernel'
        self.vlmTool = Vlm.vlmTool
        self.getAttrOnReserve = True
        self.bootTimeout = 180
        self.icDelay = 0
        self.status = None
        self.conn = None  # xiaozhan ---this is a telnet session
        self.debug = True
        self.bootLoader = vlmTargetConfigs[id]['bootLoader']
        self.autoBootFlag = vlmTargetConfigs[id]['autoBootFlag']
        self.bootPrompt = vlmTargetConfigs[id]['bootPrompt']
        self.osPrompt = vlmTargetConfigs[id]['osPrompt']
        self.osInitDone = vlmTargetConfigs[id]['osInitDone']
        self.imageStartAddr = vlmTargetConfigs[id]['imageStartAddr']
        self.dtbStartAddr = vlmTargetConfigs[id]['dtbStartAddr']
        self.netDriver = vlmTargetConfigs[id]['netDriver']
        self.delay = 20
        self.bootArgs = ''

    def reserve(self, user=None):
        ''' reserve a target through the VLM CLI command (vlmTool) '''
        debugPrint('reserve')
        self.cmdStatus, self.output = self.vlmToolCmd(VLMTOOL_CMD_DEVICE_RESERVE, self.id)

        self.status = 'UNKNOWN'

        if self.id in self.output:
            self.status = 'RESERVED'
            if self.getAttrOnReserve:
                self.getAttr(self.output)

        return self.status == 'RESERVED'

    def unreserve(self):
        ''' unreserve a target through the VLM CLI command (vlmTool) '''
        debugPrint('unreserve')
        self.cmdStatus, self.output = self.vlmToolCmd(VLMTOOL_CMD_DEVICE_UNRESERVE, self.id)

        self.status = 'UNKNOWN'

        if self.output[0] == '1':
            self.status = 'UNRESERVED'

        return self.status == 'UNRESERVED'

    def reboot(self):
        debugPrint('reboot')
        self.status = 'UNKNOWN'
        self.cmdStatus, self.output = self.vlmToolCmd(VLMTOOL_CMD_DEVICE_REBOOT, self.id)
        self.status = 'REBOOTED'
        return self.status == 'REBOOTED'

    def load(self, hostIp, imagePath, dtbPath):
        # load image to the target
        self.status = 'UNKNOWN'
        return

    def loaded(self, delay=0):
        self.connOpen()
        if not delay:
            self.conn.write('\n')

        stuff = self.conn.read_until(self.bootPrompt.encode(), delay)
        print(stuff)

        self.status = 'LOADED'
        return stuff.endswith(self.bootPrompt.encode())

    def setup(self, hostIp, imagePath, dtbPath, timeout=300):
        return self.status == 'SETUP'

    def __connect(self, prompt, timeout=60):
        try:
            tcmd = "telnet %s %s" % (self.Terminal_Server, int(self.Terminal_Server_Port) + 2000)
            # xiaozhan self.conn is a telnet session
            # http://t.zoukankan.com/mmdln-p-9006274.html
            self.conn = pexpect.spawn(tcmd, echo=False, timeout=timeout, encoding='utf-8')
            if debugFlag:  # xiaozhan this did not set log file
                self.conn.logfile = sys.stdout  # turn on pexpect debugging
                # xiaozhan debug,below will capture stdout
                # fout = open('mylog.txt', 'a+')
                # self.conn.logfile = fout
            connectFlag = str('Connected to %s.' % self.Terminal_Server)

            expect_array = [r"scape character is '^]'.",  # connected
                            connectFlag,  # connected
                            prompt,  # connected and at boot loader
                            '->',  # connected and at vxworks C interpreter
                            pexpect.EOF,  # disconnected
                            pexpect.TIMEOUT,  # time out
                            ]

            for _ in range(1):
                i = self.conn.expect(expect_array, timeout)

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
            # successful login
            # break
        except VLMException as e:
            print(e)
            print(self.conn.before)

    def __disconnect(self):
        if self.conn is not None:
            self.conn.sendcontrol(']')
            self.conn.expect('telnet> ')
            self.conn.sendline('q')
            self.conn.expect('Connection closed.')
            self.conn = None

        return

    def connOpen(self, timeout=20):
        # debugPrint('connOpen')
        if self.conn:
            return self.conn

        status = self.__connect(self.bootPrompt)

        # return self.conn
        return status

    def connClose(self):
        # debugPrint('connClose')
        self.__disconnect()

    def __checkPexpectVersion(self):
        if pexpect.__version__ < '4.2.1':
            print('pexpect version %s not supported, should be 4.2.1 or later' % pexpect.__version__)
            sys.exit(1)

    def send(self, cmd):
        if self.conn:
            # print('\n--- send="%s"' % cmd)
            self.conn.sendline(cmd)
        else:
            raise VLMException('self.conn not set up')

    def expect(self, expect, timeout=20):
        if self.conn is not None:
            # print('\n--- expect="%s" within %s seconds' % (expect, timeout))
            return self.conn.expect(expect, timeout=timeout)
        else:
            raise VLMException('self.conn not set up')

    def sendAndExpect(self, cmd, expect, timeout=20):
        if self.conn is not None:
            # print('\n--- send="%s" and expect="%s" within %s seconds' % (cmd, expect, timeout))
            self.conn.sendline(cmd)
            return self.conn.expect(expect, timeout=timeout)
        else:
            raise VLMException('self.conn not set up')

    def sendAndReturnAll(self, cmd, expect, timeout=60):
        '''return the lines not empty, each line gets stripped'''
        if self.conn is not None:
            # print('\n--- send="%s" and expect="%s" within %s seconds' % (cmd, expect, timeout))
            self.conn.sendline(cmd)
            self.conn.expect(expect, timeout=timeout)
            lines = self.conn.before.split('\n')
            # print('original lines are---\n', lines)
            return filter(lambda x: x != '',
                          map(lambda x: x.strip(), lines))
        else:
            raise VLMException('self.conn not set up')

    def sendAndReturnAllByTimeout(self, cmd, cmd_timeout=30, strip_lines=True):
        '''
        "cmd" is sent to the shell with a "newline" appended.
        A list of lines is returned as result after cmd_timeout seconds.
        All lines are not stripped.
        This funtion is used for the command without any returned prompt/flag, like "route monitor"
        '''
        id, logfile = tempfile.mkstemp(prefix='tmp')
        # print('tempfile=%s' % logfile)
        magic_start = 'start_magic_start'
        magic_stop = 'stop_magic_stop'

        # save pexpect config
        old_timeout = self.conn.timeout
        old_logfile = self.conn.logfile

        with open(logfile, 'w') as fdw:
            self.conn.logfile = fdw

            self.conn.sendline('echo ' + magic_start + '\n')
            self.conn.expect(magic_start)
            # print('step1')
            self.conn.send(cmd + '\n')
            time.sleep(cmd_timeout)

            # print('step2')
            self.conn.send('echo ' + magic_stop + '\n')
            self.conn.expect(magic_stop)

        # print('step3')
        # restore pexpect config
        self.conn.timeout = old_timeout
        self.conn.logfile = old_logfile

        with open(logfile, 'r') as fdr:
            content = fdr.read()

        run_cmd('rm -f %s' % logfile)

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

    def getAttr(self, output=''):
        debugPrint('getAttr')
        if not output:
            status, self.output = self.vlmToolCmd(VLMTOOL_CMD_DEVICE_GETATTR, self.id)

        for line in [x for x in self.output.split('\n') if x.strip()]:
            k, v = line.split(': ', 1)
            k = k.replace(' ', '_').replace('\t', '')
            setattr(self, k, v)
            sys.stderr.write('DEBUG target attribute  "%s" : "%s"\n' % (k, v))

    def vlmToolCmd(self, cmd, *args):
        print(cmd, args)
        if cmd == VLMTOOL_CMD_DEVICE_RESERVE:
            params = ' -t %s' % (args[0])
            if self.getAttrOnReserve:
                params += ' -l'

        elif cmd == VLMTOOL_CMD_DEVICE_UNRESERVE:
            params = '-t %s' % (args[0])

        elif cmd == VLMTOOL_CMD_DEVICE_REBOOT:
            params = '-t %s' % (args[0])

        elif cmd == VLMTOOL_CMD_DEVICE_GETATTR:
            params = '-t %s all' % (args[0])

        cmd = '%s %s %s' % (self.vlmTool, cmd, params)

        return run_cmd(cmd)


class VlmUbootTarget(VlmTarget):
    def setup(self, hostIp, clientIp, imagePath, dtbPath, timeout=120, netMask='255.255.255.0'):
        ''' set up boot parameters: bootargs, bootcmd
        a) reboot
        b) go to uboot command line
        c) set up boot parameters
        d) saveenv
        '''
        # debugPrint('setup')

        self.reboot()
        time.sleep(2)
        self.connOpen()

        self.expect(self.autoBootFlag, timeout=timeout)

        self.sendAndExpect('\n', self.bootPrompt)  # send enter key

        # print('check current uboot env')
        lines = self.sendAndReturnAll('printenv',
                                      'Environment size: .*? bytes.*?%s' % self.bootPrompt)  # not work using self.bootPrompt

        # set up ipaddr
        if clientIp is None:
            self.sendAndExpect('setenv ipaddr %s' % self.IP_Address, self.bootPrompt)
        else:
            self.sendAndExpect('setenv ipaddr %s' % clientIp, self.bootPrompt)

        # set up net mask
        if clientIp is None:
            self.sendAndExpect('setenv netmask %s' % self.IP_Mask, self.bootPrompt)
        else:
            self.sendAndExpect('setenv netmask %s' % netMask, self.bootPrompt)

        # set up serverip
        self.sendAndExpect('setenv serverip %s' % hostIp, self.bootPrompt)

        # set up gatewayip
        if clientIp is None:
            self.sendAndExpect('setenv gatewayip %s' % self.Gateway, self.bootPrompt)
        else:
            self.sendAndExpect('setenv gatewayip %s' % hostIp, self.bootPrompt)

        # set up bootargs
        if clientIp is None:
            bootArgs = '%s host:vxWorks h=%s e=%s:%s g=%s u=%s pw=%s f=0x0' % (
                self.netDriver, hostIp, self.IP_Address, toHexStr(self.IP_Mask), self.Gateway, self.user, self.password)
        else:
            bootArgs = '%s host:vxWorks h=%s e=%s:%s g=%s u=%s pw=%s f=0x0' % (
                self.netDriver, hostIp, clientIp, toHexStr(netMask), hostIp, self.user, self.password)

        bootArgs = 'setenv bootargs \'%s\'' % bootArgs
        self.sendAndExpect(bootArgs, self.bootArgs)

        # saveenv
        self.sendAndExpect('saveenv', self.bootPrompt)
        self.sendAndExpect('printenv', 'Environment size: .*? bytes.*?%s' % self.bootPrompt)
        # set up bootcmd
        bootCmd = 'tftpboot %s %s; tftpboot %s %s; bootm %s - %s' % (
            self.imageStartAddr, imagePath, self.dtbStartAddr, dtbPath, self.imageStartAddr, self.dtbStartAddr)

        bootCmd = 'setenv bootcmd \'%s\'' % bootCmd
        self.sendAndExpect(bootCmd, self.bootPrompt)

        self.status = 'SETUP'
        return self.status == 'SETUP'

    def load(self, hostIp, clientIp, imagePath, dtbPath, workaround=False):
        waitReboot = 120
        for num in range(2):
            try:
                # load image to the target
                self.status = 'UNKNOWN'
                self.unreserve()  # force existing console telnet to disconnect itself

                self.reserve()
                if self.status != 'RESERVED':
                    raise VLMException('failed to reserve the target %s' % self.id)

                self.setup(hostIp, clientIp, imagePath, dtbPath, timeout=waitReboot)
                if self.status != 'SETUP':
                    raise VLMException('failed to setup the target %s' % self.id)

                self.status = 'LOADING'
                self.sendAndExpect('boot', self.osInitDone, timeout=waitReboot)
                self.status = 'LOADED'
                break
            except pexpect.TIMEOUT:
                print('\nEXCEPTION: boot image TIMEOUT and retry %s time' % (num + 1))
                self.status = 'LOAD_TIMEOUT'
                waitReboot += 30
                if self.conn.isalive():
                    self.conn.terminate()
                self.conn = None
            except pexpect.EOF:
                print('\nEXCEPTION: boot image EOF and retry %s time' % (num + 1))
                self.status = 'LOAD_EOF'
                if self.conn.isalive():
                    self.conn.terminate()
                self.conn = None

        if self.status != 'LOADED':
            raise VLMException('\nEXCEPTION: failed to load the image %s and %s to the target %s, target status:%s' % (
                imagePath, dtbPath, self.id, self.status))

        if clientIp is None:
            return self.IP_Address, self
        else:
            return clientIp, self


class VlmVxbootTarget(VlmTarget):
    def setup(self, hostIp, clientIp, imagePath, dtbPath, timeout=120):
        ''' set up boot parameters for vxboot image
        a) reboot
        b) set up boot parameters
        c) load image automatically
        '''
        # debugPrint('setup')

        self.reboot()
        time.sleep(3)

        status = self.connOpen()
        # print('=== connOpen() status:%s' % status)
        self.expect(self.autoBootFlag, timeout=timeout)

        self.send('\n')  # send return key
        self.expect(self.bootPrompt, 10)

        # set up vxboot boot parameters, e.g.
        # @gei(0,0)pek-cc-pb02l:/view_test/lchen3/vxcert/tftpboot/vxWorks 
        # h=128.224.160.44 e=128.224.167.56:fffffe00 g=128.224.166.1 u=target tn=itl_64 pw=vxTarget
        if clientIp is None:
            bootArgs = '@%s%s:%s h=%s e=%s:%s g=%s u=%s tn=%s pw=%s' % (
                self.netDriver, hostIp, imagePath, hostIp, self.IP_Address, toHexStr(self.IP_Mask), self.Gateway,
                self.user, 'itl_64', self.password)
        else:
            bootArgs = '@%s%s:%s h=%s e=%s:%s g=%s u=%s tn=%s pw=%s' % (
                self.netDriver, hostIp, imagePath, hostIp, clientIp, toHexStr(self.IP_Mask), getFirstIp(clientIp),
                self.user, 'itl_64', self.password)
        self.sendAndExpect(bootArgs, self.osInitDone)

        self.status = 'SETUP'
        return self.status == 'SETUP'

    def load(self, hostIp, clientIp, imagePath, dtbPath):
        waitReboot = 120
        for num in range(2):
            try:
                # load image to the target
                self.status = 'UNKNOWN'
                self.unreserve()  # force existing console telnet to disconnect itself

                self.reserve()
                if self.status != 'RESERVED':
                    raise VLMException('failed to reserve the target %s' % self.id)

                self.setup(hostIp, clientIp, imagePath, dtbPath, timeout=waitReboot)
                if self.status != 'SETUP':
                    raise VLMException('failed to setup the target %s' % self.id)

                self.status = 'LOADING'
                for i in range(3):
                    try:
                        self.sendAndExpect('\n', self.osPrompt)
                        break
                    except pexpect.TIMEOUT:
                        print('timeout for %s time' % (i + 1))
                        time.sleep((i + 1) * 3)
                self.status = 'LOADED'
                break
            except pexpect.TIMEOUT:
                print('\nEXCEPTION: boot image TIMEOUT and retry %s time' % (num + 1))
                self.status = 'LOAD_TIMEOUT'
                waitReboot += 30
                if self.conn.isalive():
                    self.conn.terminate()
                self.conn = None
            except pexpect.EOF:
                print('\nEXCEPTION: boot image EOF and retry %s time' % (num + 1))
                self.status = 'LOAD_EOF'
                if self.conn.isalive():
                    self.conn.terminate()
                self.conn = None

        if self.status != 'LOADED':
            raise VLMException('\nEXCEPTION: failed to load the image %s and %s to the target %s, target status:%s' % (
                imagePath, dtbPath, self.id, self.status))

        return self.IP_Address, self


def debugPrint(msg):
    if debugFlag:
        print('=== %s' % msg)


def toHexStr(ip4Mask, prefix=''):
    return prefix + ''.join(['{:02x}'.format(int(x)) for x in ip4Mask.split('.')])


def getFirstIp(ipAddr):
    return '.'.join(ipAddr.split('.')[:-1]) + '.1'


def loadImageToTarget(board, hostIp, clientIp, imagePath, dtbPath):
    bootLoader = vlmTargetConfigs[board]['bootLoader']
    if bootLoader == 'uboot':
        target = VlmUbootTarget(board)
    elif bootLoader == 'vxboot':
        target = VlmVxbootTarget(board)
    else:
        raise VLMException('unsupported boot loader %s' % bootLoader)

    return target.load(hostIp, clientIp, imagePath, dtbPath)


def test_vxboot_target():
    board = '25096'
    t = VlmTarget(board, vlmTargetConfigs[board])

    t.unreserve()
    t.reserve('lchen3')
    status = t.connOpen(90)

    t.expect('Press any key to stop auto-boot...', timeout=90)
    t.send('\n')
    t.expect(t.bootPrompt, 10)

    t.connClose()


def boot_target_16278():
    board = '16278'
    hostIp = '128.224.178.153'
    imagePath = '/folk/xli3/tsn_trial/IA_Image/vxWorks'
    dtbPath = None
    ipAddr, tgt = loadImageToTarget(board, hostIp, None, imagePath, dtbPath)
    return tgt


def boot_target_18290():
    board = '18290'
    hostIp = '128.224.178.153'
    imagePath = '/folk/xli3/tsn_trial/IA_Image/vxWorks'
    dtbPath = None
    ipAddr, tgt = loadImageToTarget(board, hostIp, None, imagePath, dtbPath)
    return tgt


# This target is for 40G performance test
def boot_target_916620():
    board = '916620'
    hostIp = '128.224.178.153'
    imagePath = '/folk/xli3/40G_image/vxWorks'
    dtbPath = None
    ipAddr, tgt = loadImageToTarget(board, hostIp, None, imagePath, dtbPath)
    return tgt


def boot_target_28572():
    board = '28572'
    hostIp = '128.224.178.153'
    imagePath = 'uVxWorks'  # xiaozhan here should not be full path
    dtbPath = 'xlnx-zcu102.dtb'
    ipAddr, tgt = loadImageToTarget(board, hostIp, None, imagePath, dtbPath)
    # print('board %s ip address: %s' % (board, ipAddr))
    return tgt


if __name__ == '__main__':
    # boot target and start iperf test
    tgt4 = boot_target_916620()
    tgt4.sendAndExpect('ipAttach 0,"qei"', 'value = 0 = 0x0', timeout=10)
    tgt4.sendAndExpect('ifconfig "qei0 10.0.0.1/24 up"', 'value = 0 = 0x0', timeout=10)
    tgt4.sendAndExpect('cmd ethtool -K qei0 lro on', '->', timeout=10)
    # start
    tst_dict = {}
    Tx = True
    print('Payload is 64 bytes')
    rets = tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -N -t 20 -p 10000 -i 20 -l 64 -f m -P 1"', 'iperf Done',
                                 timeout=25)
    rets = list(rets)
    tcp_64 = parser_iperf(rets, Tx)
    print(f'assert {tcp_64} versus baseline 313 Mbits/sec')
    if 313 / int(tcp_64) >= 1.1:
        print(f'tcp_64 result {tcp_64} is not ok')
    # TODO record test result into to dic or list, and then into excel or csv with pandas, note pass or fail
    tst_dict['tcp_64'] = tcp_64

    print('===========Payload is 1024 bytes=============')
    rets = tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -t 20 -p 10000 -i 20 -l 1024 -f m -P 1"', 'iperf Done',
                                 timeout=25)
    rets = list(rets)
    tcp_1024 = parser_iperf(rets, Tx)
    print(f'assert {tcp_1024} versus baseline 313 Mbits/sec')
    if 4450 / int(tcp_1024) >= 1.1:
        print(f'tcp_1024 result {tcp_1024} is not ok')
    tst_dict['tcp_1024'] = tcp_1024

    print('===========Payload is 65536 bytes=============')
    rets = tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -t 20 -p 10000 -i 20 -l 65536 -f m -O 6 -w 2m"', 'iperf Done',
                                 timeout=30)
    tcp_65536 = parser_iperf(rets, Tx)
    print(f'assert {tcp_65536} versus baseline 29300 Mbits/sec')
    if 29300 / int(tcp_65536) >= 1.1:
        print(f'tcp_65536 result {tcp_65536} is not ok')
    tst_dict['tcp_65536'] = tcp_65536

    print('===========Payload is UDP 1400 bytes=============')
    rets = tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -t 20 -p 10000 -i 20 -l 1400 -f m -b 0 -u"', 'iperf Done',
                                 timeout=30)
    rets = list(rets)
    udp_1400 = parser_iperf(rets, Tx)
    print(f'assert {udp_1400} versus baseline 10352 Mbits/sec')
    if 10352 / int(udp_1400) >= 1.1:
        print(f'udp_1400 result {udp_1400} is not ok')
    tst_dict['udp_1400'] = udp_1400

    print('==============Below is for Rx test=============\n')
    Tx = False
    print('===========Payload is 64 bytes Rx==============')
    rets = tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -N -t 20 -p 10000 -i 20 -l 64 -f m -R"', 'iperf Done',
                                 timeout=25)
    rets = list(rets)
    tcp_64_Rx = parser_iperf(rets, Tx)
    print(f'assert {tcp_64_Rx} versus baseline 398 Mbits/sec')
    if 398 / int(tcp_64_Rx) >= 1.1:
        print(f'tcp_64_Rx result {tcp_64_Rx} is not ok')
    tst_dict['tcp_64_Rx'] = tcp_64_Rx

    print('===========Payload is 1024 bytes  Rx=============')
    rets = tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -t 20 -p 10000 -i 20 -l 1024 -f m -R"', 'iperf Done',
                                 timeout=25)
    rets = list(rets)
    tcp_1024_Rx = parser_iperf(rets, Tx)
    print(f'assert {tcp_1024_Rx} versus baseline 4310 Mbits/sec')
    if 4310 / int(tcp_1024_Rx) >= 1.1:
        print(f'tcp_1024_Rx result {tcp_1024_Rx} is not ok')
    tst_dict['tcp_1024_Rx'] = tcp_1024_Rx

    print('===========Payload is 65536 bytes Rx=============')
    rets = tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -t 20 -p 10000 -i 20 -l 65536 -f m -R"', 'iperf Done',
                                 timeout=30)
    rets = list(rets)
    tcp_65536_Rx = parser_iperf(rets, Tx)
    print(f'assert {tcp_65536_Rx} versus baseline 16828 Mbits/sec')
    if 16828 / int(tcp_65536_Rx) >= 1.1:
        print(f'tcp_65536_Rx result {tcp_65536_Rx} is not ok')
    tst_dict['tcp_65536_Rx'] = tcp_65536_Rx

    print('===========Payload is UDP 1400 bytes  Rx=============')
    rets = tgt4.sendAndReturnAll('sp iperf3,"-c 10.0.0.2 -t 20 -p 10000 -i 20 -l 1400 -f m -b 0 -u -R"', 'iperf Done',
                                 timeout=30)
    rets = list(rets)
    udp_1400_Rx = parser_iperf(rets, Tx)
    print(f'assert {udp_1400_Rx} versus baseline 4420 Mbits/sec')
    if 4420 / int(udp_1400_Rx) >= 1.1:
        print(f'udp_1400_Rx result {udp_1400_Rx} is not ok')
    tst_dict['udp_1400_Rx'] = udp_1400_Rx
    # =======================================================================
    # close session
    tgt4.connClose()
    # record test result
    for k in tst_dict:
        print("%s - %s" % (k, tst_dict[k]))
    date_range = pd.date_range(start=time.strftime("%Y-%m-%d"), periods=1)
    df = pd.DataFrame(tst_dict, index=date_range)
    res_csv = time.strftime("%Y-%m-%d") + '.csv'
    df.to_csv(res_csv)
