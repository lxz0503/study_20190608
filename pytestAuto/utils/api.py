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
import re
import time
import sys

sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.log_record import log

vxprompt = '# '

def runSockTest(protocol, funcName, hostA, hostB, version, parentTestName, timeout, minInterval=10):
    definedProtocols = ('all', 'udp', 'tcp')
    if protocol in definedProtocols:
        protocolId = definedProtocols.index(protocol)
    else:  # xiaozhan, debug
        log.error('protocol %s not found' % protocol)
        assert False

    funcNames = (
        'socket', 'bind', 'connect', 'accept', 'getsockname', 'getpeername', 'send', 'sendto', 'sendmsg', 'recv',
        'recvfrom', 'recvmsg', 'ioctl', 'select', 'shutdown', 'close')
    funcId = funcNames.index(funcName) + 1

    if version == 'IPv6':
        # start socktest servers
        svr_cmd = 'C sock6testServerStart'
        log.info(f'Run on target {hostB.board}->{svr_cmd}')    # xiaozhan, this will show on screen if using pytest -s interminal
        hostB.sendAndExpect(svr_cmd, vxprompt)      # xiaozhan,  modify

        # b_ip = hostB.ip(6)
        b_ip = '2000::4/64'  # xiaozhan
        cmd = 'C sock6test "%s", %s, %s, 0' % (b_ip, protocolId, funcId)
        log.info('%s %s IPv6 test' % (protocol, funcName))
    else:
        # start socktest servers
        svr_cmd = 'C socktestServerStart'
        log.info(f'Run on target {hostB.board}->{svr_cmd}')
        hostB.sendAndExpect(svr_cmd, vxprompt)

        # b_ip = hostB.ip()
        b_ip = '192.168.123.20/24'  # xiaozhan
        cmd = 'C socktest "%s", %s, %s, 0' % (b_ip, protocolId, funcId)
        log.info('%s %s IPv4 test' % (protocol, funcName))
    log.info(f'Run on target {hostA.board}->{cmd}')
    ret = hostA.sendAndReturnAll(cmd, vxprompt)   # xiaozhan, debug

    stp = SockTestParser('\n'.join(ret), version)   # xiaozhan debug
    test_results = stp.parse(parentTestName=parentTestName)

    return test_results  # must have for C test cases


class SockTestParser(object):
    def __init__(self, content, version):  # xiaozhan debug
        self.content = content
        self.version = version    # xiaozhan debug
        self.ptnTestSuite = r'(?s)TEST-CASE-\d+\n(.*?)\*\*\* TESTS COMPLETE\n'    # xiaozhan-- (?s) means cross-line search
        self.ptnTestCase = '(.*?):(.*?) returned .*?'    # xiaozhan, regular expression for each case

    def isTestCase(self, theLine):
        return theLine.find(':') != -1 and theLine.find(' returned ') != -1

    def createTestName(self, theStr, parentTestName=None):
        tokens = (' ', ':', '::', '.', '/', '(', ')', ',', '=', '>',)
        for t in tokens:
            theStr = theStr.strip().replace(t, '_')
        theStr = filter(lambda x: x not in ('', '_'), [x.strip() for x in theStr.split('_')])
        theStr = '_'.join(theStr)
        if parentTestName is None:
            return theStr
        else:
            return parentTestName + '.' + theStr + '-' + self.version   # xiaozhan

    def parse(self, parentTestName=None):
        rets = []
        testSuites = self.__parseTestSuite(self.content)

        for testSuite in testSuites:
            log.info('testsuite %s' % testSuite)   # xiaozhan, this is same as ret, keep or remove it based on your requirement
            for theLine in testSuite.split('\n'):
                if self.isTestCase(theLine):
                    testResult, testName = self.__parseTestCase(theLine)
                    rets.append((self.createTestName(testName, parentTestName), testResult.strip()))
        return rets

    def __parseTestSuite(self, content):
        return re.findall(self.ptnTestSuite, content)

    def __parseTestCase(self, theLine):
        if self.isTestCase(theLine):
            found = re.search(self.ptnTestCase, theLine)
            if found is not None:
                return found.groups()[0], found.groups()[1]
            else:
                return '', ''


