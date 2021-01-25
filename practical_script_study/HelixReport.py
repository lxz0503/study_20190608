#!/usr/bin/env python
import re
import sys
import time
from operator import itemgetter, attrgetter

from KongConfig import kongJenkins, kongUser, kongPassword
from KongRerunTest import AnalyzeJenkinsTestResult
from InstallSpin import GetSpinInfo
from LTAF import NightlyRecord, NightlyReportWriter, ConvertTestNameToLTAF, ConvertTestResultToLTAF, NightlyTestReader, LTAFTestResult
from Mail import SendEmail
from HelixConfig import helixEmailReceivers, helixTestPlanToReport
from Jenkins import GetBuildConsole

def reportToLTAF(testResults, bsp, module, branch):
    # write nightly test results on the other date
    name = ''
    spinType = 'helix'
    if branch.find('/HELIXSPIN/') != -1:
        name = 'HELIXSPIN'
    elif branch.find('/HELIXCISPIN/') != -1:
        name = 'HELIXCISPIN'
    else:
        raise Exception('unknown helix release name %s' % branch)
    release = GetSpinInfo(name, 'release')
    toDate = GetSpinInfo(name, 'date')
    print('=== release=%s, date=%s' % (release, toDate))     
    #toDate = '2019-09-01'

    writer = NightlyReportWriter(spinType, release, toDate)
    for tr in testResults:
        x = createHelixNightlyRecord(tr, bsp, module)
        writer.AddTestResult(x)
    writer.Store()
    

def createHelixNightlyRecord(tr, bsp, module):
    configs = { 'itl_generic'        : 'Dynamic',
                'nxp_layerscape_a72' : 'Dynamic',
                'xlnx_zynqmp'        : 'Static',
              }
    
    networkNightlyRecord = {
                 'testName' : '',               # must be filled up
                 'testSuite' : '',              # must be filled up
                 'runDate' : '',                # must be filled up
                 'status' : '',                 # must be filled up
                 'log' : '',   
                 'component' : 'networking',   
                 'tester' : 'KONG',
                 'automation' : 'Auto',  
                 'requirement' : '',
                 'trDomain' : 'networking',
                 'funcPass' : '',              # must be filled up
                 'funcFail' : '',              # must be filled up
                 'bsp' : '',      
                 'board' : '',       
                 'spin' : '',      
                 'tags' : 'KONG-helix-nightly', 
                 'updateTime' : '',  
                 'defects' : '',   
                 'comment' : '',    
                 'tech' : 'guestOS',          # must be filled up
                 'configLabel' : 'vx7smp32',  # must be filled up
                 'configuration' : '',        # must be filled up
                }

    testName, testResult = tr
    networkNightlyRecord['testName'] = ConvertTestNameToLTAF(testName)
    networkNightlyRecord['status'] = ConvertTestResultToLTAF(testResult)
    networkNightlyRecord['testSuite'] = module
    networkNightlyRecord['bsp'] = bsp
    networkNightlyRecord['runDate'] = GetSpinInfo('HELIXSPIN', 'date')
    networkNightlyRecord['spin'] = GetSpinInfo('HELIXSPIN', 'name')
    
    if bsp in configs:
        networkNightlyRecord['configuration'] = configs[bsp]
    
    if ConvertTestResultToLTAF(testResult) == 'Pass':
        networkNightlyRecord['funcPass'] = '1'
        networkNightlyRecord['funcFail'] = '0'
    else:
        networkNightlyRecord['funcPass'] = '0'
        networkNightlyRecord['funcFail'] = '1'
        
    return NightlyRecord(**networkNightlyRecord)


def printTestResult(testResults):
    testResults = sorted(testResults, key=itemgetter(0))
    for tn, tr in testResults:
        print('\t\t%s : %s' % (tn, tr))


