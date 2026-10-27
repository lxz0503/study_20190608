from __future__ import print_function
from __future__ import absolute_import

import argparse, os, sys, time, getopt, re, logging
import signal, fcntl, termios, struct
import pexpect
sys.path.insert(0, '/home/xli3/kong')
from testEngine import ip
from target import NetworkBuilder, QemuTarget, VlmVxbootTarget, VlmUbootTarget, VxWorksBuild, ConfigError, loadImageToTarget  
from util import readYaml, checkPath, copyTree

def demo_VlmVxbootTarget():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S')

    board = '28514'
    hostIp = '128.224.153.34' # pek-vx-nwk1
    
    build = VxWorksBuild('/folk/lchen3/tftpboot/IA/vxWorks', dtb=None, user='ftp', passwd='interpeak')
    target = VlmVxbootTarget(board, logFile='vlm%s.log' % board)
    console = loadImageToTarget(target, build, hostIp)
    
    print('board %s, ip address: %s' % (board, target.ip.get_addr_str()))
    #inKey = input('go to vxworks command line shell?(yes/no)')      # python 3.x
    inKey = input('go to vxworks command line shell?(yes/no)')   # python 2.x
    if inKey == 'yes':
        console.sendline('cmd')
        console.expect('# ')

    input('wait to close...')      # python 3.x
    target.cleanup()

def demo_VlmUbootTarget():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
    
    board = '25003'
    hostIp = '128.224.153.34' # pek-vx-nwk1
    imagePath = '/folk/lchen3/tftpboot/ARM/uVxWorks'
    dtbPath = '/folk/lchen3/tftpboot/ARM/imx6q-sabrelite.dtb'
    
    build = VxWorksBuild(imagePath, dtb=dtbPath, user='ftp', passwd='interpeak')
    target = VlmUbootTarget(board, logFile='vlm%s.log' % board)
    console = loadImageToTarget(target, build, hostIp)

    print('board %s, ip address: %s' % (board, target.ip.get_addr_str()))
    inKey = input('go to vxworks command line shell?(yes/no)')      # python 3.x
    if inKey == 'yes':
        console.sendline('cmd')
        console.expect('# ')

    input('wait to close...')      # python 3.x
    target.cleanup()

def getNICName(content):
    nicNames = []
    lines = content.split('\n')
    print('lines are', lines)
    for line in lines:
        if not line[0] in (' ', '\t',) and line.find('Link type:') != -1:
            name = line.split(' ')[0].split('\t')[0]
            if name.strip() and name != 'lo0':
                nicNames.append(name)
    return nicNames
            
def mainTwoBoards(noBridge, debug=True):
    logfile1 = open('qemu1.log', 'wb')
    logfile2 = open('qemu2.log', 'wb')
    
    try:    
        targets = [QemuTarget('QEMU-Q35-%s' % (x + 1), logFile='qemu%s.log' % (x+1)) for x in range(0, 2)]
        ips = [ip('192.168.123.%s/24' % (102 + x)) for x in range(0, 2)]
        vxBuild = VxWorksBuild('/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu/vxWorks', dtb=None, user='wrsadmin', passwd='kernel')
        builds = [vxBuild, vxBuild]
        
        if noBridge:
            bridgeName = input('you have to manually set up a bridge first, please input bridge name:')
            netbdr = NetworkBuilder(targets, builds, ips, bridge=bridgeName)
        else:
            netbdr = NetworkBuilder(targets, builds, ips)
        netbdr.setup()
        # input('go to network.start()?')       # python 3.x
        print('go to network.start()')
        # consoles = netbdr.start()
        netbdr.start()

        for target in targets:
            print('\n=== enter console %s vxworks command line' % targets.index(target))
            # console = target.console      # xiaozhan, remove
            target.sendAndExpect('cmd', '# ')
            content = '\n'.join(target.sendAndReturnAll('ifconfig -a', '# ')[1:])
            print('=======content is=========\n', content)
            # print(getNICName(content))
            print('=== disable HW checksum')
            target.sendAndExpect('ethtool -K eth0 rx off', '# ')
        # netbdr.cleanup()
        # xiaozhan debug
        if debug is True:
            input('pause...')    # xiaozhan,debug
        else:
            pass
    except (pexpect.TIMEOUT, ConfigError) as e:
        print(e)
        print('test failed')
    # xiaozhan, debug, add 3 lines
    finally:
        # xiaozhan, debug
        print('go to network.cleanup()?')       # python 3.x
        netbdr.cleanup()
        for t in targets:
            t.logFile.close()


def mainOneBoard(noBridge):
    logfile = open('qemu.log', 'wb')

    try:    
        vxBuild = VxWorksBuild('/folk/lchen3/tftpboot/IA/vxWorks', dtb=None, user='ftp', passwd='interpeak')
        q35 = QemuTarget('QEMU-Q35-4Disk', logFile=logfile)
        q35.setup(vxBuild, targetIp=None)
        
        #input('go to target.start()?')       # python 3.x
        raw_input('go to target.start()?')    # python 2.x
        console = q35.start()
    
        print('=== enter vxworks command line')    
        console.sendline('cmd')
        console.expect('# ')
        time.sleep(3)
        print('=== input ifconfig -a')
        console.sendline('ifconfig -a')
        console.expect('# ')

        #input('go to target.cleanup()?')       # python 3.x
        raw_input('go to target.cleanup()?')    # python 2.x
        q35.cleanup()
        
        logfile.close()
        print('test passed')
    except (pexpect.TIMEOUT, ConfigError) as e:
        print(e)
        print('test failed')

def printUsageAndExit():
    print('usage: %s 1_or_2_or_3' % os.path.basename(sys.argv[0]))
    sys.exit(1)            

def parseArgument():
    parser = argparse.ArgumentParser('Demo VLM/Qemu target operations')
    parser.add_argument('--vlm', action='store', dest='vlmNum', help='VLM target number')
    parser.add_argument('--qemu', action='store', dest='qemuNum', help='Qemu target number')
    parser.add_argument('--nobridge', dest='noBridge', action='store_true', help='need to create bridge or not')
    parser.add_argument('--debug', dest='debug', help='debug or not')
    r = parser.parse_args()
    
    if ((r.vlmNum is None) and (r.qemuNum is None)) or \
       ((r.vlmNum is not None) and (r.qemuNum is not None)):
        print('one of --vlm and --qemu arguments must be selected')
        parser.print_help()
        sys.exit(1)

    return r
            
if __name__ == "__main__":
    arg = parseArgument()
    print(arg)
    if int(arg.qemuNum) == 1: 
        mainOneBoard(arg.noBridge)
    elif int(arg.qemuNum) == 2:
        mainTwoBoards(arg.noBridge, debug=False)   # xiaozhan
    elif int(arg.vlmNum) == 1:
        demo_VlmVxbootTarget()
    elif int(arg.vlmNum) == 2:
        demo_VlmUbootTarget()
    else:
        printUsageAndExit()
    