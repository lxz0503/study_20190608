#!/usr/bin/env python3
import os
import re
import sys
import tempfile
import time
import pexpect
# Here intend to use pexpect instead of telnetlib to avoid the issue of 'connection reset by peer' 
# refer to https://mail.python.org/pipermail/python-list/2004-August/263556.html
# import telnetlib

sys.path.insert(0, '.')
from .shellUtils import run_cmd
# xiaozhan---use below line to debug---python3 vlmTarget_dev.py
# from shellUtils import run_cmd

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
                              'Terminal_Server': '128.224.164.42',
                              'Terminal_Server_Port': 11,
                              'IP_Mask': '255.255.254.0',
                              'Gateway': '128.224.166.1'
                              }

vxboot_common_config_18290 = {'bootLoader': 'vxboot',
                              'autoBootFlag': 'Press any key to stop auto-boot...',
                              'bootPrompt': 'VxWorks Boot]:',  # the string of "[VxWorks Boot]:" not work
                              'osPrompt': '-> ',
                              'osInitDone': '-> ',
                              'netDriver': 'gei(1,0)',
                              'imageStartAddr': None,
                              'dtbStartAddr': None,
                              'Terminal_Server': '128.224.164.42',
                              'Terminal_Server_Port': 13,
                              'IP_Mask': '255.255.254.0',
                              'Gateway': '128.224.166.1'
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

zcu102_pb_common_config_28572 = {'bootLoader': 'uboot',
                                 'autoBootFlag': 'Hit any key to stop autoboot:',
                                 'bootPrompt': 'ZynqMP> ',
                                 'osPrompt': '\r\n-> ',
                                 'osInitDone': '\r\n-> ',
                                 'netDriver': 'gem(0,0)',
                                 'imageStartAddr': '0x01000000',
                                 'dtbStartAddr': '0x0f000000',
                                 'Terminal_Server': '128.224.157.61',
                                 'Terminal_Server_Port': 18,
                                 'IP_Mask': '255.255.254.0',
                                 'Gateway': '128.224.166.1'
                                 }

vlmTargetConfigs = {
    # zcu_102
    '28572': zcu102_pb_common_config_28572,
    # fsl_imx6
    '22478': fsl_imx6_common_config,  # zone: BeijingCertPlat
    '22479': fsl_imx6_common_config,  # zone: BeijingCertPlat
    '25002': fsl_imx6_common_config2,  # zone: BeijingVxNwkPerfTest
    '25003': fsl_imx6_common_config2,  # zone: BeijingVxNwkPerfTest
    # itl_generic
    # '28525': vxboot_common_config,  # zone: BeijingVxNwkPerfTest
    # '28526': vxboot_common_config,  # zone: BeijingVxNwkPerfTest
    # '25096': vxboot_common_config,  # zone: BejingVxWorksNetworkingDev
    '16278': vxboot_common_config_16278,  # zone: BeijingVxNwkPerfTest
    '18290': vxboot_common_config_18290,  # zone: BeijingVxNwkPerfTest
    # helix boards
    # '28567': vxboot_common_config,  # zone: BeijingVxNwkPerfTest
    # '28593': ls1046_pb_common_config,  # zone: BeijingVxNwkPerfTest
    # '28623': zcu102_pb_common_config,  # zone: BeijingVxNwkPerfTest
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


class VlmTarget():

    def __init__(self, id):
        assert id in vlmTargetConfigs.keys()
        self.__checkPexpectVersion()
        self.id = id
        self.user = 'wrsadmin'
        self.password = 'kernel'
        self.bootTimeout = 120
        self.icDelay = 0
        self.status = None
        self.conn = None
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
        self.Terminal_Server = vlmTargetConfigs[id]['Terminal_Server']
        self.Terminal_Server_Port = vlmTargetConfigs[id]['Terminal_Server_Port']
        self.IP_Mask = vlmTargetConfigs[id]['IP_Mask']
        self.Gateway = vlmTargetConfigs[id]['Gateway']

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

    def setup(self, hostIp, imagePath, dtbPath, timeout=120):
        return self.status == 'SETUP'

    def __connect(self, prompt, timeout=60):
        try:
            tcmd = "telnet %s %s" % (self.Terminal_Server, int(self.Terminal_Server_Port) + 2000)
            self.conn = pexpect.spawn(tcmd, echo=False, timeout=timeout, encoding='utf-8')
            # xiaozhan add below line
            self.conn.send(os.linesep)

            if debugFlag:
                self.conn.logfile = sys.stdout  # turn on pexpect debugging
            expect_array = [
                prompt,  # connected and at boot loader
                '->',  # connected and at vxworks C interpreter
                pexpect.EOF,  # disconnected
                pexpect.TIMEOUT,  # time out
            ]

            for _ in range(1):
                i = self.conn.expect(expect_array, timeout)

                if i == 0:
                    return 'T_BOOTLOADER'
                elif i == 1:
                    return 'T_VXWORKS'
                elif i == 2:
                    return 'T_EOF'
                elif i == 3:
                    return 'T_TIMEOUT'
            else:
                raise VLMException('\nFailed to login using telnet')

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
        debugPrint('connOpen')
        if self.conn:
            return self.conn

        status = self.__connect(self.bootPrompt)

        # return self.conn
        return status

    def __checkPexpectVersion(self):
        if pexpect.__version__ < '4.2.1':
            print('pexpect version %s not supported, should be 4.2.1 or later' % pexpect.__version__)
            sys.exit(1)

    def connClose(self):
        debugPrint('connClose')
        self.__disconnect()

    def send(self, cmd):
        if self.conn:
            print('\n--- send="%s"' % cmd)
            self.conn.sendline(cmd)
        else:
            raise VLMException('self.conn not set up')

    def expect(self, expect, timeout=20):
        if self.conn is not None:
            print('\n--- expect="%s" within %s seconds' % (expect, timeout))
            return self.conn.expect(expect, timeout=timeout)
        else:
            raise VLMException('self.conn not set up')

    def sendAndExpect(self, cmd, expect, timeout=120):
        if self.conn is not None:
            self.conn.sendline(cmd)
            return self.conn.expect(expect, timeout=timeout)
        else:
            raise VLMException('self.conn not set up')

    def sendAndReturnAll(self, cmd, expect, timeout=60):
        '''return the lines not empty, each line gets stripped'''
        if self.conn is not None:
            # print('---send:%s' % cmd)
            self.conn.sendline(cmd)
            # print('---expect:%s' % expect)
            ret = self.conn.expect(expect, timeout=timeout)
            lines = self.conn.before.split('\n')
            # print('---before=|%s|' % self.conn.before)
            # print('---after=|%s|\n' % self.conn.after)
            return filter(lambda x: x != '',
                          map(lambda x: x.strip(), lines))
        else:
            raise VLMException('self.conn not set up')

    def sendAndReturnAllByTimeout(self, cmd, timeout=30, strip_lines=True):
        '''return the lines not empty, each line gets stripped'''
        if self.conn is not None:
            logfile = tempfile.mktemp(prefix='tmp')
            magic_start = 'start_magic_magic_start'
            magic_stop = 'stop_magic_magic_stop'

            # save pexpect config
            old_timeout = self.conn.timeout
            old_logfile = self.conn.logfile

            self.conn.timeout = timeout + 10

            with open(logfile, 'w', encoding="utf-8") as fdw:
                self.conn.logfile = fdw
                self.conn.send('echo ' + magic_start + '\n')
                self.conn.expect(magic_start)

                self.conn.send(cmd + '\n')
                time.sleep(timeout)

                self.conn.send('echo ' + magic_stop + '\n')
                self.conn.expect(magic_stop)

            # restore pexpect config
            self.conn.timeout = old_timeout
            self.conn.logfile = old_logfile

            with open(logfile, 'r', encoding='utf-8') as fdr:
                content = fdr.read()

            run_cmd('rm -f %s' % logfile)

            # different version pexpects return slightly different results
            ptn = r'(?s)%s\s*(.*?)%s' % (self.osPrompt + cmd, 'echo ' + magic_stop)
            found = re.search(ptn, content)
            if found is not None:
                content = found.groups()[0].replace(magic_start, '').strip()
                if strip_lines:
                    return list(map(lambda line: line.strip(), content.split('\n')))
                else:
                    return list(map(lambda line: line, content.split('\n')))
            else:
                return []
        else:
            raise VLMException('self.conn not set up')


class VlmUbootTarget(VlmTarget):
    def setup(self, hostIp, clientIp, imagePath, dtbPath, timeout=120, netMask='255.255.255.0'):
        debugPrint('setup')
        # bootArgs = 'gem(0,0)host:vxWorks h=128.224.178.153 e=128.224.167.182:fffffe00 g=128.224.166.1 u=wrsadmin pw=kernel f=0x0'
        bootArgs = '%s host:vxWorks h=%s e=%s:%s g=%s u=%s pw=%s f=0x0' % (
            self.netDriver, hostIp, clientIp, toHexStr(self.IP_Mask), self.Gateway, self.user, self.password)
        bootArgs = 'setenv bootargs \'%s\'' % bootArgs
        print('setenv bootargs', bootArgs)
        # bootCmd = 'tftpboot 0x01000000 /folk/xli3/tsn_trial/ZCU102_Image/uVxWorks; tftpboot 0x0f000000 /folk/xli3/tsn_trial/ZCU102_Image/xlnx-zcu102.dtb; bootm 0x01000000 - 0x0f000000'
        bootCmd = 'tftpboot %s %s; tftpboot %s %s; bootm %s - %s' % (
            self.imageStartAddr, imagePath, self.dtbStartAddr, dtbPath, self.imageStartAddr, self.dtbStartAddr)
        bootCmd = 'setenv bootcmd \'%s\'' % bootCmd
        status = self.connOpen()  # xiaozhan here
        print('=== connOpen() status:%s' % status)

        if status == 'T_BOOTLOADER':
            self.sendAndExpect('setenv ipaddr %s' % clientIp, self.bootPrompt)
            self.sendAndExpect('setenv netmask %s' % self.IP_Mask, self.bootPrompt)
            self.sendAndExpect('setenv serverip %s' % hostIp, self.bootPrompt)
            self.sendAndExpect('setenv gatewayip %s' % self.Gateway, self.bootPrompt)

            self.sendAndExpect(bootArgs, self.bootPrompt)
            self.sendAndExpect(bootCmd, self.bootPrompt)
            self.sendAndExpect('boot', self.osInitDone, timeout=timeout)
        elif status == 'T_VXWORKS':
            self.sendAndExpect('reboot', self.autoBootFlag)
            self.send('\n')  # send return key
            self.expect(self.bootPrompt, 10)

            self.sendAndExpect('setenv ipaddr %s' % clientIp, self.bootPrompt)
            self.sendAndExpect('setenv netmask %s' % self.IP_Mask, self.bootPrompt)
            self.sendAndExpect('setenv serverip %s' % hostIp, self.bootPrompt)
            self.sendAndExpect('setenv gatewayip %s' % self.Gateway, self.bootPrompt)

            self.sendAndExpect(bootArgs, self.bootArgs)
            self.sendAndExpect(bootCmd, self.bootPrompt)
            self.sendAndExpect('boot', self.osInitDone, timeout=timeout)

        else:
            raise VLMException('\nstatus is not right')

        self.status = 'SETUP'
        return self.status == 'SETUP'

    def load(self, hostIp, clientIp, imagePath, dtbPath, workaround=False):
        waitReboot = 120
        for num in range(1):
            try:
                self.setup(hostIp, clientIp, imagePath, dtbPath, timeout=waitReboot)
                if self.status != 'SETUP':
                    raise VLMException('failed to setup the target %s' % self.id)

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
        return self


class VlmVxbootTarget(VlmTarget):
    def setup(self, hostIp, clientIp, imagePath, dtbPath, timeout=120):
        debugPrint('setup')
        # set up vxboot boot parameters, e.g.
        # @gei(0,0)pek-cc-pb02l:/view_test/lchen3/vxcert/tftpboot/vxWorks
        # h=128.224.160.44 e=128.224.167.56:fffffe00 g=128.224.166.1 u=target tn=itl_64 pw=vxTarget
        bootArgs = '@%s%s:%s h=%s e=%s:%s g=%s u=%s tn=%s pw=%s' % (
            self.netDriver, hostIp, imagePath, hostIp, clientIp, toHexStr(self.IP_Mask), self.Gateway, self.user,
            'itl_64', self.password)
        print('bootargs', bootArgs)
        status = self.connOpen()  # xiaozhan here
        print('=== connOpen() status:%s' % status)

        if status == 'T_BOOTLOADER':
            print('xiaozhan bootloader')
            self.sendAndExpect(bootArgs, self.osInitDone)
        elif status == 'T_VXWORKS':
            self.sendAndExpect('reboot', self.autoBootFlag)
            self.send('\n')  # send return key
            self.expect(self.bootPrompt, 10)
            print('xiaozhan send bootargs', self.conn.before)
            self.sendAndExpect(bootArgs, self.osInitDone)
        else:
            raise VLMException('\nstatus is not right')

        self.status = 'SETUP'
        return self.status

    def load(self, hostIp, clientIp, imagePath, dtbPath):
        waitReboot = 120
        for num in range(1):
            try:
                self.setup(hostIp, clientIp, imagePath, dtbPath, timeout=waitReboot)
                if self.status != 'SETUP':
                    raise VLMException('failed to setup the target %s' % self.id)

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
        return self


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


def my_test_VlmVxbootTarget():
    board = '16278'  # 25096
    hostIp = '128.224.153.135'
    imagePath = '/folk/lchen3/tftpboot/IA_TSN/vxWorks'
    dtbPath = None
    ipAddr, tgt = loadImageToTarget(board, hostIp, None, imagePath, dtbPath)

    print('board %s ip address: %s' % (board, ipAddr))

    cmds = ('ipAttach 5,"gei"',
            'ifconfig "gei5 10.10.10.3/24 up"',
            'ptpdAdd "gei5",4,2,0,0,200,0,0',
            'ptpdStart',
            'ptpdSetDebugLevel "gei5", 1',
            'ptpdSetDebugLevel "gei5", 0',
            )
    for cmd in cmds:
        if cmd.startswith('ptpdSetDebugLevel'):
            lines = tgt.sendAndReturnAllByTimeout(cmd, timeout=15)
        else:
            lines = tgt.sendAndReturnAll(cmd, '-> ', timeout=3)
        print('CMD=|%s|\nRET=|%s|\n\n' % (cmd, '\n'.join(lines)))
        time.sleep(1)

    print('end of test_VlmVxbootTarget')
    tgt.connClose()


def my_test_VlmUbootTarget():
    board = '28564'  #
    hostIp = '128.224.153.135'
    imagePath = '/folk/lchen3/tftpboot/ARM_ZCU102/uVxWorks'
    dtbPath = '/folk/lchen3/tftpboot/ARM_ZCU102/xlnx-zcu102.dtb'
    ipAddr, tgt = loadImageToTarget(board, hostIp, None, imagePath, dtbPath)

    print('board %s ip address: %s' % (board, ipAddr))
    lines = tgt.sendAndReturnAll('version', tgt.osPrompt)
    print('\n'.join(lines))
    tgt.conn.logfile_read = None
    tgt.conn.interact()
    # input('wait to close...')
    tgt.connClose()


def test_helix_VxbootTarget():
    print('the script must be run at pek-canoepass which has directly-linked target 28567')
    import socket
    host = socket.gethostname()
    if host.startswith('pek-canoepass'):
        sudovoid('sudo ifconfig enp7s0f1 10.0.0.200')
        board = '28567'
        hostIp = '10.0.0.200'
        clientIp = '10.0.0.2'
        imagePath = '/folk/lchen3/tftpboot/helix/itl_generic/vxWorks'
        dtbPath = None
        ipAddr, tgt = loadImageToTarget(board, hostIp, clientIp, imagePath, dtbPath)
        print('ipAddr=%s' % ipAddr)
        print('tgt=%s' % tgt)

        lines = tgt.sendAndReturnAll('version', tgt.osPrompt)
        print('\n'.join(lines))
        sudovoid('sudo ifconfig enp7s0f1 0.0.0.0')


def boot_target_16278():
    board = '16278'
    hostIp = '128.224.178.153'
    clientIp = '128.224.167.52'
    imagePath = '/folk/xli3/tsn_trial/IA_Image/vxWorks'
    dtbPath = None
    tgt = loadImageToTarget(board, hostIp, clientIp, imagePath, dtbPath)
    # tgt.sendAndReturnAll('ifconfig', 'value = 0 = 0x0', timeout=60)
    # tgt.connClose()
    return tgt


def boot_target_18290():
    board = '18290'
    hostIp = '128.224.178.153'
    clientIp = '128.224.166.239'
    imagePath = '/folk/xli3/tsn_trial/IA_Image/vxWorks'
    dtbPath = None
    tgt = loadImageToTarget(board, hostIp, clientIp, imagePath, dtbPath)
    # tgt.sendAndReturnAll('ifconfig', 'value = 0 = 0x0', timeout=60)
    # tgt.connClose()
    return tgt


def boot_target_28572():
    board = '28572'
    hostIp = '128.224.178.153'
    clientIP = '128.224.167.182'
    imagePath = 'uVxWorks'  # xiaozhan here should not be full path
    dtbPath = 'xlnx-zcu102.dtb'
    tgt = loadImageToTarget(board, hostIp, clientIP, imagePath, dtbPath)
    # tgt.sendAndReturnAll('ifconfig', 'value = 0 = 0x0', timeout=60)
    # tgt.connClose()
    return tgt


tgt1 = boot_target_16278()
tgt2 = boot_target_18290()

if __name__ == '__main__':
    # main()
    # test_vxboot_target()
    # my_test_VlmVxbootTarget()
    # my_test_VlmUbootTarget()
    # boot_target_16278()
    boot_target_28572()