def outputLTAFSummary(release, component, tags, reportDate, num, tester):
    fetcher = NightlyTestReader(release, component, tags, reportDate, num, tester)
    html = fetcher.GetHtml()

    body = []
   
    nightlyResult = LTAFTestResult()
    records = nightlyResult.GetRecords(html)
    for r in sorted(records, key=attrgetter('testName')):
        print('%s %s %s' % (r.testName, r.testSuite, r.status))
        body.append('%s %s %s' % (r.testName, r.testSuite, r.status))
    numPass = len([x for x in records if x.status == 'Pass'])
    numFail = len([x for x in records if x.status == 'Fail'])
    numBlocked = len([x for x in records if x.status == 'Blocked'])
    body.insert(0, 'total=%s, pass=%s, fail=%s, blocked=%s\n' % (numPass + numFail + numBlocked, 
                                                                 numPass, numFail, numBlocked))
    body.insert(0, '%s\n' % fetcher.url)
    print('\ntotal=%s, pass=%s, fail=%s, blocked=%s' % (numPass + numFail + numBlocked, 
                                                        numPass, numFail, numBlocked))
    print('\n%s' % fetcher.url)
    
    sender = 'libo.chen@windriver.com'
    to = helixEmailReceivers
    subject = 'Kong Helix Report on %s' % reportDate
    SendEmail(sender, to, subject, '\n'.join(body))
    

def combineWithPredefine(testResults, predefinedTests):
    # predefinedTests is a dictionary
    tests = predefinedTests
    for tn, tr in testResults:
        if tn in tests:
            tests[tn] = tr
        else:
            print('ERROR: %s not in predefined test' % tn)
    retTestResults = []
    for tn in sorted(tests.keys()):
        retTestResults.append( (tn, tests[tn]))
    return retTestResults
            

def getTestResults(kongJob, kongBuild):
    content = GetBuildConsole(kongJenkins, kongJob, kongBuild, user=kongUser, password=kongPassword)
    found = re.findall('(?s)runKong.sh -g .*? -m (.*?) -c (.*?) -b (.*?) --helix', content)
    if found is None:
        raise Exception('bsp/module/tests not found in %s %s' % (kongJob, kongBuild))
    
    bsp = found[0][2]
    module = found[0][0]
    tests = sorted(list(set(found[0][1].split(','))))

    selectedTestPlanToReport = {}
    for testNameWithVersion in helixTestPlanToReport[module]:
        testName = testNameWithVersion.split(' - ')[0]
        if testName in tests:
            selectedTestPlanToReport[testNameWithVersion] = helixTestPlanToReport[module][testNameWithVersion]
    
    testResults, _ = AnalyzeJenkinsTestResult(kongJob, kongBuild, kongJenkins)

    newTestResults = combineWithPredefine(testResults, selectedTestPlanToReport)
    testNames = sorted(list(set([x[0].split(' - ')[0] for x in newTestResults])))
    assert(tests == testNames)
    return newTestResults


def getBranch(kongJob, kongBuild):
    content = GetBuildConsole(kongJenkins, kongJob, kongBuild, user=kongUser, password=kongPassword)
    found = re.findall('(?s)\nSPIN:(.*?)\n', content)
    if found is None:
        raise Exception('bsp/module/tests not found in %s %s' % (kongJob, kongBuild))
    
    branch = found[0]
    return branch


def test_getBranch():
    job = 'helix-test-nxp_layerscape_a72'
    build = 522 # 539 HELIXCISPIN, 522 HELIXSPIN
    branch = getBranch(job, build)
    print('branch=%s' % branch)
    if branch.find('/HELIXCISPIN/') != -1:
        print('HELIX CISPIN')
    elif branch.find('/HELIXSPIN/') != -1:
        print('HELIX SPIN')
    else:
        print('others')
    

