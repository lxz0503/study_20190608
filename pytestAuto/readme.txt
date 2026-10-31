conftest.py只负责一些前置或者后置工作--但是不作为test case

最外层的conftest.py---最先被执行--修改了系统的sys.path ---导入了工程根目录
-接下来在每个测试目录里面都不需要再手动执行sys.path.insert(0,'root_dir')
入口函数run_xiaozhan.py  ---也可以在里面添加寻找工程根目录的代码，然后直接修改sys.path.insert(0,root_dir)
 ---session级别-----只负责检测，安装spin


ARM包里面的conftest.py------module级别--只负责检查ARM的image是否编成功
test_1.py里面的第一个case--就是来检查这个包里的conftest.py是否执行成功

IA和PPC同理  ----module级别---------


@gei(4,0)128.224.178.153:/folk/xli3/tsn_trial/IA_Image/vxWorks h=128.224.178.153 e=128.224.167.52:fffffe00 g=128.224.166.1 u=wrsadmin tn=itl_64 pw=kernel

@gei(1,0)128.224.178.153:/folk/xli3/tsn_trial/IA_Image/vxWorks h=128.224.178.153 e=128.224.166.239:fffffe00 g=128.224.166.1 u=wrsadmin tn=itl_64 pw=kernel
conftest.py与运行的测试用例要在同一个package下,并且要有__init__.py文件

=====================
测试--conftest.py里面有多个fixture--如果一个失败--接下来会怎样？
例如我的---安装spin--但是spin不存在--失败，分支上编image--成功

实际测试发现，最好不要在一个conftest.py里面写太多fixture,因为fixture是预置条件
一旦失败，很容易造成混乱--从我的例子来看，加入了3个fixure，其中第一个失败，导致后面俩fixture基本混乱
我在最外层代码添加一个conftest.py---里面只去安装spin---失败了--后面的基本无法进行
因为后面基于这个安装的spin去编image

注意; @pytest.mark.skip() --这个是用在测试用例前面的，如果用在fixture函数的前面--不起作用


spidertools.cn
爬取下面网址信息--保存到csv
so.zhaopin.com/?jl=538&kw=数据分析&p=1
movie.douban.com/top250?    抓取电影  分页

=================================
目前单独执行test_1和test_2都没有问题

from TSN01.utils.vlmTarget import tgt1, tgt2
头部导入tgt1和tgt2只是在整个程序开始执行时候进行-当执行完test_1,再执行test_2,
就不会再去执行一次导入tgt1和tgt2的操作---所以就没法实现重新加载image的目的----正在想办法？？？


在当前架构中，test_1执行完后，关闭串口，然后test_2执行，再去直接调用tgt1发现串口已经关闭
实际需求是需要重新加载image----怎么实现？

解决方案：
from TSN01.utils.vlmTarget import boot_target_16278, boot_target_18290
在类class TestSuite01(object):
    def test_1(self):  # 在下面初始化函数，相当于每次执行新的case都会调用boot_开头的函数--相当于重新加载image
        tgt1 = boot_target_16278()
        tgt2 = boot_target_18290()

================================
如果有spin---代码可以正常运行

框架还存在问题---如果没有新的spin，即安装spin失败--但是仍然会继续在老的spin上去执行case
---这个不符合需求----需要调整代码---
解决方案==？？？？
方案---运行整个框架之前判断是否有spin，有就运行，没有就sys.exit(1)
其实不需要去执行sys.exit(1),因为在判断是否有spin的代码里面有代码：
def GetSpinInfo(commit, action):
    # xiaozhan，这个assert很关键，如果成功，就继续执行，如果失败，这个run_trail.py就会执行失败
    # 也就是不会往下运行Pytest
    assert commit in KongConfig.spinConfig.keys()

rootdir: /home/wrsadmin/TSN01

只有进入到上述目录 执行python3才可以
+ cd /home/wrsadmin/TSN01
+ python3 run_xiaozhan.py
代码里面的路径是相对于Python3解释器的路径的，当前路径就是  /home/wrsadmin/TSN01
====================================================================
单独调试case：自己添加打印
[xli3@pek-vx-29075 TSN01]$ python3 -m pytest -v test_IA/test_3.py

开发需求：
1.抓取串口log----保存到一个文件---log会很大---
解决方案--已经做好--增加一条打印语句即可
因为我的架构设计的是保存sys.stdout,
参考   http://128.224.36.49:8080/job/TSN0/49/allure/data/attachments/8f7dea35b2780079.txt
/home/wrsadmin/Jenkins/workspace/TSN0/allure-report/data/attachments
2.搭建performance环境---增加一个linux server--保持当前架构不动
3.测试报告展示上，更加直观--可以显示各个架构的-例如，I210，I350，LS1028--点击就能看到结果
===================================================================
参考ssh_server.py里面的代码----可以通用
如果没有复杂需求---用之前写的ssh模块的代码即可
SSH到一台linux server，如果执行类似于ping 这种命令，会一直运行，直到ctrl+c
有一些TSN的命令，也是一直运行，然后抓取屏幕上的信息。
正常情况的pexpect模块或者ssh操作，都是send一条命令行，直接去expect一个prompt，但是以上属于
特殊情况，不存在这种prompt，-----解决方案如下
    def sendAndReturnAllByTimeout(self, cmd, cmd_timeout=30, strip_lines=True):
        id, logfile = tempfile.mkstemp(prefix='tmp')  # /tmp
        # print('tempfile=%s' % logfile)
        magic_stop = 'stop_magic_stop'

        # save pexpect config
        old_timeout = self.conn.timeout
        old_logfile = self.conn.logfile

        with open(logfile, 'wb') as fdw:   # must be 'wb'
            self.conn.logfile = fdw
            self.conn.sendline(cmd)
            time.sleep(30)

            cmd2 = 'echo ' + magic_stop + '\n'
            self.conn.sendline(cmd2)
            self.conn.expect(magic_stop)

        # restore pexpect config
        self.conn.timeout = old_timeout
        self.conn.logfile = old_logfile

        with open(logfile, 'rb') as fdr:
            content = fdr.read().decode('utf-8')  # change to string
            # process content based on the original content, it may be different
            content = [line.strip().rstrip('\r\n') for line in content.split('\r\n') if line != '']

        run_cmd('rm -f %s' % logfile)
        # print('content is\n', content)
        return content
代码解析：把屏幕上的输出保存到临时文件里面，然后读取临时文件，必要时候通过正则来获取内容
注意字节和字符串的转换----这个根据实际情况来修改代码
with open(logfile, 'wb') as fdw:   # must be 'wb' 必须是字节形式 即二进制，根据实际情况，有时候是w
    self.conn.logfile = fdw    # 临时文件
    self.conn.sendline(cmd)    # 发送命令
    time.sleep(30)    #  命令只是30秒，会输出很多内容

    cmd1 = 'echo ' + magic_stop + '\n'
    self.conn.sendline(cmd1)     # 执行下一条命令，其实这条命令是什么不重要，只有能获取到prompt即可
    self.conn.expect(magic_stop)  # 这个命令自己写了一个prompt，设定了关键字
    # 如果没有上面的sendline和expect，最上面那条sendline就会超时，因为没有和它相匹配的prompt

   #注意，如果用self.conn.before来获取，则必须是sendline和expect成对出现
   #因为self.conn.before只能获取最近的一组sendline和expect数据--以代码为例，最上面那条sendline后输出的
   内容不会被获取到
=========================================================================
修改29075上的Jenkins工作目录为/home/xli3/Jenkins
需要disconnect或者offline这个节点，然后重新launch这个节点即可
============================================================================
在linux机器上，没有安装pycharm，类似于命令行，所以系统不会自动设置工程路径，需要自己添加

from utils.nightlyInfo import nightlyInfo
但是在windows的pycharm上是不需要上面的设置的，
即用 from pytestAuto.utils.nightlyInfo import nightlyInfo
===============================================================
pytest---目录结构如下
/home/xli3/pytestAuto/test-cases/network-iperf/iperf-server-29075
[xli3@pek-vx-29075 iperf-server-29075]$ ll
total 12K
-rw-r--r-- 1 xli3 users    0 Jan 12 11:34 __init__.py
drwxr-xr-x 2 xli3 users 4.0K Jan 13 10:25 __pycache__/
-rw-r--r-- 1 xli3 users 1.3K Jan 13 10:14 conftest.py
-rw-r--r-- 1 xli3 users 3.3K Jan 13 10:24 test_28610.py    # 必须以test_开头或者_test为结尾
=========================================================================
pytest并发，我的框架里面有conftest.py并且是auto session级别的
从Jenkins的log能看出---所谓的并发--上来就是根据test_.py中的case个数按照cpu做了分配
感觉conftest.py和所有test case一起执行了---这个不是我想要的---按理说不该这样--继续调研
我需要的是conftest.py必须执行在前---然后才是test case---但是即使有疑问，测试结果依然正常

scheduling tests via LoadScheduling

test-cases/network-iperf/iperf-server-29075/test_28610.py::TestSuite28610::test_tcp_1024
test-cases/network-iperf/iperf-server-29075/test_28610.py::TestSuite28610::test_udp_1400
test-cases/network-iperf/iperf-server-29075/test_28610.py::TestSuite28610::test_tcp_65536
test-cases/network-iperf/iperf-server-29075/test_28610.py::TestSuite28610::test_tcp_64
从上面的log能看出以上四个case打算分配在不同的进程来执行---但实际上一个target上只能同时执行一个case
所以造成有时候加载image失败---
class TestSuite28610(object):
    def setup_class(self):
        self.tgt = boot_target_28610()
        self.tgt.sendAndExpect('ipAttach 0,"gei"', 'value = 0 = 0x0', timeout=60)
        self.tgt.sendAndExpect('ifconfig "gei0 192.168.10.3/24 up"', 'value = 0 = 0x0', timeout=60)
        self.tst_dict = {}

    def teardown_class(self):
        self.tgt.connClose()
从并发的实际测试经验来看---每个def test()函数里面的都需要和前面的setup_class()关联起来作为一个整体
这才算是一个整体的case---所以实际执行每个def test()函数都去加载一次image---这不是我想要的
-----IPERF并发宣告失败
如果不并发--执行时间---18分钟--http://128.224.153.29:8888/job/xiaozhan-pytest-auto/8/console
单独并行编译，设置俩空的case--执行时间 http://128.224.153.29:8888/job/xiaozhan-pytest-auto/14/console
----用了6分钟

如果不是并行编译----http://128.224.153.29:8888/job/xiaozhan-pytest-auto/15/consoleFull
----时间为7分钟
==============================================================
添加一个debug开关---可以选择是用spin还是local branch来测试，只有debug支持并行
python工程路径是/home/xlie/pytestAuto ---所以里面的读写yaml的路径设置为相对路径即可
read_yaml('config/debug.yaml')
同时在每个conftest.py里面增加和上面一样的debug判断
==================================================
调试单个函数的时候--进入pytestAuto目录，执行下面的命令
[xli3@pek-vx-29075 pytestAuto]$ pytest -s test-cases/network-iperf/iperf-server-29075/test_28610.py::TestSuite28610::test_tcp_64

pytest -s test-cases/network-protocl/tftp/test_tftp.py::TestTFTP::test_tftp_1
================================================================================
                SPIN
git=/home/wrsadmin/SPIN/vx20240109165519_vx_2403
+ pkgname=24.03
+ echo 24.03
24.03
+ wrenv='/home/wrsadmin/SPIN/vx20240109165519_vx_2403/wrenv.linux -p vxworks/24.03 LM_LICENSE_FILE=27000@ala-lic4.wrs.com'
+ bsp=itl_generic
+ tool=llvm
+ vsbDir=/home/wrsadmin/SPIN/vx20240109165519_vx_2403/vsb_itl_generic_tsn
+ vipDir=/home/wrsadmin/SPIN/vx20240109165519_vx_2403/vip_itl_generic_tsn
+ true
+ sudo rm -fr /home/wrsadmin/SPIN/vx20240109165519_vx_2403/vsb_itl_generic_tsn
===================================================================================
branch
[xli3@pek-vx-29075 common]$ python3 get-vx-env.py
('/home/xli3/vxworks/vxworks/relx/source/os', '/home/xli3/vxworks/wrenv.sh -p vxworks')
==========================================================================================
git=/home/xli3/vxworks
+ wrenv='/home/xli3/vxworks/wrenv.linux -p vxworks/relx'
+ bsp=xlnx_zynqmp
+ tool=llvm
+ vsbDir=/home/xli3/vxworks/vsb_xlnx_zynqmp
+ vipDir=/home/xli3/vxworks/vip_xlnx_zynqmp
+ true
+ sudo rm -fr /home/xli3/vxworks/vsb_xlnx_zynqmp

==================================================================================
run-shell.py 可以在linux上执行shell的命令---返回一个list---自己根据情况再处理返回内容

    def getAttr(self, output=''):
        log.info('getAttr %s' % self.board)
        if not output:
            _, self.output = self.__vlmToolCmd('getAttr', self.board)

        for line in [x for x in self.output.split('\n') if x.strip()]:
                k,v = line.split(': ',1)
                k=k.replace(' ','_').replace('\t','')
                setattr(self, k, v.strip())
                log.debug('DEBUG target attribute  "%s" : "%s"\n' % (k,v))


[xli3@pek-vx-29075 pytestAuto]$ vlmTool getAttr -s amazon.wrs.com -t 28610 all
Target ID       : 28610
Master Target ID: 28610
Target Alias    : xilinx_zcu102_Rev1.1
BSP             : xilinx_zcu102
Architecture    : ARM
CPU             : AMR-Cortex-A53
CPU Speed       : 0
CPU L1 I-Cache  : 0
CPU L1 D-Cache  : 0
CPU L2 Cache    : 0
CPU Bitsize     :
Memory Size     : 0
Flash Size      : 0
Endianness      :
Bootrom Version :
Bootrom Built   :
Boot Device     : eth0
Serial Port     : null
MAC Address     : 00:00:00:00:00:00
IP Address      : 128.224.166.193
IP Alias        : null
IP Mask         : 255.255.254.0
Gateway         : 128.224.166.1
Reserved By     : xli3
Reserved Date   : Tue Jan 16 01:26:32 PST 2024
Reserve Note    :
Zone            : BeijingVxNwkPerfTest
Room            : B1F BJ E10
Street Address  : Beijing HMT B1
City            : Beijing
State           : -
Country         : CHINA
Terminal Server : 128.224.157.61
Terminal Server Port: 27
============================================================
def boot_target_28610():
    board = '28610'
    hostIp = '128.224.178.153'
    imagePath = 'uVxWorks-IPERF'  # xiaozhan here should not be full path
    dtbPath = 'xlnx-zcu102-rev-1.1.dtb-IPERF'
    tgt = loadImageToTarget(board, hostIp, None, imagePath, dtbPath)  # xiaozhan，修改了返回值
    return tgt
