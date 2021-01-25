import os
import re
import sys
import time
import pprint
import random
from operator import itemgetter

from jenkins import Jenkins

from KongConfig import *
from Jenkins import GetJobBuildsFromMultiJob
from KongRerunTest import GetBuildConsole, SplitRawTestResult, GetModName
from KongTestPlanToReport import kongTestPlanToReport
from HelixConfig import *

moduleDurationFile = '/folk/lchen3/ttemp/modDuration.py'
notPassedDuration = -0.001


def getAllTestResultList(content):
    rets = []
    rawTestResult = FindRawTestResult(content)
    if rawTestResult:
        testCaseRawStrs = SplitRawTestResult(rawTestResult)
        for oneTestCaseStr in testCaseRawStrs:
            testName, testResult, duration = parseOneTestCaseResult(oneTestCaseStr)
            if testResult is not None: # None means that the testName is not valid, so remove it
                rets.append((testName, testResult, duration))
        return rets
    else:
        return []
    

def FindRawTestResult(content):   
    # '(?s)Total ETA: .*?20\d\d\)(.*?)rounds:' find the first section
    # while '(?s)Total ETA: .*20\d\d\)(.*?)rounds:' finds the second section one if there is any failed test cases
    r = re.search('(?s)Total ETA: .*?20\d\d\)(.*?)rounds:', content)
    if r is not None:
        return r.groups()[0]
    else:
        return ''


def parseOneTestCaseResult(testCase):
    debug = False
    testResult = None
    duration = ''
    tokens = testCase.split('ETA:')
    testName = tokens[0].strip()
    
    if debug and testName == 'ipike.daemon.event_log1 - IPv4':
        print('test case raw string:|%s|' % testCase)
    
    if testCase.find('ETA:') == -1:
        return testCase, None, ''
    resultTokens = [x.strip() for x in tokens[1].replace('\n', ' ').split(' ') if x != '']
    
    if debug and testName == 'ipike.daemon.event_log1 - IPv4':
        print(resultTokens)
    
    resultTokens.reverse()
    
    for i in xrange(len(resultTokens)):  # handle tokens from right to left
        lastToken = resultTokens[i]
        if lastToken in ['OK', 'failed', 'skipped', 'OKException']:
            if lastToken == 'OKException':
                testResult = 'OK'
            else:
                testResult = lastToken
            if testResult == 'OK':
                if debug and testName == 'ipike.daemon.event_log1 - IPv4':
                    print('i=%s' % i)
                if i == 2:
                    duration = '%s%s' % (resultTokens[1], resultTokens[0])
                if i == 1:
                    duration = '%s' % resultTokens[0]
                else:
                    Exception('cannot find duration for %s' % testCase)
            else:
                duration = notPassedDuration
            break

    if debug and testName == 'ipike.daemon.event_log1 - IPv4':
        print('%s, %s, %s' % (testName, testResult, duration))
    
    return testName, testResult, duration


def filterJobs(jobBuilds):
    return [x for x in jobBuilds if x[0].startswith('ut-vxsim-') and not x[0].startswith('ut-vxsim-RTNET')]


def convertDuration(tn, tr, duration):
    if tr == 'OK':
        if duration.find('m') == -1:
            s = duration.replace('s', '')
            if s:
                duration = int(s)
            else:
                duration = 0
        else:
            m, s = duration.split('m')
            s = s.replace('s', '')
            duration = int(m) * 60 + int(s)
    return tn, tr, duration


def getModName(job, build):
    content = GetBuildConsole(kongJenkins, job, build, kongUser, kongPassword)
    return getModNameFromContent(content)


def getModNameFromContent(content):
    # kong native
    # /runtestsuite.py --uml=.*? --smp (.*?) --no-rebuild
    found = re.findall('(?s)/runtestsuite.py --uml=.*? --smp (.*?) --no-rebuild', content)
    if found:
        return found[0].strip()
    else:
        return ''
    
        
def handleModule(testPlans, job, build):
    print('handing %s %s' % (job, build))
    bsp = 'vxsim_linux'
    module = getModName(job, build)
    #print(module)
    if module in testPlans[bsp]:
        content = GetBuildConsole(kongJenkins, job, build, kongUser, kongPassword)
        testResults = getAllTestResultList(content)
        if testResults:
            for tn, tr, d in testResults:
                tn, tr, d = convertDuration(tn, tr, d)
                #print('%s, %s, %s' % (tn, tr, d))
                if tn in testPlans[bsp][module]:
                    testPlans[bsp][module][tn] = d
        else:
            print('test result not found')
    return testPlans


def filterTestPlans(testPlans, modules):
    bsp = 'vxsim_linux'
    retTestPlans = {}
    retTestPlans[bsp] = {}
    for mod in modules:
        if mod in testPlans[bsp]:
            retTestPlans[bsp][mod] = testPlans[bsp][mod]
    return retTestPlans