def getNotPassedTests(module, kongJob, kongBuild):
    if True:
        testResults = getTestResults(kongJob, kongBuild)
        return sorted(list(set([x[0].split(' - ')[0] for x in testResults if x[1] != 'OK'])))
    else:
        testResults, _ = AnalyzeJenkinsTestResult(kongJob, kongBuild, kongJenkins)
        failedTests = [x[0] for x in combineWithPredefine(testResults, helixTestPlanToReport[module]) if x[1] != 'OK']
        return sorted(list(set([x.split(' - ')[0] for x in failedTests])))


def test_getTestResults():
    module = 'FIREWALL'
    kongJob = 'helix-test-nxp_layerscape_a72'
    kongBuild = 495
    tests = getTestResults(kongJob, kongBuild)
    for x in tests: print(x)


def test_getNotPassedTests():
    module = 'IKE-ADVANCED'
    kongJob = 'helix-test-itl_generic'
    kongBuild = 1277
    testResults = getNotPassedTests(module, kongJob, kongBuild)
    for x in testResults: print(x)
    if len(testResults) == 3:
        print('1st test passed')
    else:
        print('1st test failed')
    
    """    
    module = 'IKE-BASIC'
    kongBuild = 496
    testResults = getNotPassedTests(module, kongJob, kongBuild)
    for x in testResults: print(x)
    if testResults == []:
        print('2nd test passed')
    else:
        print('2nd test failed')
    """
            
def reportSummary(helixTasks):
    for bsp in sorted(helixTasks.keys()):
        print('bsp=%s' % bsp)
        modules = sorted(helixTasks[bsp])
        for mod in modules:
            print('\tmodule=%s' % mod)
            if helixTasks[bsp][mod][1][0] == 'test':
                project = helixTasks[bsp][mod][1][1]
                build   = helixTasks[bsp][mod][1][2]
                if helixTasks[bsp][mod][1][3] in ('SUCCESS', 'FAILURE'):
                    testResults, _ = AnalyzeJenkinsTestResult(project, build, kongJenkins)
                    testResults = combineWithPredefine(testResults, helixTestPlanToReport[mod])
                else:
                    testResults = combineWithPredefine([], helixTestPlanToReport[mod])
                printTestResult(testResults)
                if testResults:
                    branch = getBranch(project, build)
                    reportToLTAF(testResults, bsp, mod, branch)

    release = GetSpinInfo('HELIXSPIN', 'release')
    component = 'networking'
    tags = 'KONG-helix-nightly'
    tester = 'KONG'
    reportDate = GetSpinInfo('HELIXSPIN', 'date')
    num = 3000
    outputLTAFSummary(release, component, tags, reportDate, num, tester)
    