==============================================================
class VlmVxbootTarget(VlmTarget):
    # set up boot parameters
    def setup(self, hostIp, clientIp, imagePath, dtbPath, timeout=120):
        return self.status
    # load image and return console
    def load(self, hostIp, clientIp, imagePath, dtbPath):
        self.setup(hostIp, clientIp, imagePath, dtbPath, timeout=waitReboot)
        return self.IP_Address, self   # xiaozhan, this needs to improve---直接删除返回值-用不到

=============================================================
def loadImageToTarget(board, hostIp, clientIp, imagePath, dtbPath):
    bootLoader = vlmTargetConfigs[board]['bootLoader']
    if bootLoader == 'uboot':
        target = VlmUbootTarget(board)
    elif bootLoader == 'vxboot':
        target = VlmVxbootTarget(board)
    else:
        raise VLMException('unsupported boot loader %s' % bootLoader)
    # xiaozhan, target is the class instance
    target.load(hostIp, clientIp, imagePath, dtbPath)
    return target    # 这个才是想要的类实例--里面包含了各种方法
==============================================================================
修改def load()函数---取消里面的返回值，用不到

Getting started : https://docs.pytest.org/en/stable/getting-started.html
How to guide : https://docs.pytest.org/en/stable/how-to/index.html
Passing test data : https://automationpanda.com/2023/01/12/passing-test-inputs-into-pytest/
=======================================================================
python单例设计模式
http://www.coolpython.net/informal_essay/20-09/five-methods-to-achieve-singleton.html
====================================================================
如何添加bridge
sudo brctl addbr vxBridge
sudo tunctl -t tap1
sudo ifconfig tap1 0.0.0.0 up
sudo ifconfig enp1s0f1 0.0.0.0 up
sudo brctl addif vxBridge tap1
sudo brctl addif vxBridge enp1s0f1
sudo brctl show
sudo ifconfig vxBridge 101.10.10.100/24 up
=====================================================================================
enp1s0f1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        ether 00:15:17:a2:16:df  txqueuelen 1000  (Ethernet)
        RX packets 1042630990  bytes 586263515332 (586.2 GB)
        RX errors 0  dropped 905  overruns 905  frame 0
        TX packets 81690531  bytes 6650157378 (6.6 GB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        device memory 0xb2100000-b211ffff

tap1: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet6 fe80::787a:aff:fe0a:afe  prefixlen 64  scopeid 0x20<link>
        ether 7a:7a:0a:0a:0a:fe  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 5388635  bytes 463643883 (463.6 MB)
        TX errors 0  dropped 6177271 overruns 0  carrier 0  collisions 0

vxBridge: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 101.10.10.100  netmask 255.255.255.0  broadcast 101.10.10.255
        inet6 fe80::215:17ff:fea2:16df  prefixlen 64  scopeid 0x20<link>
        ether 00:15:17:a2:16:df  txqueuelen 1000  (Ethernet)
        RX packets 963978159  bytes 567575184225 (567.5 GB)
        RX errors 0  dropped 2416  overruns 0  frame 0
        TX packets 81690373  bytes 6650133512 (6.6 GB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
=========================================================================================
xli3@pek-vx-29075 kong]$ python3 example/demoTarget.py --qemu 2

sudo apt-get install bridge-utils
sudo apt install uml-utilities

[xli3@pek-vx-29075 kong]$ sudo brctl delif br-vm-123
Incorrect number of arguments for command
Usage: brctl delif <bridge> <device>    delete interface from bridge
[xli3@pek-vx-29075 kong]$ sudo brctl del br-vm-123
never heard of command [del]
Usage: brctl [commands]
commands:
        addbr           <bridge>                add bridge
        delbr           <bridge>                delete bridge
        addif           <bridge> <device>       add interface to bridge
        delif           <bridge> <device>       delete interface from bridge
        hairpin         <bridge> <port> {on|off}        turn hairpin on/off
        setageing       <bridge> <time>         set ageing time
        setbridgeprio   <bridge> <prio>         set bridge priority
        setfd           <bridge> <time>         set bridge forward delay
        sethello        <bridge> <time>         set hello time
        setmaxage       <bridge> <time>         set max message age
        setpathcost     <bridge> <port> <cost>  set path cost
        setportprio     <bridge> <port> <prio>  set port priority
        show            [ <bridge> ]            show a list of bridges
        showmacs        <bridge>                show a list of mac addrs
        showstp         <bridge>                show bridge stp info
        stp             <bridge> {on|off}       turn stp on/off
[xli3@pek-vx-29075 kong]$ sudo ifconfig tap-QEMU-Q35-1 down
[xli3@pek-vx-29075 kong]$ sudo ifconfig tap-QEMU-Q35-2 down
[xli3@pek-vx-29075 kong]$ sudo ifconfig br-vm-123 down
[xli3@pek-vx-29075 kong]$ sudo brctl delbr br-vm-123



[xli3@pek-vx-29075 kong]$ ifconfig
br-vm-123: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 192.168.123.1  netmask 255.255.255.0  broadcast 192.168.123.255
        inet6 fe80::70c0:42ff:fe92:c9d7  prefixlen 64  scopeid 0x20<link>
        ether 72:c0:42:92:c9:d7  txqueuelen 1000  (Ethernet)
        RX packets 7  bytes 440 (440.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 26  bytes 3058 (3.0 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

tap-QEMU-Q35-1: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet6 fe80::800b:8cff:fe1b:7538  prefixlen 64  scopeid 0x20<link>
        ether 82:0b:8c:1b:75:38  txqueuelen 1000  (Ethernet)
        RX packets 5  bytes 388 (388.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 20  bytes 2476 (2.4 KB)
        TX errors 0  dropped 3 overruns 0  carrier 0  collisions 0

tap-QEMU-Q35-2: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet6 fe80::70c0:42ff:fe92:c9d7  prefixlen 64  scopeid 0x20<link>
        ether 72:c0:42:92:c9:d7  txqueuelen 1000  (Ethernet)
        RX packets 2  bytes 150 (150.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 5  bytes 408 (408.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
==================================================================================
程序运行完  串口就没了  无法telnet --必须自己加代码停住demoTarget.py
加了一行input 语句    input('pause...')    # xiaozhan,debug
然后就能telnet到qemu上了-----自己加了打印--没有用--后来想到父子进程

def cleanup(self):
        if self.console is not None:
            if self.debug:
                print('=== quit target %s' % self.board)
            if not self.console.terminate(force=True):
                if self.debug:
                    print('use ctrl+c to quit target')
                self.console.sendcontrol('c')         ---退出qemu  关闭
                self.console.expect(pexpect.EOF)

        if self.bridge is not None:
            shellCmd('sudo ifconfig %s down' % self.tapName, debug=self.debug)
            shellCmd('sudo brctl delif %s %s' % (self.bridge, self.tapName), debug=self.debug)
            shellCmd('sudo tunctl -d  %s' % self.tapName, debug=self.debug)

父子进程：
demoTarget.py--这个是父进程--进程ID 1545617
下面有两个子进程---所以当主进程即python程序结束后，子进程自动结束--如果不结束--也会被init清掉
root     1545645 1545617  0 13:24 pts/3    00:00:00 /usr/bin/sudo qemu-system-x86_64 -machine q35 -
root     1545752 1545617  0 13:24 pts/4    00:00:00 /usr/bin/sudo qemu-system-x86_64 -machine q35
[xli3@pek-vx-29075 kong]$ ps -ef
UID          PID    PPID  C STIME TTY          TIME CMD
xli3     1545617  166914  0 13:24 pts/2    00:00:00 python3 example/demoTarget.py --qemu 2
root     1545632       2  0 13:24 ?        00:00:00 [kworker/6:1-events]
root     1545643       2  0 13:24 ?        00:00:00 [kworker/7:0-mm_percpu_wq]
root     1545645 1545617  0 13:24 pts/3    00:00:00 /usr/bin/sudo qemu-system-x86_64 -machine q35 -m 2048 -smp 4 --serial stdio -ke
root     1545646 1545645  8 13:24 pts/3    00:00:01 qemu-system-x86_64 -machine q35 -m 2048 -smp 4 --serial stdio -kernel /folk/xli
root     1545651       2  0 13:24 ?        00:00:00 [kvm-nx-lpage-re]
root     1545656       2  0 13:24 ?        00:00:00 [kvm-pit/1545646]
root     1545752 1545617  0 13:24 pts/4    00:00:00 /usr/bin/sudo qemu-system-x86_64 -machine q35 -m 2048 -smp 4 --serial stdio -ke
root     1545753 1545752  8 13:24 pts/4    00:00:01 qemu-system-x86_64 -machine q35 -m 2048 -smp 4 --serial stdio -kernel /folk/xli
==============================================================================
sudo brctl show
./env-clean.sh
ps -eaf | grep qemu
ip addr
telnet 192.168.123.102 2323
============================================
python3 demoVxBuild.py     ----try it on branch
增加下面一处调试---调试qemu用
if debug is True:
    input('pause...')
===========================================================
python3 example/demoTarget.py  --qemu 2 --debug=True

==============================================================
[xli3@pek-vx-29075 pytestAuto]$ pytest -s test-cases/network-protocol/tftp/test_tftp.py::TestTFTP::test_tftp_1

[xli3@pek-vx-29075 kong]$ telnet 192.168.123.102 2323
Trying 192.168.123.102...
Connected to 192.168.123.102.
Escape character is '^]'.

->
-> cmd
[vxWorks]#
================================================================================
testEngine.py-------class ShellOperations(object):   里面有交互的实现---需要看一下实现，最好直接套用到minikong
应该需要在target.py里面去实现这些交互动作
from utils.testEngine import ip, ShellOperations   -----已经导入了模块---去尝试一下功能
/buildarea1/lchen3/vxworks-new/vxworks/relx/source/os/net/ipnet/coreip/src/ipcom/util/scripts

http://pek-kong-01.wrs.com:8080/view/pek-sec-kong-02/job/new-ci-build-slave/  -----找到每个模块的编译需要的组件 例如DHCP
http://pek-kong-01.wrs.com:8080/view/pek-sec-kong-02/job/new-ci-build-slave/21369/consoleFull    ---DHCP的编译


KONG case的例子： 是在cmd shell
[vxWorks]# tftp
usage: tftp [-a] <host [port]> <get|put> <source> [destination]
[vxWorks]# tftp -a noserver.interpeak.se get no_server.txt
Unknown host: noserver.interpeak.se
[vxWorks]#
====================================================================
ANVL  ---example for sysvar
-> cmd sysvar set -co ipike.strict_lifetime_policy "1"
sysvar: ipike.strict_lifetime_policy=1 ok
-> cmd sysvar get ipike.strict_lifetime_policy
sysvar: ipike.strict_lifetime_policy=1
-> cmd sysvar set -co ipike.filename "/romfs/ANVL_ikev1_resp.cfg"
sysvar: ipike.filename=/romfs/ANVL_ikev1_resp.cfg ok
-> cmd sysvar list ipike.filename

[xli3@pek-vx-29075 vxworks]$ find ./ -name 'iptestengine.py'
./vxworks/relx/source/os/net/ipnet/NOT_IMPORTED/iptestengine/src/iptestengine.py
[xli3@pek-vx-29075 vxworks]$ vi ./vxworks/relx/source/os/net/ipnet/NOT_IMPORTED/iptestengine/src/iptestengine.py
check this function---- set_sysvar  ----class Target() is the key

./vxworks/relx/source/os/net/ipnet/app/tftp/test/tftp.py   ---check tftp cases

./vxworks/relx/source/os/net/ipnet/coreip/src/ipcom/util/scripts/runtestsuites_conf.py  ---every test suite config
kong -- test code--/home/xli3/vxworks/vxworks/relx/source/os/net/ipnet/coreip/src

http://pek-kong-01.wrs.com:8080/view/pek-sec-kong-02/job/new-ci-build-slave/21410/

/folk/xli3/tsn_trial/ZCU102_Image   ---tftp dir

    def ip(self, v6=''):
        if v6 == '6':
            return self.ts.primary_ip6
        else:
            return self.ts.primary_ip

 =======content is=========
 inet 127.0.0.1  mask 255.255.255.255
inet6 unicast fe80::1%lo0  prefixlen 64  automatic
inet6 unicast ::1  prefixlen 128
UP RUNNING LOOPBACK MULTICAST NOARP ALLMULTI
MTU:1500  metric:1  VR:0  ifindex:1
RX packets:22 mcast:0 errors:0 dropped:0
TX packets:22 mcast:0 errors:0
collisions:0 unsupported proto:0
RX bytes:960  TX bytes:960

eth0    Link type:Ethernet  HWaddr 52:55:c0:a8:7b:66
capabilities: VLAN_MTU VLAN_TXHWTAG VLAN_RXHWTAG
inet 192.168.123.102  mask 255.255.255.0  broadcast 192.168.123.255
inet6 unicast fe80::5055:c0ff:fea8:7b66%eth0  prefixlen 64  automatic
UP RUNNING SIMPLEX BROADCAST MULTICAST
MTU:1500  metric:1  VR:0  ifindex:2
RX packets:7 mcast:0 errors:0 dropped:0
TX packets:6 mcast:5 errors:0
collisions:0 unsupported proto:0
RX bytes:420  TX bytes:480

> cmd ifconfig gei0 inet6 add 2000::5 prefixlen 64 up
-> ipAttach 1,"gei"
value = 0 = 0x0
-> cmd ifconfig gei1 inet6 add 2111::5 prefixlen 64 up
-> cmd ifconfig -a
lo0	Link type:Local loopback
	inet 127.0.0.1  mask 255.255.255.255
	inet6 unicast fe80::1%lo0  prefixlen 64  automatic
	inet6 unicast ::1  prefixlen 128
	UP RUNNING LOOPBACK MULTICAST NOARP ALLMULTI
	MTU:1500  metric:1  VR:0  ifindex:1
	RX packets:228795 mcast:2853 errors:0 dropped:0
	TX packets:228795 mcast:2853 errors:0
	collisions:0 unsupported proto:0
	RX bytes:17386253 (17 M)  TX bytes:17386253 (17 M)

gei2	Link type:Ethernet  HWaddr 00:25:90:04:e2:de
	capabilities: TXCSUM TX6CSUM VLAN_MTU VLAN_TXHWTAG VLAN_RXHWTAG
	inet 128.224.166.238  mask 255.255.254.0  broadcast 128.224.167.255
	inet6 unicast fe80::225:90ff:fe04:e2de%gei2  prefixlen 64  automatic
	UP RUNNING SIMPLEX BROADCAST MULTICAST PROMISC ALLMULTI
	MTU:1500  metric:1  VR:0  ifindex:2
	RX packets:112433 mcast:8950 errors:0 dropped:4456
	TX packets:40068 mcast:1438 errors:0
	collisions:0 unsupported proto:0
	RX bytes:16911294 (16 M)  TX bytes:3574189 (3574 k)

gei0	Link type:Ethernet  HWaddr 00:15:17:c8:90:28
	capabilities: TXCSUM TX6CSUM VLAN_MTU VLAN_TXHWTAG VLAN_RXHWTAG
	inet6 unicast fe80::215:17ff:fec8:9028%gei0  prefixlen 64  tentative  automatic
	inet6 unicast 2000::5  prefixlen 64  tentative
	================================================

	    def _stop_proc(self, name, vr, cleanup, timeout): ---key is ---ipd kill
        vrx = IF(vr, '-V %s ' % vr, '')
        self.sh.send('%sipd %skill %s' % (self.las_prefix(), vrx, name))  ----xiaozhan
        if not cleanup:
            self.sh.expect_exact("ipd: kill %s ok" % name, timeout = timeout)  ---xiaozhan


            def _start_proc(self, name, vr, cleanup): ----key is--- ipd start
        vrx = IF(vr, '-V %s ' % vr, '')
        cmd = ''
        if len(self.las_prefix()) > 0:
            cmd += 'PATH=${PATH}:%s %s' % (self.las_prefix(), self.las_prefix())
        cmd += 'ipd %sstart %s' % (vrx, name)  ======xiaozhan
        self.sh.send(cmd)
        if not cleanup:
            self.sh.expect_exact('ipd: start %s ok' % name)   -----xiaozhan,


   def _add_netif(self, *a, **k):
        x = netif_ipnet(self)
        x.new(*a, **k)
        return x

   def add_netif(self, *a, **k):
       return self._add_netif(*a, **k)

    def reconfigure_proc(self, name, vr = 0):
        #if not self.opt['fast'] and
        if self._intern_proc_state(name,vr) == 'killed':
            raise engine_error('')
        self._reconfigure_proc(name,vr)

        def _intern_proc_state(self, name, vr):
        if not self.ts.procs:
            self._proc_state()
            self.ts.procs_copy = self.ts.procs.copy()
        return self.ts.procs.get((name,vr), 'killed')

            def _proc_state(self):
        self.ts.procs = self._get_running_procs()

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
================================================================
 metaclass=ABCMeta让你的类变成一个纯虚类,子类继承必须实现某个方法,这个方法用@abstractmethod修饰
iptestengine.py  中的class target()----解读代码
    def __init__(self, shops, ts):
        #no self.s exists at this point
        self.ts = ts      # xiaozhan ---this is used in every function to get state
        self.sh = shops   # xiaozhan---this is used in every command to get information
也就是说---self.ts的应用场景，如下例子---类似于调用函数
self.ts.default_route = self.get_route('default', exp_gw = True).get('gw')
ts---肯定是一个target的instance

sh也是一个target的instance---用法如下----直接发送命令
route = self.sh.send_and_return_all('ping')  ----通常用正则来判断返回值
==========================================
遇到问题---手动给配上IPV6地址---IPv4地址就无法ping通
但是手动telnet到qemu上，就能ping通
解决方案是 ping两次   理论上第一次找不到ARP，所以互通性应该没问题
ping6 -S 2002::5 -c 2 2001::5
cmd = 'ping -c 2 192.168.123.102'
==============================================
一行代码运行测试:进入工程目录
pytest -s test_cases/network_protocol/tftp/test_tftp.py::TestTFTP::test_tftp_no_server
解析qemu创建，bridge创建的代码:

    def start(self):  # xiaozhan, debug---self.build --build is Image class
        cmd = self.__createQemuCmd(self.build, self.ip, self.tapName)
        if self.debug:
            print(cmd)
        self.console = pexpect.spawn(cmd, timeout=self.timeout)  # xiaozhan
        if self.logFile is not None:
            self.console.logfile = self.logFile
        self.build.run(self.console)  # xiaozhan  debug, it is to check the console status after pexpect.spawn
  641      return ShellOperations(self.console, prompt='-> ')

 class QemuTarget()---里面的setup函数,必须要执行这个来给self.build 和self.bridge赋值--后者是从NetworkBuilder类中获取的
 self.build来自于  class VxWorksBuild(Build): -----即判断启动后状态

 然后才能执行里面的start函数-------是启动qemu
 在NetworkBuilder类里面的setup函数如下：---注意里面调用了QemuTarget类中的setup函数
     def setup(self):
        if not self.singleBoard:
            if self.bridge is None:
                self.__setupBridge()     # 实现了变量的赋值---self.bridge = createBridgeName(self.ips[0])
                self.outsideBridge = False
            else:
                self.outsideBridge = True
            for t in self.targets:
                print('\n')
                i = self.targets.index(t)     # 下面调用了target里面的setup函数
                self.tapNames.append(t.setup(self.builds[i], targetIp=self.ips[i], bridge=self.bridge))

 然后在  class NetworkBuilder(object):里面
     # xiaozhan, debug, remove below
     def start(self):
         consoles = []
         for t in self.targets:
             print('\n')
            i = self.targets.index(t)
             console = t.start()    这里调用了QemuTarget()类中的start方法来启动串口，也就是启动qemu
             consoles.append(console)
         return consoles
 如果没有创建bridge的需求---只需要创建完qemu实例，然后直接调用setup函数，再调用start函数就可以启动qemu
 但是目前的框架是创建完qemu实例后，再去创建bridge，然后启动了qemu实例的串口----又是关联的--
 也就是说---这部分框架没有解耦---但是不影响实际使用

 TODO   class VxWorksBuild(Build):  ======》class VxWorksImage(Image): ---修改成这样的名字  看着直观
 class Build(metaclass=ABCMeta):  # python 3.0 syntax ========class Image(abc.ABC):
 增加这部分  class LinuxImage(Image):

 修改builds和build的命名========》vximage = VxWorksImage
 lximage = LinuxImage()

 testEngine.py中修改所有的python2中的语法为python3---
 所有正在表达式前面都要添加r   ======= r'[\r\n\ ]'
 修改 all = self.s.before  =====  ret = self.s.bofore  因为all是python中的关键字，不要作为变量名存在
 修改target.py中的config文件位置--- self.configYaml = 'config/ezConfigTargetQEMUs.yaml'

 class QemuTarget(Target):里面的代码打印 ====
 从代码打印看，=======start to create====bridge====
go to network.start()
=======create vxworks qemu cmd is==========
 先创建bridge，然后再启动的qemu---即先调用setup函数，然后才是start函数

 考虑在 class QemuTarget(Target)里面实现出啊关键

        # xiaozhan, add below
        self.console = None
        self.bridge = None
        self.image = None
        self.ip = None
        self.hostIp = None
=======================================创建bridge===========
[xli3@pek-vx-29075 pytestAuto]$ echo $USER
xli3
sudo brctl addbr br-vm-123
sudo brctl sethello br-vm-123 10
sudo brctl setfd br-vm-123 0
=======start to create====vxworks bridge====
sudo tunctl -u $USER -t tap-QEMU-Q35-5
Set 'tap-QEMU-Q35-5' persistent and owned by uid 19044
sudo brctl addif br-vm-123 tap-QEMU-Q35-5
sudo ifconfig tap-QEMU-Q35-5 up

xiaozhan debug====== vxworks bridge cleanup====
sudo ip link set br-vm-123 down
sudo brctl delbr br-vm-123

=== quit target QEMU-Q35-2
use ctrl+c to quit target
sudo ifconfig tap-QEMU-Q35-2 down
sudo brctl delif br-vm-123 tap-QEMU-Q35-2
sudo tunctl -d  tap-QEMU-Q35-2
Set 'tap-QEMU-Q35-2' nonpersistent
================================================================================
在class NetworkBuilder(object)里面的函数---cleanup()删除bridge
def teardown_class(self):
    # tear down bridge
    self.netbdr.cleanup()

def cleanup(self):
    if not self.singleBoard:
        for t in self.targets:
            print('\n')
            t.cleanup()  -----这个调用了QemuTarget中的cleanup函数--用来退出串口，同时还有清bridge if not None
        print('\n')
        self.__cleanupBridge()  # 感觉这个函数应该放在前面执行  然后执行t.cleanup
    else:
        self.targets[0].cleanup()
QemuTarget类中的cleanup函数：
    def cleanup(self):
        if self.console is not None:
            if self.debug:
                print('=== quit target %s' % self.board)
            if not self.console.terminate(force=True):
                if self.debug:
                    print('use ctrl+c to quit target')
                self.console.sendcontrol('c')   # xiaozhan, debug
                self.console.expect(pexpect.EOF)

        if self.bridge is not None:   # xiaozhan  感觉这段不需要
            shellCmd('sudo ifconfig %s down' % self.tapName, debug=self.debug)
            shellCmd('sudo brctl delif %s %s' % (self.bridge, self.tapName), debug=self.debug)
            shellCmd('sudo tunctl -d  %s' % self.tapName, debug=self.debug)

==========下面两条逻辑主线===========================
NetWorkBuilder里面的setup函数调用QemuTarget中的setup函数---来创建tap
NetWorkBuilder里面的start函数调用QemuTarget中的start函数---来创建bridge，并启动串口
=========================================================

[xli3@pek-vx-29075 vxworks]$ ifconfig
br-vm-123: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.123.1  netmask 255.255.255.0  broadcast 192.168.123.255
        inet6 fe80::46:24ff:fe20:1f6  prefixlen 64  scopeid 0x20<link>
        ether 02:46:24:20:01:f6  txqueuelen 1000  (Ethernet)
        RX packets 38  bytes 2576 (2.5 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 50  bytes 5943 (5.9 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

eno1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 128.224.178.153  netmask 255.255.254.0  broadcast 128.224.179.255
        inet6 fe80::3eec:efff:fe22:bdba  prefixlen 64  scopeid 0x20<link>
        ether 3c:ec:ef:22:bd:ba  txqueuelen 1000  (Ethernet)
        RX packets 978527973  bytes 400890832122 (400.8 GB)
        RX errors 0  dropped 35382  overruns 0  frame 0
        TX packets 78657712  bytes 37776016416 (37.7 GB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        device interrupt 16  memory 0xdf100000-df120000

eno2: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.3.1  netmask 255.255.255.0  broadcast 192.168.3.255
        ether 3c:ec:ef:22:bd:bb  txqueuelen 1000  (Ethernet)
        RX packets 268860152  bytes 390566659716 (390.5 GB)
        RX errors 8  dropped 1  overruns 0  frame 8
        TX packets 16693927  bytes 1146431116 (1.1 GB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        device memory 0xdf000000-df07ffff

eno2:0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.10.1  netmask 255.255.255.0  broadcast 192.168.3.255
        ether 3c:ec:ef:22:bd:bb  txqueuelen 1000  (Ethernet)
        device memory 0xdf000000-df07ffff

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 8606152  bytes 9815122813 (9.8 GB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 8606152  bytes 9815122813 (9.8 GB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

tap-QEMU-LX-1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::5833:4ff:fe46:9221  prefixlen 64  scopeid 0x20<link>
        ether 5a:33:04:46:92:21  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 5  bytes 470 (470.0 B)
        TX errors 0  dropped 2 overruns 0  carrier 0  collisions 0

tap-QEMU-Q35-1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::46:24ff:fe20:1f6  prefixlen 64  scopeid 0x20<link>
        ether 02:46:24:20:01:f6  txqueuelen 1000  (Ethernet)
        RX packets 42  bytes 3486 (3.4 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 656  bytes 73797 (73.7 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

tap-QEMU-Q35-2: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::b029:80ff:fe59:d8f  prefixlen 64  scopeid 0x20<link>
        ether b2:29:80:59:0d:8f  txqueuelen 1000  (Ethernet)
        RX packets 44  bytes 3606 (3.6 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 423  bytes 45040 (45.0 KB)
        TX errors 0  dropped 2 overruns 0  carrier 0  collisions 0

tap-QEMU-Q35-3: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::6c91:f0ff:fed3:5ab0  prefixlen 64  scopeid 0x20<link>
        ether 6e:91:f0:d3:5a:b0  txqueuelen 1000  (Ethernet)
        RX packets 42  bytes 3486 (3.4 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 210  bytes 19380 (19.3 KB)
        TX errors 0  dropped 75 overruns 0  carrier 0  collisions 0

tap-QEMU-Q35-4: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::b8f4:42ff:febe:df12  prefixlen 64  scopeid 0x20<link>
        ether ba:f4:42:be:df:12  txqueuelen 1000  (Ethernet)
        RX packets 42  bytes 3486 (3.4 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 151  bytes 13912 (13.9 KB)
        TX errors 0  dropped 75 overruns 0  carrier 0  collisions 0

tap-QEMU-Q35-5: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::f8c5:abff:fed8:7b98  prefixlen 64  scopeid 0x20<link>
        ether fa:c5:ab:d8:7b:98  txqueuelen 1000  (Ethernet)
        RX packets 42  bytes 3486 (3.4 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 105  bytes 10027 (10.0 KB)
        TX errors 0  dropped 75 overruns 0  carrier 0  collisions 0

tap-QEMU-Q35-6: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::8c20:f2ff:fee0:d7dc  prefixlen 64  scopeid 0x20<link>
        ether 8e:20:f2:e0:d7:dc  txqueuelen 1000  (Ethernet)
        RX packets 26  bytes 2058 (2.0 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 44  bytes 4115 (4.1 KB)
        TX errors 0  dropped 79 overruns 0  carrier 0  collisions 0
[xli3@pek-vx-29075 vxworks]$ sudo brctl show
bridge name     bridge id               STP enabled     interfaces
br-vm-123               8000.1eb0d69225f4       no      tap-QEMU-LX-1
                                                        tap-QEMU-Q35-1
                                                        tap-QEMU-Q35-2
                                                        tap-QEMU-Q35-3
                                                        tap-QEMU-Q35-4
                                                        tap-QEMU-Q35-5
                                                        tap-QEMU-Q35-6

=======create qemu cmd is==========
sudo qemu-system-x86_64 -m 2048 -smp 4 -machine q35 -kernel /folk/xli3/tsn_trial/IA_Image/vxWorks-qemu/vxWorks -append "sysbootline:gei(0,0) e=192.168.123.107" -netdev tap,id=mynet107,ifname=tap-QEMU-Q35-6,script=no,downscript=no -device e1000,netdev=mynet107,mac=52:55:c0:a8:7b:6b --serial stdio -nographic -monitor none -enable-kvm
=============using config========== config/qemuTargetConfig.yaml
1 1 1


=======start to create====vxworks bridge====
go to linux network.start()
=======create qemu cmd is==========
sudo qemu-system-x86_64 -m 2048 -smp 4 -cpu host -boot order=d -hda /home/xli3/pytestAuto/config/focal-server-cloudimg-amd64.img -netdev tap,id=mynet108,ifname=tap-QEMU-LX-1,script=no,downscript=no -device e1000,netdev=mynet108,mac=52:55:c0:a8:7b:6c --serial stdio -nographic -monitor none -enable-kvm

Ubuntu 20.04.3 LTS ubuntu ttyS0

ubuntu login:
ubuntu login: ubuntu
Password:
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-99-generic x86_64)

ubuntu@ubuntu:~$ uname -a
Linux ubuntu 5.4.0-99-generic #112-Ubuntu SMP Thu Feb 3 13:50:55 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux
ubuntu@ubuntu:~$

buffer (last 100 chars): b'neric #112-Ubuntu SMP Thu Feb 3 13:50:55 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux\r\r\nubuntu@ubuntu:~$ '
E           before (last 100 chars): b'neric #112-Ubuntu SMP Thu Feb 3 13:50:55 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux\r\r\nubuntu@ubuntu:~$ '


    def expect(self, expect, timeout=20):   ====xiaozhan   debug    在target.py中添加打印 调试Linux
        if self.console is not None:
            log.debug('\n--- expect="%s" within %s seconds' % (expect, timeout))
            print('\n--- expect="%s" within %s seconds' % (expect, timeout))
            print('=====xiaozhan=====', self.console.before.decode('utf-8'))

    查看log ==
    [vxWorks]

--- expect="ubuntu@ubuntu:~$" within 20 seconds
=====xiaozhan===== sudo ip link set dev ens3 up   -----这里返回值不对

全部RTP----里面的交互命令全部换成C代码实现     获取现有实现的模块   TCP  UDP
KONG里面需要去掉IKE等安全测试     全改 RTP  case

VSOMEIP ----RTP模式  ---参考   交互模式全部改为RTP的实现方式 -----用C来实现


ubuntu@ubuntu:~$ sudo ip addr add 192.168.123.108/24 dev ens3
sudo ip addr add 192.168.123.108/24 dev ens3^M^M
ubuntu@ubuntu:~$ sudo ip link set dev ens3 up
sudo ip link set dev ens3 up^M^M

ubuntu@ubuntu:~$ sudo ip addr add 2000::2/64 dev ens3

ubuntu@ubuntu:~$ ip addr show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: ens3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 100
    link/ether 52:55:c0:a8:7b:6c brd ff:ff:ff:ff:ff:ff
    inet 192.168.123.108/24 scope global ens3
       valid_lft forever preferred_lft forever
    inet6 2000::2/64 scope global             -----xiaozhan
       valid_lft forever preferred_lft forever
    inet6 fe80::5055:c0ff:fea8:7b6c/64 scope link
       valid_lft forever preferred_lft forever



[xli3@pek-vx-29075 vxworks]$ sudo brctl show qemuBridge
bridge qemuBridge does not exist!

[xli3@pek-vx-29075 vxworks]$ sudo brctl show qemuBridge
bridge name     bridge id               STP enabled     interfaces
qemuBridge              8000.062e4849d832       no              tap-QEMU-LX-1
                                                        tap-QEMU-Q35-1
[xli3@pek-vx-29075 pytestAuto]$ pytest -s test_cases/network_protocol/tftp/test_eztarget.py::TestEZ::test_tftp_no_server
====================================== test session starts =======================================
platform linux -- Python 3.8.10, pytest-7.1.2, pluggy-1.0.0
rootdir: /home/xli3/pytestAuto
plugins: xdist-3.4.0, html-3.1.1, metadata-2.0.2, allure-pytest-2.10.0, rerunfailures-10.2
collected 1 item

test_cases/network_protocol/tftp/test_eztarget.py =============using config========== config/ezConfigTargetQEMUs.yaml
bridge name============ qemuBridge
-------xiaozhan bridge needs to create======
======debug  crate bridge======
NetworkBuilder add()
======ipv4 addr===== 192.168.123.80
NetworkBuilder add()

1. run command at QEMU-LX-1
======linux output is====== ['Linux ubuntu 5.4.0-99-generic #112-Ubuntu SMP Thu Feb 3 13:50:55 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux']

2. run command at QEMU-Q35-1
=======ifconfig content is=========
 ['lo0\tLink type:Local loopback', 'inet 127.0.0.1  mask 255.255.255.255', 'inet6 unicast fe80::1%lo0  prefixlen 64  automatic', 'inet6 unicast ::1  prefixlen 128', 'UP RUNNING LOOPBACK MULTICAST NOARP ALLMULTI', 'MTU:1500  metric:1  VR:0  ifindex:1', 'RX packets:22 mcast:0 errors:0 dropped:0', 'TX packets:22 mcast:0 errors:0', 'collisions:0 unsupported proto:0', 'RX bytes:960  TX bytes:960', '', 'eth0\tLink type:Ethernet  HWaddr 00:40:47:a8:7b:0a', 'capabilities: VLAN_MTU VLAN_TXHWTAG VLAN_RXHWTAG', 'inet 192.168.123.10  mask 255.255.255.0  broadcast 192.168.123.255', 'inet6 unicast 2000::3  prefixlen 64  tentative', 'inet6 unicast fe80::240:47ff:fea8:7b0a%eth0  prefixlen 64  tentative  automatic', 'UP RUNNING SIMPLEX BROADCAST MULTICAST', 'MTU:1500  metric:1  VR:0  ifindex:2', 'RX packets:0 mcast:0 errors:0 dropped:0', 'TX packets:6 mcast:5 errors:0', 'collisions:0 unsupported proto:0', 'RX bytes:0  TX bytes:468']

3. ping Linux from vxworks at QEMU-Q35-1
=======ping content is=========
 ['Pinging 192.168.123.80 (192.168.123.80) with 64 bytes of data:', 'Reply from 192.168.123.80 bytes=64 ttl=64 seq=0 time=1500ms', 'Reply from 192.168.123.80 bytes=64 ttl=64 seq=1 time=500ms', '', '--- 192.168.123.80 ping statistics ---', '2 packets transmitted, 2 received, 0% packet loss, time 1500 ms', 'rtt min/avg/max = 500/1000/1500 ms']

4. ping Linux from vxworks QEMU-Q35-1
=======ping6 content is=========
 ['Pinging 2000::2 (2000::2) with 64 bytes of data:', 'Reply from 2000::2 bytes=64 hlim=64 seq=0 time=0ms', 'Reply from 2000::2 bytes=64 hlim=64 seq=1 time=16ms', '', '--- 2000::2 ping statistics ---', '2 packets transmitted, 2 received, 0% packet loss, time 1017 ms', 'rtt min/avg/max = 0/8/16 ms']

5. Linux show QEMU-LX-1
=======Linux show IP=========
 ['1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000', 'link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00', 'inet 127.0.0.1/8 scope host lo', 'valid_lft forever preferred_lft forever', 'inet6 ::1/128 scope host', 'valid_lft forever preferred_lft forever', '2: ens3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000', 'link/ether 00:40:47:a8:7b:50 brd ff:ff:ff:ff:ff:ff', 'inet 192.168.123.80/24 scope global ens3', 'valid_lft forever preferred_lft forever', 'inet6 2000::2/64 scope global', 'valid_lft forever preferred_lft forever', 'inet6 fe80::240:47ff:fea8:7b50/64 scope link', 'valid_lft forever preferred_lft forever']
.

======================================= 1 passed in 46.24s =======================================
[xli3@pek-vx-29075 pytestAuto]$
用下面的code来调试-----接下来需要解决log的存储问题---如果没有allure，target上的操作如何保存
目前已经能实现vxworks和linux的组网---还需研究组网部分的代码---涉及到单例模式
[xli3@pek-vx-29075 pytestAuto]$ pytest -s test_cases/network_protocol/tftp/test_eztarget.py::TestEZ::test_tftp_no_server
============================================debug code===


 def sendAndExpect(self, cmd, expect, timeout=20):
        if self.console is not None:
            logger.debug('\n--- send="%s" and expect="%s" within %s seconds' % (cmd, expect, timeout))
>           self.console.sendline(cmd)
E           AttributeError: 'shell_ops' object has no attribute 'sendline'
分析上面的错误
    def boot(self, image): ------在QemuTarget里面调用这个函数来启动板子--里面返回一个串口供操作命令
        # logger.info('boot the target %s with %s' % (self.board, image.getBin()))
        print('xiaozhan=======boot the target %s with %s' % (self.board, image.getBin()))
        if self.netBuilder is None:
            # use singleton NetworkBuilder
            self.netBuilder = NetworkBuilder()
            self.console = self.netBuilder.add(self, image, self.ip) ---check这个函数
        return self.console    # xiaozhan, check this console
 check下面的add函数实现 --查看返回的console属性---
    def add(self, target, image, targetIp):
        print('NetworkBuilder add()')
        assert isinstance(targetIp, ip)

        NetworkBuilder.targets.append(target)
        NetworkBuilder.builds.append(image)
        NetworkBuilder.ips.append(targetIp)

        target.setup(image, targetIp=targetIp, bridge=self.bridge) ----创建tap接口，添加到bridge上面
        shellOps = target.start()        -----check这个函数实现----检查这个的属性shellOps

        netId = targetIp.get_networkid_str()
        shCmd('sudo ifconfig %s inet %s up' % (NetworkBuilder.bridge, netId))

        NetworkBuilder.consoles.append(shellOps)
        return shellOps
==如果用上一套代码，即target.py---test_tftp.py, boot_qemu.py----需要解决Linux上的串口问题
即输入命令行 没有匹配成功

====如果用当前代码---ezTargets.py----test_eztarget.py---boot_qemu_ez.py -----需要解决串口自动存储log问题
当前log没有写入，原因正在调查 -----在class Qemu(Target)类里面的start函数添加一行代码：
    def start(self):
        logger.debug(f'start the target {self.board}')
        cmd = self.__createQemuCmd(self.image, self.ip, self.tapName)
        # logger.info(cmd)
        print(f'=======start cmd for qemu target{self.board} =======', cmd)

        if isinstance(self.image, LinuxImage):
            self.timeout = 180

        self.console = pexpect.spawn(cmd, timeout=self.timeout)   ====这个才是每个板子的类似于telnet的串口session
        self.image.run(self.console)
        # xiaozhan add  ======================================添加这个，每个串口log自动保存到文件里
        if self.logFile is not None:
            self.console.logfile = self.logFile


register command shell======
'tftp -a noserver.interpeak.se get no_server.txt'


  child = pexpect.spawn(bootCmd, timeout=240, preexec_fn=preexecSpawn, encoding='utf-8')
318         child.expect('ubuntu login: ')
319         child.sendline('ubuntu')
320         child.expect('Password: ')
321         child.sendline('ubuntu')
322         linuxPrompt = 'ubuntu@ubuntu:~\$ '     ------原来我用的是 'ubuntu@ubuntu:~$ '  没有那个\来转移特殊字符$ --造成一直匹配失败

=====================================================================
验证8021x，先手动跑KONG的case--检查log---再对比和qemu上的差别
目前qemu上运行失败---
=================================================
def test(self, log, hosts, v6, __):
解决上面这种IPV4和IPv6都执行的case---用传参数的方式来解决--这样只需要写一个case，但是执行两次即可---
写一个装饰器或者直接参数化list来传参

@pytest.mark.parametrize('version', ['v4', 'v6'])
def test_ipnet_bond_configure(self, version):
    a = self.t1
    if version == 'v6':
        ret = '\n'.join(a.sendAndReturnAll('sysvar set -co ip8021x.if_name "simtest-eth0-loopback"', self.vxprompt))
        print(f'====ret is ===== {ret}')
        assert 'ok' in ret
    else:
        assert True
=====================================
每个KONG的case里面执行完毕都会清楚配置   ---这样不需要频繁重启qemu
pytest -s test_cases/network_protocol/bond/test_bond.py::TestBond::test_ipnet_bond_configure

--networks 3     表示三个网段？---BOND的case需要起多个网段--还不知道咋弄
=================================================================
self.ptnTestSuite = '(?s)TEST-CASE-\d+\n(.*?)\*\*\* TESTS COMPLETE\n'

    def parse(self, parentTestName=None):
        rets = []
        testSuites = self.__parseTestSuite(self.content)

        for testSuite in testSuites:
            print testSuite
            for theLine in testSuite.split('\n'):
                if self.isTestCase(theLine):
                    testResult, testName = self.__parseTestCase(theLine)
                    rets.append((self.createTestName(testName, parentTestName), testResult.strip()))
        return rets

    def __parseTestSuite(self, content):
        return re.findall(self.ptnTestSuite, content)

stp = SockTestParser('\n'.join(ret))
    print '-'*22
    testResults = stp.parse(parentTestName=parentTestName)   # 返回一个元组列表，例如[(case1,pass),(case2,fail)]


parentTestName ----就是类似于socktest.udp.c0030connect
def createTestName(self, theStr, parentTestName=None):
   PASS: connect invalid descriptor returned -1/EBADF ---
上面的函数就是把上面的内容转成下划线连接的字符 connect_invalid_descriptor
然后再拼接成 socktest.udp.c0030connect.connect_invalid_descriptor
===============================================================
KONG image--vsb and vip===
http://pek-kong-01.wrs.com:8080/view/pek-sec-kong-02/job/new-ci-build-slave/22292/consoleFull


C socktestServerStart
=====xiaozhan======ret==== C socktestServerStart
value = 0 = 0x0
[vxWorks]
value = 0 = 0x0
[vxWorks]
tcp socket IPv4 test
===  C socktest "192.168.123.30/24", 2, 1, 0

===================================================

sudo qemu-system-x86_64 -m 2048 -smp 4 -machine q35 -kernel /folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-socktest/vxWorks -append "sysbootline:gei(0,0) e=192.168.123.20" -netdev tap,id=mynet20,ifname=tap-QEMU-Q35-2,script=no,downscript=no -device e1000,netdev=mynet20,mac=00:40:47:a8:7b:14 --serial stdio -nographic -monitor none -enable-kvm

sudo qemu-system-x86_64 -m 2048 -smp 4 -machine q35 -kernel /folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-crypto/vxWorks -append "sysbootline:gei(0,0) e=192.168.123.30" -netdev tap,id=mynet30,ifname=tap-QEMU-Q35-3,script=no,downscript=no -device e1000,netdev=mynet30,mac=00:40:47:a8:7b:1e --serial stdio -nographic -monitor none -enable-kvm

C socktest "192.168.123.30/24", 2, 1, 0

C socktest "192.168.123.30/24", 1, 2, 0


C sock6testServerStart

C sock6test "2000::4/64", 1, 3, 0

C socktest "192.168.123.30/24", 2, 4, 0     accept
C socktest "192.168.123.30/24", 2, 3, 0     connect

pytest -s test_cases/network_protocol/socktest   -----This can store complete test log under pytestAuto directory----test.log and qemu1.log, socktest.log

socktest.log ---- this will only write when running pytest -s in the terminal but not Jenkins

if you are using Jenkins, you can only see test.log  --------------------------

if logFile is not None:       class Target里面定义了串口log的搜集
    if type(logFile) == str:
        self.logFile = open(logFile, 'w')   # xiaozhan,
self.console = pexpect.spawn(cmd, timeout=self.timeout, encoding='utf-8')    搜索这行代码  在 def start()函数里面
注意：如果下面没有encoding='utf-8'   上面就需要用'wb'模式
==================================================
如何去掉log里面的特殊字符？应该是跟编码有关
TEST-CASE-3^M^M
PASS: connect invalid descriptor returned -1/EBADF^M^M
PASS: tcp connect null sockaddr returned -1/EINVAL^M^M
PASS: tcp connect sockaddr wrong length retu

pytest -s test_cases/network_protocol/socktest/test_socktest.py::TestSocktest::test_socktest_tcp_c0010socket 2>&1 | tee xiaozhan.log

pytest -s test_cases/network_protocol/socktest  2>&1 | tee xiaozhan.log
cat xiaozhan.log

[('socktest.tcp.c0010socket.socket_invalid_domain-IPv6', 'PASS'), ('socktest.tcp.c0010socket.socket_unspecified_domain-IPv6', 'PASS'), ('socktest.tcp.c0010socket.socket_invalid_type-IPv6', 'PASS'), ('socktest.tcp.c0010socket.socket_type_proto_disagreement-IPv6', 'PASS'), ('socktest.tcp.c0010socket.socket_SOCK_STREAM_0-IPv6', 'PASS'), ('socktest.tcp.c0010socket.socket_SOCK_STREAM_IPPROTO_TCP-IPv6', 'PASS')]

cd /home/ubuntu/jenkins/workspace/jobname/casename/cvs/iptestengine/src/log
4. log就在上述路径下
=====================================================================================
firewall 的代码解读  util.py
n = layout_net('rcs' + v6, hosts)   # 组网 是必须的步骤 -----这部分是核心代码
# create shells
n.sshell = n.s.ipcom_shell()     # 这两部分创建shell可能需要自己调整，看是否能直接省去ipcom_shell这一层函数调用
n.cshell = n.c.ipcom_shell()

xiaozhan--- hosts参数就是我之前创建好的6个qemu和一个Linux---也就是对应着 self.t1, self.t2, self.t3, self.t4, self.t5, self.t6 = self.vx_targets
layout_net函数里面的调用=====先针对rcs组网进行分析
elif layout == 'rcs':
    return rcs(hosts, '')
    跳转到  def rcs(hosts, v6):
               return n     ---返回一个n 类似于
    n = _nat() =====n来自于下面这个类实例
    class _nat:
        pass
    n = _nat()
    r, s, c = hosts   =======这里先定义3个target
    n.r, n.s, n.c = r,s,c     # router, server, client
    n.cif = cif           #client netif
    n.sif = sif
    n.cnet = cnet         #10.lucky_number.client_net(cnet).ip
    n.snet = snet
    n.rifc = rifc         #router netif facing client
    n.rifs = rifs
    n.ripc = ripc         #router ip on netif facing client
    n.rips = rips

iptestengine.py里面：
class netif(object):
class netif_iptarget(netif):

class target(object):
class iptarget(target):
class ipcom_shell(iptarget):
class ipnet(iptarget):

=============================================
iptestengine.py---- class _log(object):  存储log的代码

global es
es = engine_state()

logfile = open(config.logpath + os.path.sep + 'test.log' + '_' + localtime_str(), 'w')
if not logverbose:
    logverbose = logfile
runlog = _log(logfile, o.verbose)

# Setup the network.
targets = login_to_n_targets(runlog,
                             logverbose,
                             opt,
                             max(test.hosts, hosts_per_net_layout.get(test.net_layout, 1)),
                             filter_hosts)
runlog('Skipping test %s since it requires ipv%s on target which are not available' % (test.prodname + '.' + test.modname + '.' + test.testname + ' ' + ipv, ipv if ipv == '6' else 4), echo = True)

xiaozhan=== 下面的ts和shops是否还需要？
class target(object):
    '''Base class for all test targets. Make no direct instances of this class.
    Only one instance per target is allowed. The proxy will be used for multiple
    logins to the same target.'''
    #__metaclass__ = trace_metaclass

    def __init__(self, shops, ts):
        #no self.s exists at this point
        self.ts = ts
        self.sh = shops
# shell operations
class shell_ops(object):
    def __init__(self, session):
        self.s = session

class session(object):
    def __init__(self, log=None, logverbose=None, addr=None, port=None, user=None, passwd=None, name=None, native = False, dry=None, relogin = False, target_access=None, target_prefix = None, timeout = 30): #interactive=False
        self.relogin = relogin
        self.login_ip = ip('%s/24' % addr)   # ip is a class
================================================================================
cif = c.add_vlan()
cnet = 1
c.ts.primary_ip = cif.add_ip("%s%s.1/%s" % (ab, cnet, pfx))
c.ts.primary_ip6 = c.ts.primary_ip

def _add_netif(self, *a, **k):
    x = netif_ipnet(self)
    x.new(*a, **k)
    return x    # renturn is a class instance

class target_state(object):    # xiaozhan, it is self.ts
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

ts = target_state()   # self.ts

class target(object):
    '''Base class for all test targets. Make no direct instances of this class.
    Only one instance per target is allowed. The proxy will be used for multiple
    logins to the same target.'''
    #__metaclass__ = trace_metaclass

    def __init__(self, shops, ts):
        #no self.s exists at this point
        self.ts = ts
        self.sh = shops

class shell_ops(object):
    def __init__(self, session):
        self.s = session

shops = shell_ops(s)
==========================================================

def layout_net(layout, hosts, v6=''):
    def rcs(hosts, v6):

n = layout_net('rcs' + v6, hosts)
===============================================================================
Run KONG case on pek-sec-kong-02
/home/xli3/vxworks/vxworks/relx/source/os/net/ipnet/coreip/src/ipcom/util/scripts


ssh to pek-sec-kong-02 with xli3:
cd /workspace/svc-cmnet/CISPIN/vx20240224000223_vx_2409/vxworks/relx/source/os/net/ipnet/coreip/src/ipcom/util/scripts
cp runKong.sh /workspace/xli3
sudo chmod -R 777 xli3
./runKong.sh -m FIREWALL -g /workspace/svc-cmnet/CISPIN/vx20240224000223_vx_2409 -c ipfirewall.ipfilter.syntax buildTest
=================================================================================================
./iptestengine.py -t ipfirewall.ipfilter.syntax

[2024-02-29 11:37:34] Debug: Checking connectivity to all targets
[2024-02-29 11:37:34] Info: Target at address 192.168.199.2 is running
[2024-02-29 11:37:34] Info: Target at address 192.168.199.3 is running
[2024-02-29 11:37:34] Info: Target at address 192.168.199.4 is running
[2024-02-29 11:37:34] Info: Target at address 192.168.199.5 is running
[2024-02-29 11:37:34] Info: Target at address 192.168.199.6 is running
[2024-02-29 11:37:34] Info: Target at address 192.168.199.7 is running
[2024-02-29 11:37:34] Info: Target at address 192.168.199.8 is running
[2024-02-29 11:37:34] Info: Target at address 192.168.199.9 is running
[2024-02-29 11:37:34] Info: Target at address 192.168.199.10 is running
[2024-02-29 11:37:34] Info: 1/1: Test setup: groups = {'default': (vxsim0,vxsim1,vxsim2,vxsim3,vxsim4,vxsim5,uml8,uml9,uml10)
=== current dir:/workspace/xli3/FIREWALL/cvs/iptestengine/src
=== ./iptestengine.py -t ipfirewall.ipfilter.syntax
=======================================================================
Firewall 模块设计很多代码，设计架构的改动，需要特殊对待---可以考虑后期把创建vlan等步骤提取出来，单独写class来实现，继续用一个class Target类，然后基于这个类单独写测试模块来支持一系列API，例如创建vlan，添加IP
每个都需要做封装----   此特例只针对firewall，预计其他模块不需要特别复杂的API，只需要提供交互接口即可覆盖大部分场景
==========================================================================================================

WARNING -add failed _WRS_CONFIG_IPNET_IPCRYPTO=y is not enabled in VSB

CRYPTO的测试得去掉最后一个 no-test
WRS_CONFIG_OPENSSL_OPTIONS="no-aria no-blake2 no-camellia no-chacha no-md2 no-ocb no-poly1305 no-rc2 no-scrypt no-seed no-siphash no-sm2 no-sm3 no-sm4 no-cms no-cmp no-err no-autoerrinit no-filenames no-ct no-ec2m no-multiblock no-rfc3779 no-srp no-tests"

vxprj vsb config -s -add _WRS_CONFIG_OPENSSL_OPTIONS="no-aria no-blake2 no-camellia no-chacha no-cmac"

@pytest.fixture(params=['参数1', '参数2'])
def my_fixture(request):
    return request.param

===========================================================测试log的搜集===打算采用下面的方案---所有操作都会存储在test.log文件===
from utils.log_record import log
log.debug(f'run on target {self.t1.board}\nexptest')
ret = '\n'.join(target.sendAndReturnAll('exptest', self.vxprompt))
log.debug(f'return value on {self.t1.board}\n{ret}')

=======================================================

['-----BEGIN PRIVATE KEY-----', 'MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAK0UymzfZnJsNykX', '0B6eb2DkrkVdUcYEjrBJbyN94/On9oFpZw2Jg+EqEjWBX9S9SOvJsvSFxIKfcj6v', 'dBgMJ4DIG8508lKOx3CUJj2x+xH++wov45P5zKIGFwQT9qXn7P+dOdYwFH8lSaMh', 'QBTFg2Qe13r26heCY36eXvMmypZHAgMBAAECgYAadmdMpgtfyzPT0JQ9WjPlOJF8', 'gXwTLncydMfNQV4szq1ds+PRqgjD0E7gZ1tjh10yz6/QuvMElaQ9+U1ir9kKEyRY', 'mEBz+K7oU8g8TUz6lFsNyhL2h/CZSocIw8ZGf1uuIHwjtz38jbO7RrldxDh/pX00', '1p2DyoQVZ1PMJBmdYQJBANqxZVsKFySI9PnDiSfay6KF7FL8+lcRrLCfaWESzrQd', 'sSkmn1xqeIbXkH8+jFLUawiqAWeaDdHZsznL1oe1niMCQQDKm3ieoepycsf6Broe', '/grZZqb7B33d0lRl6ZIK56qATHVIlYIpKIya9rKbwXGeKTPMXuDILOxb0kDUpw20', 'Ft+NAkAbrukNpTFYxp18IGx0RxYP9LP9rVhjPTGHCibkyuSvmDKc6u6xXCj1qMP5', '14kb0xfZeOvEmZO2RMCTSGJXu33RAkA4wPA6z3RS9uAZo4TDZbo4R88Choi1eFN3', '8MOeFmLmaYR4/phlWxx31B8YDkn7WeNOnk0tBZh36B+M8faeucGJAkEAh/KHc0P1', 'N6KprVUdoXq7ZhlXGb+SCvmbQ5hzcgqmiC9sB5W9GxWghf8m3gvQ+CniHLadgQvG', 'tCm4GRtND0seyg==', '-----END PRIVATE KEY-----']

cd /ram   添加这个才能生产下面的文件   不知道KONG里面的simulator是在什么目录
target.sendAndExpect('cd /ram', self.vxprompt)
genrsa -out rsa_key.pem -aes128 1024
buffer (last 100 chars): b' rsa_key.pem -aes128 1024\r\r\ngenrsa: Can\'t open "rsa_key.pem" for writing, errno = 0x13\r\r\n[vxWorks]# '

sudo qemu-system-x86_64 -m 2048 -smp 4 -machine q35 -kernel /folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-crypto/vxWorks -append "sysbootline:gei(0,0) e=192.168.123.60" -netdev tap,id=mynet60,ifname=tap-QEMU-Q35-6,script=no,downscript=no -device e1000,netdev=mynet60,mac=00:40:47:a8:7b:3c --serial stdio -nographic -monitor none -enable-kvm

[vxWorks]# dsaparam -out dsaparam.pem 1024
Can't open "dsaparam.pem" for writing, errno = 0x13
E0A7B4000080FFFF:error:80000013:lib(2):BIO_new_file:reason(19)::0:calling fopen(dsaparam.pem, w)
E0A7B4000080FFFF:error:10080002:lib(32):BIO_new_file:reason(524290)::0:
[vxWorks]# cd /ram
[vxWorks]# dsaparam -out dsaparam.pem 1024
==================================================================================
self.console = pexpect.spawn(cmd, timeout=self.timeout)
这个self.console调用了pexpect里面的函数--所以自带了pexpect提供的sendline和expect方法
self.console.sendline(cmd)
self.console.expect(expect, timeout=timeout)

代码里面的send  expect  看情况调整，下面是一个经典的例子
send命令后--expect可以有多个匹配值--甚至里面可以是列表，只要能匹配列表其中一个元素或者多个就可以
如果需要对send后的返回值进一步分析--需要用sendAndReturnAll来获取除了self.vxprompt之外的所有信息，然后分析
如果send之后  没有输出，例如下面的rm语句--则直接用sendAndExpect
[vxWorks]# rm rsa_key.pem
[vxWorks]#


target.send("Goofy")
target.expect("modulus:")
target.expect("publicExponent:")
target.expect("privateExponent:")
target.expect("prime1:")
target.expect("prime2:")
target.expect("exponent1:")
target.expect("exponent2:")
target.expect("coefficient:")
target.expect(["-----BEGIN RSA PRIVATE KEY-----",
               "-----BEGIN PRIVATE KEY-----"])
target.expect(["-----END RSA PRIVATE KEY-----",
               "-----END PRIVATE KEY-----"])
target.expect(self.vxprompt)

结论---原来的send和expect的代码结构可以直接复用--这样改动量最少
target.wait_prompt() ---修改为 target.expect(self.vxprompt)
===========================================================================
下面5条语句可以匹配下面的命令输出
target.expect("[pP]:")     ----中括号里面是正则匹配
target.expect("[qQ]:")
target.expect("[gG]:")
target.expect("-----BEGIN DSA PARAMETERS-----")
target.expect("-----END DSA PARAMETERS-----")

[vxWorks]# dsaparam -in dsaparam.pem -text
DSA-Parameters: (1024 bit)
P:
    00:ae:fa:6d:a5:d6:dc:72:7f:fa:65:0e:c1:2d:3f:
    49:20:97:d1:3d:9a:03:e5:1c:a7:5a:fe:64:49:2c:
    f0:9e:f3:0d:10:4d:43:79:79:21:d8:04:d8:83:7d:
    11:4f:02:44:e1:b8:52:d6:1d:35:f1:d2:5a:ed:70:
    e1:f9:eb:2a:7b:29:3d:ae:e5:f0:12:0d:a1:ea:8a:
    d8:b3:06:21:9a:fc:dc:60:7d:5d:b9:19:6b:d0:da:
    4f:f5:fd:84:03:05:09:52:13:f2:c0:29:82:13:6c:
    01:a0:f6:a5:05:aa:f9:3f:fe:2d:d6:0a:88:dc:b1:
    82:75:66:1e:f1:3f:e7:0b:bf
Q:
    00:86:06:34:fa:81:68:10:3f:0f:87:96:e1:a0:c4:
    1c:8b:79:9d:7d:80:6e:6e:c2:2a:87:6b:99:91
G:
    07:b2:9f:1b:61:81:43:02:ab:e7:e0:89:c4:b6:0f:
    11:c7:d0:b6:97:46:9f:aa:11:49:86:76:a1:d0:5e:
    ec:ee:e4:15:9b:de:53:48:96:6f:11:b6:b5:07:c1:
    cf:d8:bd:78:c5:cc:83:00:8d:8f:ea:4e:62:da:26:
    b0:b0:e9:2f:af:aa:77:97:70:77:ad:dd:49:75:87:
    7d:8b:a3:4b:88:5b:4a:97:2d:b1:4c:b6:91:c2:d7:
    1d:3b:78:62:e4:62:57:d9:bf:12:9d:03:26:b2:8c:
    fc:14:16:95:73:42:be:ad:96:5c:7a:89:1f:64:c6:
    b9:f4:a5:75:dc:2a:69:65
-----BEGIN DSA PARAMETERS-----
MIIBJgKBgQCu+m2l1txyf/plDsEtP0kgl9E9mgPlHKda/mRJLPCe8w0QTUN5eSHY
BNiDfRFPAkThuFLWHTXx0lrtcOH56yp7KT2u5fASDaHqitizBiGa/NxgfV25GWvQ
2k/1/YQDBQlSE/LAKYITbAGg9qUFqvk//i3WCojcsYJ1Zh7xP+cLvwIdAIYGNPqB
aBA/D4eW4aDEHIt5nX2Abm7CKodrmZECgYAHsp8bYYFDAqvn4InEtg8Rx9C2l0af
qhFJhnah0F7s7uQVm95TSJZvEba1B8HP2L14xcyDAI2P6k5i2iawsOkvr6p3l3B3
rd1JdYd9i6NLiFtKly2xTLaRwtcdO3hi5GJX2b8SnQMmsoz8FBaVc0K+rZZceokf
ZMa59KV13CppZQ==
-----END DSA PARAMETERS-----
===============================================================================
转义 pattern 中的特殊字符。如果您想匹配其中可能包含正则表达式元字符的任意文字字符串，这很有用。例如：

>>> print(re.escape('https://www.python.org'))
https://www\.python\.org

target.expect ----里面的列表元素必须是精确匹配--例如实际有空格，就带着空格--例如 DH Parameters: (1024 bit)前面就带了4个空格或者----4个横杠
# target.expect(["Diffie-Hellman-Parameters: (1024 bit)",
#                "DH Parameters: (1024 bit)"], timeout=90)   # xiaozhan, add timeout=40

[vxWorks]# speed          ------test_speed_cmd
Doing mdc2 for 3s on 16 size blocks: To get meaningful results, run this program on idle system.

0xffffffff80510fbe vxTaskEntry  +0x3e : 0xffffffff808bf1b8 ()
0xffffffff808bf476 shellTask    +0x586: 0xffffffff808c1d20 ()
0xffffffff808c1f62 shellExec    +0x762: 0xffffffff808b8aa3 ()
0xffffffff808b8e8c shellInterpCmdInit+0x99c: shellCmdExec ()
0xffffffff808bb7ec shellCmdExec +0x34c: 0xffffffff804fb196 ()
0xffffffff804fb57f speed_main   +0x16ff: 0xffffffff8050bc84 ()

Shell task 'tShell0' restarted...

[vxWorks]#
Warning: signal 14 caught by the shell.
=======================================================

192.168.199.2>ifconfig eth0 inet add 10.247.1.1/24
192.168.199.2_XunXiqX

192.168.199.2>fips_ctrl mode show
Cmd: 'fips_ctrl' not found

192.168.199.2>.
192.168.199.2_XunXiqX

192.168.199.2>evp_test evptests.txt
Subtest: run_file_tests
INFO:  @ ../test/testutil/stanza.c:21
Reading evptests.txt
ERROR: (ptr) 'equals = strchr(s->buff, '=') != NULL' failed @ ../test/testutil/stanza.c:109
0x0
INFO:  @ ../test/testutil/stanza.c:110
Missing = at line 5

INFO:  @ ../test/testutil/stanza.c:33
Completed 0 tests with 1 errors and 0 skipped
INFO:  @ ../test/evp_test.c:4209
evp_test                       failed
192.168.199.2_XunXiqX

ipcrypto.ipcrypto_test.evptest Test Passed ----------------------------------------
OK 0s


mkdir romfs
cp  -rf /home/xli3/demo/config_dev/case1_1000stream.json romfs/

evp_test /romfs/evptests.txt
[vxWorks]# cd /romfs
[vxWorks]# evp_test /romfs/evptests.txt
Subtest: run_file_tests
INFO:  @ ../test/testutil/stanza.c:21
Reading /romfs/evptests.txt
ERROR: (ptr) 'equals = strchr(s->buff, '=') != NULL' failed @ ../test/testutil/stanza.c:109
0x0
INFO:  @ ../test/testutil/stanza.c:110
Missing = at line 5

INFO:  @ ../test/testutil/stanza.c:33
Completed 0 tests with 1 errors and 0 skipped
INFO:  @ ../test/evp_test.c:4209
evp_test                       failed
[vxWorks]#
===============================================================
如果出现下面这种连续的expect语句--最后一句最好是判断prompt的语句
target.send("dhparam 1024")
target.expect("Generating DH parameters, 1024 bit long safe prime")
target.expect("-----BEGIN DH PARAMETERS-----")
target.expect("-----END DH PARAMETERS-----")
target.expect(self.vxprompt)
=================================================================

target.send("keydb import key kalle /romfs/dsa_1024.pem")
target.expect("Failed: already installed")
target.expect(self.vxprompt)

上面三行代码表示send完后---希望输出Failed:already installed,然后接下来出现self.vxprompt
上面三行代码也可以用
ret = target.sendAndReturnAll("keydb import key kalle /romfs/dsa_1024.pem", self.vxpromt)  # xiaozhan, return a list
log.debug(f'return value on {target.board}\n{ret}')
if 'Failed: already installed' in ret:  # 判断返回值里面是否出现想要的结果
==================================================================
调整log的打印和搜集---默认是info--在log_record.py里面设置--debug级别最低--只有需要时候才设置成debug
log = Logger(log_name, level='info').logger

log.info(f'run on target {target.board}\ncmactest')
ret = target.sendAndReturnAll('cmactest', self.vxprompt)[-2]
log.debug(f'return value on {target.board}\n{ret}')

ipcrypto.ipcrypto_test.bntest-IPv4
@pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
@pytest.mark.parametrize('year, version', [('123', 'IPv4'), ('345', 'IPv6')])
@pytest.mark.parametrize('version', ['IPv4'])  ---即使只有一个参数，也要用列表
===========================================================
尝试统计测试结果的插件     pytest-json-report   没有弄出来  暂时放弃
cd /home/xli3/pytestAuto
python3 test_cases/network_protocol/crypto/test_crypto.py

Traceback (most recent call last):
  File "test_cases/network_protocol/crypto/test_crypto.py", line 583, in <module>
    summary = plugin.report.get('summary')    # this is a dictionary
AttributeError: 'NoneType' object has no attribute 'ge
=====================================================================================
check below code to remove special characters  例如那些^M符号

    def sendAndReturnAll(self, cmd, expect, timeout=120):
        """return the lines not empty, each line gets stripped"""
        if self.console is not None:
            # logger.debug('\n--- send="%s" and expect="%s" within %s seconds' % (cmd, expect, timeout))
            log.info('--- send=%s' % cmd)
            log.debug('--- expect=%s' % expect)
            self.console.sendline(cmd)
            self.console.expect(expect, timeout=timeout)
            # lines = self.console.before.split(b'\n')

            ret = self.console.before.decode("utf-8")   # xiaozhan, debug
            # ret = self.console.before  # xiaozhan, add
            # Remove control codes, see http://dickey.his.com/xterm/xterm.faq.html  # xiaozhan, below operations are key points to remove special characters
            ret = ret.replace('\r\n\r\x00', '')
            ret = ret.replace(' \x08', '')
            ret = ret.replace('^[[A', '')
            ret = ret.replace('^[[K', '')
            lines = ret.split('\r\n')
========================================================================================================

# target.expect("Public-Key: (1024 bit)")     这种我当前的code还没做到精确匹配，所以用下面的模糊匹配---可能是因为里面含有小括号等特殊字符，需要正则表达式-暂时不研究
  target.expect("Public-Key:")
  =====================================================================================
# try to set clock for 15 minutes then exit
    s.send('ntpd -q -c ~/ntp/' + file)
    s.wait_prompt(timeout = (15*60))
    s.send('ntpd -c ~/ntp/' + file)
    s.wait_prompt(timeout = 60)
    s.send('ps aux')
    s.expect_exact_and_wait_prompt('ntpd')

  ntpd -q -c ~/ntp/ ntp.server.unicast.conf

  [xli3@pek-vx-29075 vxworks]$ ftp 128.224.166.46
Connected to 128.224.166.46.
220 (vsFTPd 3.0.2)
Name (128.224.166.46:xli3): root
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> pwd
257 "/"
ftp> ls
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
-rw-r--r--    1 0        0               0 Oct 08  2022 1.txt
drwxr-xr-x    3 0        0            4096 Jul 21  2023 kchong
-rw-r--r--    1 0        0             387 Oct 08  2022 minio_test.py
-rwxr-xr-x    1 0        0             248 Oct 08  2022 xiaozhan.sh
226 Directory send OK.
配置ftp在本地server或者某个地方----然后启动qemu linux后从本地server上用ftp拷贝这些ntp目录------
windriver@pek-vx-iperf211:~$ ftp 128.224.178.153
Connected to 128.224.178.153.
220 (vsFTPd 3.0.5)
Name (128.224.178.153:windriver): xli3
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp>
========================================================================
-p IFCONFIG_1='"ifname eth0","devname driver","inet driver", "gateway driver"' -p IPCOM_TELNET_PORT='"2323"' -p IPRIP_IFCONFIG_1='"eth9 broadcast"' -p NUM_FILES=1000 -p RTP_FD_NUM_MAX=100 -p SHELL_DEFAULT_CONFIG='"INTERPRETER=,LINE_EDIT_MODE=,LINE_LENGTH=4096,STRING_FREE=manual,VXE_PATH=.;/romfs"'  -c INCLUDE_IPNDP_CMD -c INCLUDE_IPPING6_CMD -c INCLUDE_IPRADVD_CMD -smp -c INCLUDE_IPFTP_CMD -c INCLUDE_IPFTPS -c INCLUDE_USER_DATABASE -c INCLUDE_SECURITY -c INCLUDE_IPCOM_USE_KEY_DB -c INCLUDE_IPCOM_KEY_DB_CMD -c INCLUDE_LOGIN_BANNER -c INCLUDE_IPTELNETS -c INCLUDE_TELNET_CLIENT -p  LOGIN_BANNER_TEXT='"Login Banner #1"' -p  SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'

-p  LOGIN_BANNER_TEXT='"Login Banner #1"'

-p LOGIN_BANNER_TEXT='"Login Banner
/bin/sh: -c: line 0: unexpected EOF while looking for matching `''
/bin/sh: -c: line 1: syntax error: unexpected end of file

vxprj create -vsb itl_generic_vsb itl_generic llvm /home/xli3/vxworks/itl_generic_vip -inet6 -c INCLUDE_SHELL -c INCLUDE_SHELL_INTERP_CMD -c INCLUDE_IPCOM_SHELL_CMD -c INCLUDE_DISK_UTIL -c INCLUDE_IPCOM_USE_RAM_DISK -c INCLUDE_DISK_UTIL_SHELL_CMD -c INCLUDE_HRFS -c INCLUDE_HRFS_FORMAT -c INCLUDE_RAM_DISK -c INCLUDE_IFCONFIG -c INCLUDE_ROMFS -c INCLUDE_IPTELNETS -c INCLUDE_IPNET_IFCONFIG_1 -c INCLUDE_NETSMP_CMD -c INCLUDE_ERRNOS_CMD -c INCLUDE_KEYADM_CMD -c INCLUDE_USER_DATABASE -c INCLUDE_SECURITY -c INCLUDE_IPQUEUE_CONFIG_CMD -c INCLUDE_IPSYSCTL_CMD -c INCLUDE_IPCOM_USE_TIME_CMD -c INCLUDE_IPCOM_SYSLOGD_CMD -c INCLUDE_IPCOM_SYSLOGD_USE_LOG_FILE -c INCLUDE_IPIFCONFIG -c INCLUDE_IPIFCONFIG_CMD -c INCLUDE_IPROUTE_CMD -c INCLUDE_HOST_TBL -c INCLUDE_IPCOM_SYSVAR_CMD -c INCLUDE_IPTCP_TEST_CMD -c INCLUDE_IPARP_CMD -c INCLUDE_IPVERSION_CMD -c INCLUDE_IPD_CMD -c INCLUDE_IPECHO_CLIENT_CMD -c INCLUDE_IPECHO_SERVER_CMD -c INCLUDE_IPSOCKTEST_CMD -c INCLUDE_IPPING_CMD -c INCLUDE_IPNET_PCAP_CMD -c INCLUDE_IPNETSTAT_CMD -c INCLUDE_DISK_UTIL_SHELL -c INCLUDE_PCAP_CMD -c INCLUDE_ROUTECMD -c INCLUDE_IPDHCPS -c INCLUDE_IPDHCPC -c INCLUDE_IPDHCPR -c INCLUDE_IPMCAST_PROXY_CMD -c INCLUDE_IPMCP -c INCLUDE_IP_SECURITY -c INCLUDE_IPSECCTRL_CMD -c INCLUDE_INTERNET_KEY_EXCHANGE -c INCLUDE_IPMCP_USE_IGMP -c INCLUDE_IPMCP_USE_MLD -c INCLUDE_TELNET_CLIENT -c INCLUDE_STANDALONE_SYM_TBL -c INCLUDE_DEBUG -c INCLUDE_DEBUG_KPRINTF -c INCLUDE_IPFIREWALL -c INCLUDE_IPFIREWALL_CMD -c INCLUDE_IPRADVD -c INCLUDE_IPRADVD_CMD -c INCLUDE_IPRIP -c INCLUDE_IPRIP_CTRL_CMD -c INCLUDE_IPTFTP_CLIENT_CMD -c INCLUDE_INCLUDE_IPTFTPS -c INCLUDE_IPPING6_CMD -c INCLUDE_IPATTACH -c INCLUDE_IPFTP_CMD -c INCLUDE_IPFTPS -c INCLUDE_IPCOM_USE_KEY_DB -c INCLUDE_IPCOM_KEY_DB_CMD -c INCLUDE_LOGIN_BANNER -p IFCONFIG_1='"ifname eth0","devname driver","inet driver","gateway driver"' -p IPCOM_TELNET_PORT='"2323"' -p IPRIP_IFCONFIG_1='"eth9 broadcast"' -p SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"' -p NUM_FILES=1000 -p INET_ENABLE_FORWARDING=1 -p INET6_ENABLE_FORWARDING=1 -p RTP_FD_NUM_MAX=100 -p SHELL_DEFAULT_CONFIG='"INTERPRETER=,LINE_EDIT_MODE=,LINE_LENGTH=4096,STRING_FREE=manual,VXE_PATH=.;/romfs"' -p LOGIN_BANNER_TEXT='"Login Banner

[xli3@pek-vx-29075 itl_generic_vip]$ vxprj parameter setstring LOGIN_BANNER_TEXT "Login Banner #1"
========================================================================================================
调整架构，在network_protocol评级的目录添加一个conftest.py----里面设置每个case开头打印log的提示信息如下：=====这个conftest.py里面的函数适用于整个network_protocol目录=
如果是单独的用于某个测试suite的装饰器，就在对应的目录例如crypto里面创建conftest.py,里面写装饰器
@pytest.fixture(scope='function', autouse=True)
def fixture_log():
    log.info('-' * 80)
    log.info('-' * 30 + ' Test starts ' + '-' * 37)
    log.info('-' * 80)
    yield
    log.info('-' * 80)
    log.info('-' * 30 + ' Test ends ' + '-' * 39)
    log.info('-' * 80)
30 passed, 5 skipped in 66.12s (0:01:06)  架构调整后执行整个crypto的时间从155秒缩短为66秒------------不清楚为什么会提升效率---------后续研究
====================================================================================================================================
在boot_qemu_ez.py里面增加对测试结果的统计：------为了将来对接xray或者其它工具存储测试结果
def teardown_class(self):
    # clean up vxworks
    for t in self.vx_targets:
        t.cleanup()
        t.logFile.close()
    # process self.result ----store result,upload to Database or sth like that
    for i in self.result:
        if i[1] == 'PASS':
            self.pass_num += 1
        else:
            self.fail_num += 1
    log.info('----test result statistics----')
    log.info(self.result)      # xiaozhan, i[0] is case name, i[1] is pass or fail
    log.info(f'total:{len(self.result)}, pass:{self.pass_num}, fail:{self.fail_num}')
=======================================================================================
conftest.py ---添加module参数--
module = 'FTP'
# xiaozhan, debug
if build_image is True:
    buildVxworks(cfg[module], installPath, bsp, tool, smp, m64bit, cpu, ipv6, module, spin)  # xiaozhan, debug

def buildVxworks(cfg, installPath, bsp, tool, smp, m64bit, cpu=None, ipv6=False, module=None, debug=False, spin=True):
添加一个module=None  来解决FTP的添加vip参数问题---vxprj parameter setstring LOGIN_BANNER_TEXT "Login Banner #1"
buildVip(cfg, installPath, bsp, tool, smp, m64bit, cpu, ipv6, module, debug, spin)
# os.chdir("%s_vip" % bsp)
os.chdir(vipPath)    # xiao zhan, debug

# xiaozhan---workaround for FTP parameter
if module == 'FTP':
    cmd = 'vxprj parameter setstring LOGIN_BANNER_TEXT "Login Banner #1"'
    runCmd(cmd, wrenvPrefix)
执行后抓取的添加参数log如下：
/home/xli3/vxworks/wrenv.sh -p vxworks LM_LICENSE_FILE=27000@ala-lic4.wrs.com vxprj parameter setstring LOGIN_BANNER_TEXT "Login Banner #1"
>>>>>> /home/xli3/vxworks/wrenv.sh -p vxworks LM_LICENSE_FILE=27000@ala-lic4.wrs.com vxprj build
如何执行命令参考：
def runCmd(x, cmd_prefix=''):
    print(">>>>>> " + cmd_prefix + x)
    lines = shCmd(cmd_prefix + x + " 2>&1")
    for line in lines:
        print(line)
    return lines

def shCmd(cmd, sudo=False):
    if sudo:
        cmd = 'sudo ' + cmd
    lines = os.popen(cmd).readlines()
    if debugFlag:
        print('\n%s %s' % (shcmdIndicator, cmd))
        print('\n'.join(lines))
    return lines
===================================================================================================================
调试FTP suite遇到的问题--启动qemu的时候失败--手动执行--界面如下  --暂时去掉这些相关组件，只涉及到一个case
Adding 14702 symbols for standalone.
Login Banner #1

sudo qemu-system-x86_64 -m 2048 -smp 4 -machine q35 -kernel /folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-ftp/vxWorks -append "sysbootline:gei(0,0) e=192.168.123.30" -netdev tap,id=mynet30,ifname=tap-QEMU-Q35-3,script=no,downscript=no -device e1000,netdev=mynet30,mac=00:40:47:a8:7b:1e --serial stdio -nographic -monitor none -enable-kvm
========================================================================
清除我的Jenkins log==
[xli3@pek-vx-29075 xiaozhan-pytest-auto]$ ll
total 204K
drwxr-xr-x 7 xli3 users 4.0K Mar 13 20:46 allure-report/
drwxr-xr-x 3 xli3 users 196K Mar 10 21:16 allure_trial/
[xli3@pek-vx-29075 xiaozhan-pytest-auto]$ pwd
/home/xli3/Jenkins/workspace/xiaozhan-pytest-auto
直接删除上面两个文件夹
=============================================================

./runKong.sh -m FTP -g /workspace/svc-cmnet/CISPIN/vx20240305221023_vx_2409/ -c ipftp.ftp.cmd_dir buildTest
check FTP log on KONG:

192.168.198.2_XunXiqX
 364 Trying 192.168.198.2...^M
 365 Connected to 192.168.198.2.^M
 366 Escape character is '^]'.^M
 367 220- Login Banner #1^M
 368 220 FTP server ready.^M
 369 USER ftp^MUSER ftp^MUSER ftp^M
 370 331 Password required for user ftp^M
 371 PASS interpeak^MPASS interpeak^MPASS interpeak^M
 372 230 Login OK^M
 373 PWD^MPWD^MPWD^M
 374 257 "/ram/" is current directory^M
 375 PWD^MPWD^MPWD^M
 376 257 "/ram/" is current directory^M
 377 MKD dir_ftptest^MMKD dir_ftptest^MMKD dir_ftptest^M
 ===========================================================
 FTP  ----qemu error as below when enabling login with banner---xiaozhan,暂时不考虑banner

 udbMgr: path to the user database may not be null! Abort initialization.
Instantiating /ram as rawFs,  device = 0x10001
Formatting /ram for DOSFS
Instantiating /ram as rawFs, device = 0x10001
Formatting...Retrieved old volume params with %38 confidence:
Volume Parameters: FAT type: FAT32, sectors per cluster 0
  0 FAT copies, 0 clusters, 0 sectors per FAT
  Sectors reserved 0, hidden 0, FAT sectors 0
  Root dir entries 0, sysId (null)  , serial number 80000
  Label:"           " ...
Disk with 64 sectors of 512 bytes will be formatted with:
Volume Parameters: FAT type: FAT12, sectors per cluster 1
  2 FAT copies, 54 clusters, 1 sectors per FAT
  Sectors reserved 1, hidden 0, FAT sectors 2
  Root dir entries 112, sysId VXDOS12 , serial number 80000
  Label:"           " ...
OK.

 Adding 14702 symbols for standalone.
Login Banner #1
====================================================
MongoDB---query---  { "board" : "idpQ35-18180" }
=====================================================
FTP test suite中运用了类似于下面的pexpect.spawn---看情况做调整--原来的架构太老了，可能不适用--Pexpect版本已经更新
支持直接发送 self.conn.sendline(cmd)
参考下面的最新写法：
tcmd = "telnet %s %s" % (self.Terminal_Server, int(self.Terminal_Server_Port) + 2000)
# http://t.zoukankan.com/mmdln-p-9006274.html
self.conn = pexpect.spawn(tcmd, echo=False, timeout=timeout, encoding='utf-8')
if debugFlag:  # xiaozhan this did not set log file
    self.conn.logfile = sys.stdout  # turn on pexpect debugging
==========================================================================================

cat /etc/redhat-release  --centos version

vi SOCKTEST/cvs/iptestengine/src/log/test.log_20240315_15.45.46
=============================================================================
debug socktest ===   def test_socktest_udp_c0170recvmsg_controllen(self, version):   修改了case架构---取消了return_all()的匹配--应用最简洁的方式来实现复杂的匹配

s_cmd = 'C recvmsg_controllen_test%s(1)' % s6
s.send(s_cmd)
s.expect('bind ok.')

c.sendAndExpect(c_cmd, self.vxprompt)
try:
    s.expect('test pass')
except:
    ret = 'FAIL'
    log.error('msg_controllen is not 0 when truncated')
else:
    ret = 'PASS'
finally:
    record_result_expect(self.result, ret, case_name)


192.168.199.2>ifconfig eth0 inet add 10.218.1.1/24
 689 192.168.199.2_XunXiqX
 690
 691 192.168.199.3>ifconfig eth0 inet add 10.218.1.2/24
 692 192.168.199.3_XunXiqX


192.168.199.3>C mysendto("10.218.1.1/24")
 869 socket created ..., id: 19
 870 rmote ip: 10.218.1.1/24
 871 remote port: 8888
 872 value = 0 = 0x0
 873 192.168.199.3_XunXiqX
 874
 875 192.168.199.2>C recvmsg_controllen_test(1)
 876 socket created ..., id: 19
 877 bind ok.
 878 local port: 8888
 879 Original msg.msg_controllen : 1
 880
 881 len = 8
 882 recvmsg runs successfully.
 883 msg.iov_base : hello!
 884 msg.msg_controllen : 0
 885 msg.msg_flags: 0x20
 886
 887 test pass
 888 value = 0 = 0x0
 889 192.168.199.2_XunXiqX
 890
 891 192.168.199.3>C mysendto("10.218.1.1/24")
 892 socket created ..., id: 19
 893 rmote ip: 10.218.1.1/24
 894 remote port: 8888
 895 value = 0 = 0x0
 896 192.168.199.3_XunXiqX
 897
 898 192.168.199.2>C recvmsg_controllen_test(16)
 899 socket created ..., id: 19
 900 bind ok.
 901 local port: 8888
 902 Original msg.msg_controllen : 16
 903
 904 len = 8
 905 recvmsg runs successfully.
 906 msg.iov_base : hello!
 907 msg.msg_controllen : 0
 908 msg.msg_flags: 0x20
 909
 910 test pass
 911 value = 0 = 0x0

C recvmsg_controllen_test(1)      this is running on s-- target 1
C mysendto("192.168.123.10/24")    this is on c target 2

[xli3@pek-vx-29075 config]$ telnet 192.168.123.10 2323   --- this is s
Trying 192.168.123.10...
Connected to 192.168.123.10.
Escape character is '^]'.

-> cmd

[vxWorks]# C recvmsg_controllen_test(1)
socket created ..., id: 29
bind ok.
local port: 8888
Original msg.msg_controllen : 1
                                        # below will print after input command on target 2
len = 8
recvmsg runs successfully.
msg.iov_base : hello!
msg.msg_controllen : 0
msg.msg_flags: 0x20

test pass
value = 0 = 0x0
[vxWorks]#


[xli3@pek-vx-29075 3pp-download]$ telnet 192.168.123.20 2323     --- this is c -- target 2
Trying 192.168.123.20...
Connected to 192.168.123.20.
Escape character is '^]'.

-> cmd
[vxWorks]# C mysendto("192.168.123.10/24")
socket created ..., id: 29
rmote ip: 192.168.123.10/24
remote port: 8888
value = 0 = 0x0
[vxWorks]#
========================================================
====NetworkBuilder add()====192.168.123.20/24
====start the target QEMU-Q35-2 192.168.123.20/24
sudo ifconfig qemuBridge inet 192.168.123.1/24 up

self.ip = ip(self.config['ip'])   --ip是一个class--感觉没必要封装
assert isinstance(self.ip, ip)
解读上面的代码---self.ip是一个类的实例--打印log其实就是192.168.123.20/24这种ip地址格式
ezEestEngine.py里面也是用了class ip这个类---考虑修改成更简单的版本---这样就需要更改架构里面所有设计到ip地址相关的操作
需要仔细走读代码---根据自己的需求来修改架构
=========================================================
socktest --debug 连续跑整个test suite会失败两个case，单独跑这个case没问题--
查看一下case的执行顺序--想办法调整一下即可--可以把这个case挪到最后面执行
FAILED test_cases/network_protocol/socktest/test_socktest.py::TestSocktest::test_socktest_udp_c0070send[IPv4] - AssertionErro...
FAILED test_cases/network_protocol/socktest/test_socktest.py::TestSocktest::test_socktest_udp_c0070send[IPv6] - Asserti
或者用最简单的rerun即可---pytest -s test_cases/network_protocol/socktest --reruns=1

=================================================================================
手动调试FTP case：  when qemu is up, run below commands
[xli3@pek-vx-29075 pytestAuto]$ telnet 192.168.123.10 21
Trying 192.168.123.10...
Connected to 192.168.123.10.
Escape character is '^]'.
220 FTP server ready.
ABOR
530 Login required
PASS
501 Invalid number of arguments
USER ftp
331 Password required for user ftp
PASS nogood
230 Login OK


打开另外一个窗口---
[xli3@pek-vx-29075 pytestAuto]$ telnet 192.168.123.10 21
Trying 192.168.123.10...
Connected to 192.168.123.10.
Escape character is '^]'.
220 FTP server ready.
USER ftp
331 Password required for user ftp
PASS interpeak
230 Login OK
USER ftp
503 Cannot change user
PASS interpeak
503 Already logged in
QUIT
221 Bye
Connection closed by foreign host.
[xli3@pek-vx-29075 pytestAuto]$

C4C里面暂时取消用户管理，不知道在哪里设置FTP用户名和密码 ---暂时去掉这部分case--不检查用户名 密码即可登录
====================================================================================
添加下面的函数去获取IP地址--- ifconfig -a  or ifconfig eth0
def get_ip(self, cmd):
    # TODO    xiaozhan, use sendAndReturnAll to get ipv4 and ipv6 addresses to replace the original -- class ip
    ret = self.sendAndReturnAll(cmd, self.osPrompt)
    ret = '\n'.join(ret)
    print('ifconfig -a\n', ret)
    return ret
==============================================================================================
ftps是直接来自于pexpect.spawn--所以直接采用sendline来替换原来的send--sendline默认支持自带换行
ftps.sendline('PASV')
ftps.expect(r'227 Entering passive mode \([0-9,]*\)')


ftps.expect('215 UNIX Type: L8 Version: IPFTPS 6.8')

PASV
227 Entering passive mode (192,168,123,10,208,129)

ftps.sendline('SYST')
ftp_expect_prompt_and_match_response(ftps, '215 UNIX Type: L8')      # 这个代码需要删除-不够灵活---替换成下面的代码
ftps.expect(r'215 UNIX Type: L8 Version: IPFTPS (\d+\.\d+)')   ---
==============================================================
debug ====
ftps.expect('257 \"' + fs_root + '/?\" is current directory')
E           TypeError: can only concatenate str (not "bytes") to str

[xli3@pek-vx-29075 pytestAuto]$ telnet 192.168.123.10 21
Trying 192.168.123.10...
Connected to 192.168.123.10.
Escape character is '^]'.
220 FTP server ready.

USER ftp
331 Password required for user ftp
PASS interpeak
230 Login OK
PWD
257 "/ram/" is current directory
abor
226 No data connection
SYST
215 UNIX Type: L8 Version: IPFTPS 6.8
PASV
227 Entering passive mode (192,168,123,10,208,129)
421 Timeout, closing control connection

lines = ['211- Session status:', 'Server: 192.168.123.20 port 21', 'Client: 192.168.123.10 port 54198', 'Type: Ascii', 'Mode: Stream', 'Stru]
response = ('211- Session status:', 'Server: 192.168.123.20 port 21', 'Client: 2000::3 port [1-9][0-9]{,4}'), cmd_only = False, offset = 0
===============================
ftp.cmd_stat------log
192.168.199.2>quote stat
 779 211- Session status:
 780  Server: 10.78.1.2 port 21
 781  Client: 10.78.1.1 port 56326
 782  Type: Ascii
 783  Mode: Stream
 784  Structure: File
 785  Readonly: No
 786  Proxy FTP: No
 787 211 End of status
 788 ftp>
 789
 790 192.168.199.2>quit
 791 221 Bye
sysvar set -o -c ipnet.inet.IcmpRedirectSend "1"
1663 sysvar: ipnet.inet.IcmpRedirectSend=1 ok


ifconfig eth0 inet delete 10.78.1.1/24
sysvar unset ipftps.tls.enable
sysvar unset ipftps.tls.cert_file

192.168.199.2>open 2005:78::1:2   ---this is for FTP IPv6
1954 220- Login Banner #1
1955 220 FTP server ready.
1956 Connected to 2005:78::1:2
1957 User:
1958
1959 192.168.199.2>ftp
1960 Password:
1961
1962 192.168.199.2>
1963 230 Login OK
1964 ftp>
1965
1966 192.168.199.2>pwd
1967 257 "/ram/" is current directory
1968 ftp>
1969
1970 192.168.199.2>quote stat    ---this is for FTP IPv6
1971 211- Session status:
1972  Server: 2005:78::1:2 port 21
1973  Client: 2005:78::1:1 port 49162
1974  Type: Ascii
1975  Mode: Stream
1976  Structure: File
==================================IP调试----注意事项
原来的KONG框架里面  str(ftps.ip().addr)  凡是这种IP地址的--一定要打印出来查看是IPv4还是IPv6--
一般是两种都有-----在现有框架里面需要做区分----直接函数获取IPv4和IPv6地址---在case走不同分支
ftp_verify_response(lines, ('211- Session status:',
                        # 'Server: ' + str(ftps.ip().addr) + ' port 21',
                        'Server: ' + self.ftps_ip[1] + ' port 21',
                        'Client: ' + ipaddr_re + ' port [1-9][0-9]{,4}'), cmd_only=False)

在FTP 测试中注意---只有是执行了 ftp_login(ftpc, ftps, ip) 之后再调用ftpc.sendAndExpect等，此时prompt是 ftp>

==================================================================
debug cmd transfer

open 192.168.123.20
INFO     test_log/test.log:ezTargets.py:882 --- send=ftp
INFO     test_log/test.log:ezTargets.py:882 --- send=interpeak
INFO     test_log/test.log:ezTargets.py:893 --- send=pwd
DEBUG    test_log/test.log:ezTargets.py:929 ret is

DEBUG    test_log/test.log:ezTargets.py:930 ['257 "/ram/" is current directory']
INFO     test_log/test.log:ezTargets.py:893 --- send=pwd
DEBUG    test_log/test.log:ezTargets.py:929 ret is

DEBUG    test_log/test.log:ezTargets.py:930 ['257 "/ram/" is current directory']
INFO     test_log/test.log:ezTargets.py:893 --- send=mkdir dir_ftptest
DEBUG    test_log/test.log:ezTargets.py:929 ret is

DEBUG    test_log/test.log:ezTargets.py:930 ['257 "dir_ftptest" directory created']
INFO     test_log/test.log:ezTargets.py:893 --- send=cd dir_ftptest
DEBUG    test_log/test.log:ezTargets.py:929 ret is

DEBUG    test_log/test.log:ezTargets.py:930 ['250 CWD changed']
INFO     test_log/test.log:ezTargets.py:893 --- send=pwd
DEBUG    test_log/test.log:ezTargets.py:929 ret is

DEBUG    test_log/test.log:ezTargets.py:930 ['257 "/ram/dir_ftptest" is current directory']
INFO     test_log/test.log:ezTargets.py:893 --- send=binary
DEBUG    test_log/test.log:ezTargets.py:929 ret is

DEBUG    test_log/test.log:ezTargets.py:930 ['200 Type I selected']
INFO     test_log/test.log:ezTargets.py:893 --- send=quote XFTP creat fil_1 10000
DEBUG    test_log/test.log:ezTargets.py:929 ret is

DEBUG    test_log/test.log:ezTargets.py:930 ['200 OK']
INFO     test_log/test.log:ezTargets.py:893 --- send=get fil_1
DEBUG    test_log/test.log:ezTargets.py:929 ret is

DEBUG    test_log/test.log:ezTargets.py:930 ['File transfer error: (open: errno = 0x13)']
ERROR    test_log/test.log:test_ftp.py:143 Too few lines in response


quote XFTP creat fil_1 10000
DEBUG    test_log/test.log:ezTargets.py:929 ret is

DEBUG    test_log/test.log:ezTargets.py:930 ['200 OK']
INFO     test_log/test.log:ezTargets.py:893 --- send=get fil_1
DEBUG    test_log/test.log:ezTargets.py:929 ret is

DEBUG    test_log/test.log:ezTargets.py:930 ['File transfer error: (open: errno = 0x13)']

ftp> rename fil_1 fil_2
250 File renamed

ftp> del fil_2
250 File deleted

ftp> delete fil_1
250 File deleted

ftp> rmdir /ram/dir_ftptest
250 Directory removed



ftp> dir
229 Entering extended passive mode (|||52458|)
125 Using existing data connection
drwxrwxrwx   1 0      0             512 Jan 01  1980 dir_ftptest
-rwxrwxrwx   1 0      0             228 Jan 01  1980 syslog
226 Transfer complete



ftp> rstatus
211- Session status:
 Server: 192.168.123.20 port 21
 Client: 192.168.123.10 port 56713
 Type: Binary
 Mode: Stream
 Structure: File
 Readonly: No
 Proxy FTP: No
211 End of status

----this is a bug----
ftp> pwd
257 "/ram" is current directory
ftp> mkdir dir_ftptest
257 "dir_ftptest" directory created
ftp> cd dir_ftptest
250 CWD changed
ftp> quote XFTP creat fil_1 10000
200 OK
ftp> dir
229 Entering extended passive mode (|||53067|)
125 Using existing data connection
-rwxrwxrwx   1 0      0           10000 Jan 01  1980 fil_1
226 Transfer complete
ftp> pwd
257 "/ram/dir_ftptest" is current directory
ftp> rmdir /ram/dir_ftptest
550 errno = 0xf
ftp> del /ram/dir_ftptest/fil_1
250 File deleted
ftp> rmdir /ram/dir_ftptest
250 Directory removed
ftp> pwd
257 "/ram/dir_ftptest" is current directory   ---这里应该为空目录才对
ftp>
对比下面linux上的ftp操作----vxworks上的操作不对
ftp> pwd
257 "/folk/xli3" is the current directory
ftp> mkdir aaaaa
257 "/folk/xli3/aaaaa" created
ftp> cd aaaaa
250 Directory successfully changed.
ftp> pwd
257 "/folk/xli3/aaaaa" is the current directory
ftp> rmdir /folk/xli3/aaaaa
250 Remove directory operation successful.
ftp> pwd
257 "" is the current directory    # this is right

考虑修改 ftp_login(ftpc, ftps, ip, ftpuser='ftp', ftppasswd='interpeak', passive=0, extended=0):
因为ftps这个参数就是设置一些sysvar --可以拿到函数外面来设置
============================================================
FTP 控制面的session---sendline之后expect--然后匹配输出---如果输出只有一行--可以适当取代sendAndReturnAll函数
ftps_ctrl.sendline('PWD')
ftps_ctrl.expect('257 \"(.*)/?\" is current directory')
fs_root = ftps_ctrl.match.group(1)  # xiaozhan /ram/
# print('debug', fs_root)    # xiaozhan   debug  /ram/
if fs_root[-1] == '/':
    fs_root = fs_root[:-1]  # /ram
=============================================

XFTP creat fil_1 820000
451 errno = 0x1c  ---this should be 200 OK

XFTP creat fil_1 820000
451 errno = 0x1c
XFTP creat fil_1 1000
200 OK
PASV
227 Entering passive mode (192,168,123,20,240,253)

ftps_ctrl.expect(r'(?s)Stream.*226 No data connection')   ---xiaozhan 正则跨行匹配 (?s)
=====================================================debug
用下面的代码来替换原来的raise_fail()函数 ----直接跳转到异常处理
if 'nisse' in ret:
    log.error('Failed to delete key_id nisse')
    assert False
=======================================================================================

keydb import buf kalle
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=Enter key:
INFO     test_log/test.log:ezTargets.py:867 --- send=kallekalle
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=Re-type key:
INFO     test_log/test.log:ezTargets.py:867 --- send=kallekalle
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=Failed: already installed
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=#
INFO     test_log/test.log:ezTargets.py:867 --- send=keydb import buf kalle
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=Enter key:
INFO     test_log/test.log:ezTargets.py:867 --- send=kalle
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=Re-type key:
INFO     test_log/test.log:ezTargets.py:867 --- send=ellak
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=Failed. Entered keys do not match
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=#
INFO     test_log/test.log:ezTargets.py:882 --- send=keydb delete buf kalle
INFO     test_log/test.log:ezTargets.py:867 --- send=keydb list buf
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=['kalle', '# ']
INFO     test_log/test.log:ezTargets.py:867 --- send=keydb import buf kalle
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=Enter key:
INFO     test_log/test.log:ezTargets.py:867 --- send=kallekalle
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=Re-type key:
INFO     test_log/test.log:ezTargets.py:867 --- send=kallekalle
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=#
INFO     test_log/test.log:ezTargets.py:867 --- send=keydb list buf
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=kalle
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=#
INFO     test_log/test.log:ezTargets.py:882 --- send=keydb delete buf kalle
INFO     test_log/test.log:ezTargets.py:867 --- send=keydb list buf
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=['kalle', '# ']
INFO     test_log/test.log:ezTargets.py:867 --- send=keydb list buf
DEBUG    test_log/test.log:ezTargets.py:875 --- expect=['nisse', '# ']
==============================================================================

def verify_buf_does_not_exist():
    ret = 5
    if 1 == 1:
        assert False   # 如果走到断言失败---不会执行下面的ret
    return ret
res = verify_buf_does_not_exist()   # 进到函数里面会执行失败- 执行不到return ret那行代码
print(res)    -----不会执行
====================================================================