def statModuleDuration(testPlans, module, bsp='vxsim_linux'):
    # return totalDurion (seconds), # of -0.001
    total, numOfNotPassed = 0, 0
    if bsp is None:
        theTestPlans = testPlans
    else:
        theTestPlans = testPlans[bsp]
    if module in theTestPlans:
        for tn in theTestPlans[module]:
            if theTestPlans[module][tn] in (notPassedDuration, 'Blocked'):
                numOfNotPassed += 1
            else:
                #if type(testPlans[bsp][module][tn]) in ('int', 'float'):
                total += float(theTestPlans[module][tn])
                #else:
                #    print('%s=%s' % (tn, testPlans[bsp][module][tn]))
    return total, numOfNotPassed    


def handleRerun(jobBuilds, testPlans):
    bsp = 'vxsim_linux'
    _, ciSummaryBuild = [x for x in jobBuilds if x[0] == 'ci-summary'][0]
    content = GetBuildConsole(kongJenkins, 'ci-summary', ciSummaryBuild, kongUser, kongPassword)
    founds = re.findall('(?s)\nStarted ci-rerun-test #(.*?)\n', content)
    for build in founds:
        rerunResult = GetBuildConsole(kongJenkins, 'ci-rerun-test', int(build), kongUser, kongPassword)
        module = getModNameFromContent(rerunResult)
        testResults = getAllTestResultList(rerunResult)
        if testResults:
            for tn, tr, d in testResults:
                tn, tr, d = convertDuration(tn, tr, d)
                if tn in testPlans[bsp][module]:
                    if d > testPlans[bsp][module][tn]:
                        testPlans[bsp][module][tn] = d        
    return testPlans

            
def printTestDuration(testPlans, modules):
    requiredTestPlans = filterTestPlans(testPlans, modules)
    pp = pprint.PrettyPrinter(indent=2, width=100)    
    pp.pprint(requiredTestPlans)  
    
        
def printModuleDuration(testPlans, modules):
    requiredTestPlans = filterTestPlans(testPlans, modules)
    bsp = 'vxsim_linux'
    print('\n')
    maxModLen = max([len(x) for x in requiredTestPlans[bsp].keys()]) + 4
    for mod in sorted(requiredTestPlans[bsp].keys()):
        total, numOfNotPassed = statModuleDuration(requiredTestPlans, mod)
        print('%s\t%s\t%s' % (mod + ' ' * (maxModLen - len(mod)), total, numOfNotPassed))
    
    print(len(requiredTestPlans[bsp]))
    

def main():
    job = 'ci-manager'
    build = 2427
    jobBuilds = GetJobBuildsFromMultiJob(kongJenkins, job, build, kongUser, kongPassword)
    networkJobBuilds = filterJobs(jobBuilds)
    modules = sorted( list(set([GetModName(x[0]) for x in networkJobBuilds])) )
    #print(handleRerun(jobBuilds, kongTestPlanToReport))
    #sys.exit(0)
    
    testPlans = dict(kongTestPlanToReport)
    for job, build in networkJobBuilds:
        handleModule(testPlans, job, build)

    testPlans = handleRerun(jobBuilds, testPlans)  
    printTestDuration(testPlans, modules)
    printModuleDuration(testPlans, modules)

#################################################

def statistic_test_duration_by_module():
    modConfig = moduleDurationFile

    sys.path.insert(0, os.path.dirname(modConfig))
    from modDuration import helixTestPlanToReport
    
    totalAll = 0
    maxModLen = max([len(x) for x in helixTestPlanToReport.keys()]) + 4
    for mod in sorted(helixTestPlanToReport.keys()):
        total, numOfNotPassed = statModuleDuration(helixTestPlanToReport, mod, bsp=None)
        totalAll += total
        print('%s\t%s\t%s' % (mod + ' ' * (maxModLen - len(mod)), total, numOfNotPassed))
    
    print('module #=%s, total=%s, per node=%.1f hours' % (len(helixTestPlanToReport), totalAll, totalAll/3.0/3600.0))
    

def calculateDeviation(totals):
    avg = sum(totals) / len(totals)
    dt = 0.0
    for v in totals:
        d = abs(v - avg)
        dt += d
    return dt


def assignModule2Bsp(numBsp, helixTestPlanToReport):
    numOfDetermined = 20
    modDurations = []
    
    totalAll = 0
    for mod in sorted(helixTestPlanToReport.keys()):
        total, numOfNotPassed = statModuleDuration(helixTestPlanToReport, mod, bsp=None)
        modDurations.append( (mod, total) )
    
    currentGroupModDurations = []
    currentTotals = []
    currentDeviation = 0
    for _ in xrange(numOfDetermined):    
        groupModDurations, totals = distributeModDurations(numBsp, modDurations)
        deviation = calculateDeviation(totals)
        print('=== %s, %s' % (totals, deviation))
        if currentDeviation == 0:
            currentDeviation = deviation
            currentTotals = totals
            currentGroupModDurations = groupModDurations
        if deviation < currentDeviation:
            currentDeviation = deviation
            currentTotals = totals
            currentGroupModDurations = groupModDurations

    return currentGroupModDurations, currentTotals    
    