def test_reportSummary():
    tasks = {
  'itl_generic': { 'DNSC': [ ['build', 'helix-build-slave', 1705, u'SUCCESS'],
                             ['test', 'helix-test-itl_generic', 740, u'SUCCESS'],
                             ['report', 'helix-report', 1023, u'SUCCESS']],
                   'FTP': [ ['build', 'helix-build-slave', 1709, u'SUCCESS'],
                            ['test', 'helix-test-itl_generic', 741, u'SUCCESS'],
                            ['report', 'helix-report', 1025, u'SUCCESS']],
                   'IKE-ADVANCED': [ ['build', 'helix-build-slave', 1713, u'SUCCESS'],
                                     ['test', 'helix-test-itl_generic', 742, u'FAILURE'],
                                     ['report', 'helix-report', 1029, u'SUCCESS']],
                   'IPNET': [ ['build', 'helix-build-slave', 1717, u'SUCCESS'],
                              ['test', 'helix-test-itl_generic', 743, u'FAILURE'],
                              ['report', 'helix-report', 1032, u'SUCCESS']],
                   'IPNET-IPSEC': [ ['build', 'helix-build-slave', 1721, u'SUCCESS'],
                                    ['test', 'helix-test-itl_generic', 744, u'SUCCESS'],
                                    ['report', 'helix-report', 1033, u'SUCCESS']],
                   'MCP': [ ['build', 'helix-build-slave', 1725, u'SUCCESS'],
                            ['test', 'helix-test-itl_generic', 745, u'SUCCESS'],
                            ['report', 'helix-report', 1036, u'SUCCESS']],
                   'NET_VLAN': [ ['build', 'helix-build-slave', 1727, u'SUCCESS'],
                                 ['test', 'helix-test-itl_generic', 746, u'SUCCESS'],
                                 ['report', 'helix-report', 1037, u'SUCCESS']],
                   'NTP': [ ['build', 'helix-build-slave', 1729, u'SUCCESS'],
                            ['test', 'helix-test-itl_generic', 747, u'SUCCESS'],
                            ['report', 'helix-report', 1042, u'SUCCESS']],
                   'QOS': [ ['build', 'helix-build-slave', 1731, u'SUCCESS'],
                            ['test', 'helix-test-itl_generic', 748, u'FAILURE'],
                            ['report', 'helix-report', 1044, u'SUCCESS']],
                   'RADIUS': [ ['build', 'helix-build-slave', 1733, u'SUCCESS'],
                               ['test', 'helix-test-itl_generic', 749, u'SUCCESS'],
                               ['report', 'helix-report', 1046, u'SUCCESS']],
                   'ROHC_IP': [ ['build', 'helix-build-slave', 1735, u'SUCCESS'],
                                ['test', 'helix-test-itl_generic', 750, u'SUCCESS'],
                                ['report', 'helix-report', 1047, u'SUCCESS']],
                   'ROHC_UDP': [ ['build', 'helix-build-slave', 1737, u'SUCCESS'],
                                 ['test', 'helix-test-itl_generic', 751, u'SUCCESS'],
                                 ['report', 'helix-report', 1049, u'SUCCESS']],
                   'SECEVENT': [ ['build', 'helix-build-slave', 1739, u'SUCCESS'],
                                 ['test', 'helix-test-itl_generic', 752, u'SUCCESS'],
                                 ['report', 'helix-report', 1050, u'SUCCESS']],
                   'SSH': [ ['build', 'helix-build-slave', 1741, u'SUCCESS'],
                            ['test', 'helix-test-itl_generic', 753, u'SUCCESS'],
                            ['report', 'helix-report', 1053, u'SUCCESS']],
                   'SSHCLIENT': [ ['build', 'helix-build-slave', 1743, u'SUCCESS'],
                                  ['test', 'helix-test-itl_generic', 754, u'SUCCESS'],
                                  ['report', 'helix-report', 1058, u'SUCCESS']],
                   'USERAUTH_LDAP': [ ['build', 'helix-build-slave', 1744, u'SUCCESS'],
                                      ['test', 'helix-test-itl_generic', 755, u'SUCCESS'],
                                      ['report', 'helix-report', 1059, u'SUCCESS']],
                   'VRRP': [ ['build', 'helix-build-slave', 1745, u'SUCCESS'],
                             ['test', 'helix-test-itl_generic', 756, u'SUCCESS'],
                             ['report', 'helix-report', 1060, u'SUCCESS']]},
  'nxp_layerscape_a72': { 'FIREWALL': [ ['build', 'helix-build-slave', 1704, u'SUCCESS'],
                                        ['test', 'helix-test-nxp_layerscape_a72', 213, u'SUCCESS'],
                                        ['report', 'helix-report', 1026, u'SUCCESS']],
                          'IKE-ALGORITHMS': [ ['build', 'helix-build-slave', 1706, u'SUCCESS'],
                                              ['test', 'helix-test-nxp_layerscape_a72', 214, u'SUCCESS'],
                                              ['report', 'helix-report', 1034, u'SUCCESS']],
                          'IKE-BASIC': [ ['build', 'helix-build-slave', 1708, u'SUCCESS'],
                                         ['test', 'helix-test-nxp_layerscape_a72', 215, u'SUCCESS'],
                                         ['report', 'helix-report', 1040, u'SUCCESS']],
                          'IKE-DAEMON': [ ['build', 'helix-build-slave', 1710, u'SUCCESS'],
                                          ['test', 'helix-test-nxp_layerscape_a72', 216, u'SUCCESS'],
                                          ['report', 'helix-report', 1048, u'SUCCESS']],
                          'IKE-IPEAP': [ ['build', 'helix-build-slave', 1712, u'SUCCESS'],
                                         ['test', 'helix-test-nxp_layerscape_a72', 217, u'FAILURE'],
                                         ['report', 'helix-report', 1051, u'SUCCESS']],
                          'IKE-ROHC-IPSEC': [ ['build', 'helix-build-slave', 1714, u'SUCCESS'],
                                              ['test', 'helix-test-nxp_layerscape_a72', 218, u'SUCCESS'],
                                              ['report', 'helix-report', 1055, u'SUCCESS']],
                          'IPSEC-IPCRYPTO': [ ['build', 'helix-build-slave', 1716, u'SUCCESS'],
                                              ['test', 'helix-test-nxp_layerscape_a72', 219, u'SUCCESS'],
                                              ['report', 'helix-report', 1061, u'SUCCESS']],
                          'RIP': [ ['build', 'helix-build-slave', 1718, u'SUCCESS'],
                                   ['test', 'helix-test-nxp_layerscape_a72', 220, u'SUCCESS'],
                                   ['report', 'helix-report', 1062, u'SUCCESS']],
                          'RIPNG': [ ['build', 'helix-build-slave', 1720, u'SUCCESS'],
                                     ['test', 'helix-test-nxp_layerscape_a72', 221, u'FAILURE'],
                                     ['report', 'helix-report', 1063, u'SUCCESS']],
                          'SCTP': [ ['build', 'helix-build-slave', 1722, u'SUCCESS'],
                                    ['test', 'helix-test-nxp_layerscape_a72', 222, u'FAILURE'],
                                    ['report', 'helix-report', 1064, u'SUCCESS']],
                          'SYSVIEW': [ ['build', 'helix-build-slave', 1724, u'SUCCESS'],
                                       ['test', 'helix-test-nxp_layerscape_a72', 223, 'INPROGRESS'],
                                       ['report', 'na', 'na', 'na']]},
  'xlnx_zynqmp': { 'CRYPTO': [ ['build', 'helix-build-slave', 1703, u'SUCCESS'],
                               ['test', 'helix-test-xlnx_zynqmp', 199, u'FAILURE'],
                               ['report', 'helix-report', 1024, u'SUCCESS']],
                   'DHCP': [ ['build', 'helix-build-slave', 1707, u'SUCCESS'],
                             ['test', 'helix-test-xlnx_zynqmp', 200, u'SUCCESS'],
                             ['report', 'helix-report', 1027, u'SUCCESS']],
                   'DHCP6': [ ['build', 'helix-build-slave', 1711, u'SUCCESS'],
                              ['test', 'helix-test-xlnx_zynqmp', 201, u'SUCCESS'],
                              ['report', 'helix-report', 1028, u'SUCCESS']],
                   'IKE-AUTHENTICATION': [ ['build', 'helix-build-slave', 1715, u'SUCCESS'],
                                           ['test', 'helix-test-xlnx_zynqmp', 202, u'FAILURE'],
                                           ['report', 'helix-report', 1030, u'SUCCESS']],
                   'IKE-RACOON': [ ['build', 'helix-build-slave', 1719, u'SUCCESS'],
                                   ['test', 'helix-test-xlnx_zynqmp', 203, u'FAILURE'],
                                   ['report', 'helix-report', 1031, u'SUCCESS']],
                   'IKE-SETTINGS': [ ['build', 'helix-build-slave', 1723, u'SUCCESS'],
                                     ['test', 'helix-test-xlnx_zynqmp', 204, u'FAILURE'],
                                     ['report', 'helix-report', 1035, u'SUCCESS']],
                   'NAT': [ ['build', 'helix-build-slave', 1726, u'SUCCESS'],
                            ['test', 'helix-test-xlnx_zynqmp', 205, u'SUCCESS'],
                            ['report', 'helix-report', 1038, u'SUCCESS']],
                   'PPP': [ ['build', 'helix-build-slave', 1728, u'SUCCESS'],
                            ['test', 'helix-test-xlnx_zynqmp', 206, u'FAILURE'],
                            ['report', 'helix-report', 1039, u'SUCCESS']],
                   'ROHC_ESP': [ ['build', 'helix-build-slave', 1730, u'SUCCESS'],
                                 ['test', 'helix-test-xlnx_zynqmp', 207, u'SUCCESS'],
                                 ['report', 'helix-report', 1041, u'SUCCESS']],
                   'ROHC_TCP': [ ['build', 'helix-build-slave', 1732, u'SUCCESS'],
                                 ['test', 'helix-test-xlnx_zynqmp', 208, u'FAILURE'],
                                 ['report', 'helix-report', 1043, u'SUCCESS']],
                   'SNMP': [ ['build', 'helix-build-slave', 1734, u'SUCCESS'],
                             ['test', 'helix-test-xlnx_zynqmp', 209, u'SUCCESS'],
                             ['report', 'helix-report', 1045, u'SUCCESS']],
                   'SNTP_CLIENT': [ ['build', 'helix-build-slave', 1736, u'SUCCESS'],
                                    ['test', 'helix-test-xlnx_zynqmp', 210, u'SUCCESS'],
                                    ['report', 'helix-report', 1052, u'SUCCESS']],
                   'SSL': [ ['build', 'helix-build-slave', 1738, u'SUCCESS'],
                            ['test', 'helix-test-xlnx_zynqmp', 211, u'SUCCESS'],
                            ['report', 'helix-report', 1054, u'SUCCESS']],
                   'TFTP': [ ['build', 'helix-build-slave', 1740, u'SUCCESS'],
                             ['test', 'helix-test-xlnx_zynqmp', 212, u'SUCCESS'],
                             ['report', 'helix-report', 1056, u'SUCCESS']],
                   'USERDB': [ ['build', 'helix-build-slave', 1742, u'SUCCESS'],
                               ['test', 'helix-test-xlnx_zynqmp', 213, u'SUCCESS'],
                               ['report', 'helix-report', 1057, u'SUCCESS']]}
                }    
    reportSummary(tasks)
    

