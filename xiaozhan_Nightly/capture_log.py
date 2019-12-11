#!/usr/bin/env python
import time
import os

cmd = "sudo /opt/Ixia/IxANVL880/ANVL-SRC/Bin/ix86-Linux/anvl -l low -f %s %s %s | tee %s 2>&1" %(cfgDir, suite, case, logDir)
curTime = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
logFolder = '/root' + '/ANVL_Vx' + '_' + curTime
if not os.path.exists(logFolder):
    os.system("mkdir -p %s" % logFolder)

def run_anvl_for_one_suite(suite, cfgDir, logDir, case, version):
    cmd = "sudo /opt/Ixia/IxANVL880/ANVL-SRC/Bin/ix86-Linux/anvl -l low -f %s %s %s | tee %s 2>&1" %(cfgDir, suite, case, logDir)
    os.chdir("/opt/Ixia/IxANVL880/ANVL-SRC/")
    os.popen(cmd)

# logFolder=/root/ANVL-automation/ANVL_Vx7_2019-12-05_19-49-56
# cmd=sudo /opt/Ixia/IxANVL880/ANVL-SRC/Bin/ix86-Linux/anvl -l low -f /opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlrip_SplitHorizon rip 8.17 |
# tee /root/ANVL-automation/ANVL_Vx7_2019-12-05_19-49-56/RipSplitHorizon.log 2>&1
# Kernel TCP:
# sp iperf3,"-c 118.1.1.2 -t 10 -i 10 -f m -l 64 -N"
# sp iperf3,"-c 118.1.1.2 -t 10 -i 10 -f m -l 1024"
# sp iperf3,"-c 118.1.1.2 -t 10 -i 10 -f m -l 65536"
#
# Kernel UDP:
# sp iperf3,"-c 118.1.1.2 -t 10 -i 10 -f m -b 0 -l 1400 -u"
#
# RTP TCP:
# rtpSp "/romfs/iperf3.vxe -c 118.1.1.2 -t 10 -i 10 -f m -l 64 -N"
# rtpSp "/romfs/iperf3.vxe -c 118.1.1.2 -t 10 -i 10 -f m -l 1024"
# rtpSp "/romfs/iperf3.vxe -c 118.1.1.2 -t 10 -i 10 -f m -l 65536"
#
# RTP UDP:
# rtpSp "/romfs/iperf3.vxe -c 118.1.1.2 -t 10 -i 10 -f m -b 0 -l 1400 -u"