def distributeModDurations(numBsp, modDurations):
    groupModDurations = []
    for i in xrange(numBsp):
        groupModDurations.append([])

    modDurations = sorted(modDurations, key=itemgetter(1), reverse=True)
    for i in xrange(len(modDurations)):
        j = random.randint(0,2)
        groupModDurations[j].append(modDurations[i])

    totals = []
    for groups in groupModDurations:
        total = sum([x[1] for x in groups])
        totals.append(total)

    return groupModDurations, totals
            
    
def find_best_module_distribution_among_bsp():
    numBsp = len(helixSupportedBsps)
    
    modConfig = moduleDurationFile
    sys.path.insert(0, os.path.dirname(modConfig))
    from modDuration import helixTestPlanToReport

    distributedBspMods, totals = assignModule2Bsp(numBsp, helixTestPlanToReport)
    pp = pprint.PrettyPrinter(indent=2, width=100)    
    pp.pprint(distributedBspMods)
    pp.pprint('%s, %s' % (totals, calculateDeviation(totals)))


moduleDistributedToBsps = [ [ (u'IKE-ADVANCED', 3399.0),
    (u'IPNET', 3145.0),
    (u'NTP', 1954.0),
    (u'IKE', 1857.0),
    (u'ROHC_IP', 374.0),
    (u'CORE_SAFETY', 368.0),
    (u'SSH', 358.0),
    (u'VRRP', 347.0),
    (u'ROHC_UDP', 309.0),
    (u'MCP', 271.0),
    (u'SSHCLIENT', 252.0),
    (u'QOS', 184.0),
    (u'FTP', 96.0),
    (u'IPNET-IPSEC', 96.0),
    (u'RADIUS', 75.0),
    (u'DNSC', 32.0),
    (u'NET_VLAN', 8.0),
    (u'SECEVENT', 0.0),
    (u'USERAUTH_LDAP', 0.0)],
  [ (u'IKE-DAEMON', 2903.0),
    (u'IKE-BASIC', 2750.0),
    (u'IKE-ALGORITHMS', 2290.0),
    (u'IPSEC-IPCRYPTO', 2154.0),
    (u'FIREWALL', 1205.0),
    (u'IKE-ROHC-IPSEC', 740.0),
    (u'SCTP', 527.0),
    (u'SYSVIEW', 382.0),
    (u'IKE-IPEAP', 331.0),
    (u'RIPNG', 124.0),
    (u'RIP', 60.0)],
  [ (u'DHCP', 1825.0),
    (u'NAT', 1564.0),
    (u'IKE-SETTINGS', 1555.0),
    (u'SNTP_CLIENT', 1443.0),
    (u'IKE-AUTHENTICATION', 1262.0),
    (u'ROHC_TCP', 1253.0),
    (u'SNTP_SERVER', 1030.0),
    (u'PPP', 582.0),
    (u'DHCP6', 506.0),
    (u'SNMP', 378.0),
    (u'IKE-RACOON', 306.0),
    (u'SSL', 277.0),
    (u'CRYPTO', 261.0),
    (u'ROHC_ESP', 209.0),
    (u'L2TP', 175.0),
    (u'ROHC_UNCMP', 156.0),
    (u'USERDB', 12.0),
    (u'TFTP', 10.0)]]

#'[13125.0, 13466.0, 12804.0], 668.666666667'

def create_helixTestPlanToReport():
    # output helixBuildModules
    if True:
        i = 0
        for groups in moduleDistributedToBsps:
            bsp = helixSupportedBsps[i]
            print('\'%s\' : (' % bsp)
            for module, duration in sorted(groups, key=itemgetter(0)):
                    print('%s\'%s\',' % (' '*10, module))
            print('         ),')
            i += 1
    print('\n\n')
    # output helixTestPlanToReport
    if True:
        modConfig = moduleDurationFile
        sys.path.insert(0, os.path.dirname(modConfig))
        from modDuration import helixTestPlanToReport
        
        print('helixTestPlanToReport = {')
        for module in sorted(helixTestPlanToReport.keys()):
            print('%s\'%s\' : {' % (' '*4, module))
            for testName in sorted(helixTestPlanToReport[module]):
                print('%s\'%s\' : \'Blocked\',' % (' '*10, testName))
            print('           },')
        print('}')


def verifyHelixTestPlanToReport():
    from HelixConfig import helixTestPlanToReport
    total = 0
    for mod in sorted(helixTestPlanToReport.keys()):
        print('\n%s' % mod)
        for test in sorted(helixTestPlanToReport[mod]):
            print('\t%s' % test)
            total += 1
    print('total %s test cases' % total)
    
    
if __name__ == '__main__':    
    main()
    #statistic_test_duration_by_module()
    #find_best_module_distribution_among_bsp() # use 1st
    #create_helixTestPlanToReport()
    #verifyHelixTestPlanToReport()
    