def rerunModuleReport():
    def reportModule(tasks, n):
        job = tasks[n][1]
        build = tasks[n][2]
        tests = getTestResults(job, build)
        branch = getBranch(job, build)
        reportToLTAF(tests, bsp, mod, branch)
    
    from myTask import myTasks
    for bsp in myTasks:
        for mod in myTasks[bsp]:
            tasks = myTasks[bsp][mod]
            if tasks[1][0] == 'test':
                reportModule(tasks, 1)
            if (tasks[3][0] == 'retest' and tasks[3][1] != 'na'):
                reportModule(tasks, 3)
                    
    
def main():
    # HelixReport.py $BRANCH=JOB $NEWCOMMIT=BUILD $MODULE $BSP
    # check arguments
    if len(sys.argv) != 5:
        print('\nusage:%s $BRANCH $NEWCOMMIT $MODULE $BSP')
        sys.exit(1)

    print('=== helix test')    
    branch, newCommit, module, bsp = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    project = branch
    build = newCommit
    #testResults, _ = AnalyzeJenkinsTestResult(project, build, kongJenkins)
    testResults = getTestResults(project, build)
    print(testResults)
    if testResults:
        branch = getBranch(project, build)
        reportToLTAF(testResults, bsp, module, branch)
    
    
if __name__ == '__main__':
    main()
    #rerunModuleReport()
    #test_reportSummary()
    #test_getTestResults()
    #test_getNotPassedTests()
    #test_getBranch()
    
