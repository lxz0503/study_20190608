#############################################################################
#
# Copyright (c) 2006-2013 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

"System viewer network stack tests"

import os
import time

wvfile = 'test.wvr'
wvtextfile = 'test.txt'

#wind_platform = 'vxworks-6.6'
#wind_home = '/usr/local/VxWorks6.6_VX27.07FA_MSP'
#wind_base = '/usr/local/VxWorks6.6_VX27.07FA_MSP/vxworks-6.6'
#wind_wrsv_path = '/usr/local/VxWorks6.6_VX27.07FA_MSP/workbench-3.0/wrsv/4.10'

#wind_platform = 'vxworks-6.7'
#wind_home = '/usr/local/VxWorks6.7_VX26.WB34.08FA_MSP'
#wind_base = '/usr/local/VxWorks6.7_VX26.WB34.08FA_MSP/vxworks-6.7'
#wind_wrsv_path = '/usr/local/VxWorks6.7_VX26.WB34.08FA_MSP/workbench-3.1/wrsysviewer'

#wind_platform = 'vxworks-6.7'
#wind_home = '/usr/local/TestHarness/installations/VxWorks6.7_VX37C.WB46C'
#wind_base = '/usr/local/TestHarness/installations/VxWorks6.7_VX37C.WB46C/vxworks-6.7'
#wind_wrsv_path = '/usr/local/TestHarness/installations/VxWorks6.7_VX37C.WB46C/workbench-3.1/wrsysviewer'

# wind_platform = 'vxworks-6.9'
# wind_home = '/usr/local/TestHarness/installations/VxWorks6.9_VX111A.WB48'
# wind_base = '/usr/local/TestHarness/installations/VxWorks6.9_VX111A.WB48/vxworks-6.9'
# wind_wrsv_path = '/usr/local/TestHarness/installations/VxWorks6.9_VX111A.WB48/workbench-3.3/wrsysviewer'

# WIND_VX_HOME and WIND_VX_VERSION are set in file ipcom/util/scripts/runtestsuite.py, if running these
# test cases through iptestengine directly, you should set wind_platform, wind_home, wind_base and
# wind_wrsv_path manually.
envstr = os.getenv('WIND_VX_HOME')
if envstr:
    wind_home = envstr
    wind_platform = os.getenv('WIND_VX_PLATFORM')
    wind_base = os.getenv('WIND_VX_BASE')
    wind_wrsv_path = wind_home + '/workbench-4/wrsysviewer'


################################################################################
#        wvnet_check - check if wvnet command is available
################################################################################
def wvnet_check(session):
    if session.is_shellcmd_present('wvnet'):
        return 'ok'
    else:
        return 'skipped'


################################################################################
#        wvnet_start - start logging
################################################################################
def wvnet_start(t):
    t.send('wvnet start')
    t.expect_exact_and_wait_prompt('Logging network events')


################################################################################
#        wvnet_stop - stop logging
################################################################################
def wvnet_stop(t):
    t.send('wvnet stop %s' % wvfile)
    t.expect_exact_and_wait_prompt('Stopped logging network events')


################################################################################
#        wvnet_download - download log file
################################################################################
def wvnet_download(t):
    try:
        os.remove(wvfile)
    except OSError:
        pass
    try:
        os.remove(wvtextfile)
    except OSError:
        pass
    t.ftp_get(wvfile)
    t.send('rm %s' % wvfile)
    t.wait_prompt()

    cmd  = wind_home + '/wrenv.linux -p ' + wind_platform + ' bash -c '
    cmd += '"export PATH=$PATH:' + wind_wrsv_path + '/host/x86_64-linux2/bin && '
    cmd += 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:' + wind_wrsv_path + '/host/x86_64-linux2/lib && '
    cmd += 'wvr2txt test.wvr | grep WV_NETDEVENT > ' + wvtextfile + '"'
    # print '####' + cmd
    os.system(cmd)


################################################################################
#        wvnet_verify - download log file
################################################################################
def wvnet_verify(modulename, tag, lo, hi):

    modules = ['ipnet.c',
               'ipnet_netif.c',
               'ipnet_ip4.c',
               'ipnet_ip6.c',
               'ipnet_sock_tcp.c',
               'ipnet_udp.c',
               'ipnet_eth.c',
               'ipnet_frag.c',
               'ipnet_icmp6.c',
               'ipnet_neigh.c',
               'ipnet_pkt_pool.c',
               'ipnet_raw.c',
               'ipnet_sock.c',
               'ipnet_tunnel.c',
               'iptcp.c']
    count = 0

    lines = open(wvtextfile).readlines()
    #print lines
    for line in lines:
        try:
            line  = line[line.index('wvEvtInfo='):]
            line  = line[len('wvEvtInfo='):line.index(' ')]
            event = int(line, 16)
        except ValueError:
            raise test_fail('Missing wvEvtInfo')
        component = (event >> 30) & 0x3
        if component != 2:
            raise test_fail('Not WINDNET_DUAL_STACK component')
        module = (event >> 8) & 0xff
        if module < 128 or module > (128 + len(modules)):
            raise test_fail('Not an IPNET module')
        #print str(modules[module-128]) + ':' + str(event & 0xff)
        if modulename == modules[module-128] and tag == (event & 0xff):
            count += 1
    if count < lo or count > hi:
        raise test_fail('Found %d event tags with id %d in %s while the accepted interval was %d-%d!' % (count, tag, modulename, lo, hi))



################################################################################
#        ping
################################################################################
class ping:
    '''Verify that an incoming echo request generate a system viewer network event.'''

    def config(self):
        self.eta = 6
        self.hosts = 2
        self.works_on_lkm = False
        self.works_on_iplite = False
        self.v6 = True

    def test(self, log, hosts, v6, __):
        t,h = hosts
        if wvnet_check(t) == 'skipped':
            return 'skipped'
        h.ping(t.ip(), count = 2, retries = 2)
        wvnet_start(t)
        h.ping(t.ip(), count = 4, retries = 2)
        wvnet_stop(t)
        wvnet_download(t)
        if v6:
            wvnet_verify('ipnet_icmp6.c', 1, 4, 4)
        else:
            wvnet_verify('ipnet_ip4.c', 21, 4, 4)


################################################################################
#        tcp_reset
################################################################################
class tcp_reset:
    '''Verify that a connection attempt to an unused TCP port generate a system
       viewer network event for the TCP reset.'''

    def config(self):
        self.eta = 1
        self.hosts = 2
        self.works_on_lkm = False
        self.works_on_iplite = False
        self.v6 = True

    def test(self, log, hosts, v6, __):
        t,h = hosts
        if wvnet_check(t) == 'skipped':
            return 'skipped'
        wvnet_start(t)
        h.ipcom_shell().echoclient(t.ip().addr, proto = 'tcp', chunk_size = 1024,
                                   succeed = False, connection_refused = True)
        wvnet_stop(t)
        wvnet_download(t)
        wvnet_verify('iptcp.c', 33, 1, 1)


################################################################################
#        icmp_unreach
################################################################################
class icmp_unreach:
    '''Verify that a connection attempt to an unused UDP port generate a system
       viewer network event for the ICMP destination unreachable message.'''

    def config(self):
        self.eta = 1
        self.hosts = 2
        self.works_on_lkm = False
        self.works_on_iplite = False
        self.v6 = True

    def test(self, log, hosts, v6, __):
        t,h = hosts
        if wvnet_check(t) == 'skipped':
            return 'skipped'
        wvnet_start(t)
        h.ipcom_shell().echoclient(t.ip().addr, proto = 'udp', chunk_size = 1024,
                                   succeed = False, connection_refused = True)
        wvnet_stop(t)
        wvnet_download(t)
        if v6:
            wvnet_verify('ipnet_icmp6.c', 10, 1, 1)
        else:
            wvnet_verify('ipnet_ip4.c', 40, 1, 1)


################################################################################
#        frag
################################################################################
class frag:
    '''Verify that the first incoming fragment of a datagram generates a system
       viewer network event for the reassembly queue.'''

    def config(self):
        self.eta = 6
        self.hosts = 2
        self.works_on_lkm = False
        self.works_on_iplite = False
        self.v6 = True

    def test(self, log, hosts, v6, __):
        t,h = hosts
        if wvnet_check(t) == 'skipped':
            return 'skipped'
        h.ping(t.ip(), count = 2, retries = 2)
        wvnet_start(t)
        h.ping(t.ip(), count = 4, retries = 2, packetsize = 2000)
        wvnet_stop(t)
        wvnet_download(t)
        if v6:
            wvnet_verify('ipnet_frag.c', 3, 4, 4)
        else:
            wvnet_verify('ipnet_frag.c', 2, 4, 4)


################################################################################
#        arp
################################################################################
class arp:
    '''Verify that an outgoing IPv4 packet generates a system viewer network
       event for the ARP request.'''

    def config(self):
        self.eta = 2
        self.hosts = 2
        self.works_on_lkm = False
        self.works_on_iplite = False
        self.v6 = False

    def test(self, log, hosts, v6, __):
        t,h = hosts
        if wvnet_check(t) == 'skipped':
            return 'skipped'
        t.send('arp -d %s' % h.ip().addr)
        t.wait_prompt()
        wvnet_start(t)
        t.ping(h.ip(), count = 2, retries = 2)
        wvnet_stop(t)
        wvnet_download(t)
        wvnet_verify('ipnet_eth.c', 21, 1, 1)


################################################################################
#        neigh
################################################################################
class neigh:
    '''Verify that an outgoing IPv6 packet generates a system viewer network
       event for the Neighbour solicitation request.'''

    def config(self):
        self.eta = 2
        self.hosts = 2
        self.works_on_lkm = False
        self.works_on_iplite = False
        self.v4 = False
        self.v6 = True

    def test(self, log, hosts, v6, __):
        t,h = hosts
        if wvnet_check(t) == 'skipped':
            return 'skipped'
        t.send('ndp -d %s' % h.ip().addr)
        t.wait_prompt()
        wvnet_start(t)
        t.ping(h.ip(), count = 2, retries = 2)
        wvnet_stop(t)
        wvnet_download(t)
        wvnet_verify('ipnet_neigh.c', 1, 1, 2)


################################################################################
#        udp
################################################################################
class udp:
    '''Verify that incoming UDP packets generate system viewer network events.'''

    def config(self):
        self.eta = 1
        self.hosts = 2
        self.works_on_lkm = False
        self.works_on_iplite = False
        self.v6 = True

    def test(self, log, hosts, v6, __):
        t,h = hosts
        if wvnet_check(t) == 'skipped':
            return 'skipped'
        wvnet_start(t)
        t.ipcom_shell().echoserver(proto = 'udp')
        h.ipcom_shell().echoclient(t.ip().addr, proto = 'udp', chunk_size = 1024)
        t.ipcom_shell().stop_echoserver()
        wvnet_stop(t)
        wvnet_download(t)
        wvnet_verify('ipnet_udp.c', 3, 1, 2)
