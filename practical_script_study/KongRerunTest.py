#!/usr/bin/env python

# TO-DO :
#    1) not cover the case below
#ipnet.windview.udp                        FAILED
#ipnet.windview.udp - IPv4 ETA: 1s                                           ipnet.windview.udp test case failed  failed
#ipnet.windview.udp - IPv6 ETA: 1s                                           OK 1s
#
#    2) not consider extracting the skipped test cases

import re, time
from sys import exit
from operator import itemgetter

from Jenkins import *
from Git import *
from Mail import *
from Config import *
from KongConfig import *
from KongJenkins import GetModTCBspFromLog, ParseBsp, ParseModule
from KongTestPlanToReport import kongTestPlanToReport
from KongTestSuite import ExtractItem

jenkinsWeb = 'http://pek-testharness-s1.wrs.com:8080'
user = 'svc-cmnet'
password='december2012!'


def AnalyzeJenkinsTestResult(project, build, jenkinsWeb, debug = False):
    # testResults = [(testName1, 'Pass'), (testName2, 'Fail'), ...]
    content = GetBuildConsole(jenkinsWeb, project, build, user, password)
    bsp = ParseBsp(content)
        
    try:
        testResults = ParseTestResult(content)
        ts1 = CategorizeTestCaseResult(testResults)
        ts2 = ExtractTestSummary(content)
        if ts1 != ts2:
            #print '== self summary is %s while log summary is %s' % (ts1, ts2)
            pass
        if debug:
            if ts1 != ts2:
                print 'WARINING: self summary:%s not equal to log summary:%s' % (ts1, ts2)
    except:
        testResults = []
    return testResults, bsp


def ParseTestResult(content):
    allTestCaseResults = GetAllTestResultList(content)
    failedTestCaseResults = GetFailedTestResultList(content)
    skippedTestCaseResults = GetSkippedTestResultList(content)
    testCaseResults = CombineTestResult(allTestCaseResults, failedTestCaseResults)
    testCaseResults = CombineTestResult(testCaseResults, skippedTestCaseResults)
    return testCaseResults


def GetAllTestResultList(content):
    rets = []
    rawTestResult = FindRawTestResult(content)
    testCaseRawStrs = SplitRawTestResult(rawTestResult)
    for oneTestCaseStr in testCaseRawStrs:
        testName, testResult = ParseOneTestCaseResult(oneTestCaseStr)
        if testResult is not None: # None means that the testName is not valid, so remove it
            rets.append((testName, testResult))
    return rets


def GetFailedTestResultList(content):
    rets = []
    rFailed = re.search('(?s)Failed tests:(.*?)\n\n', content)
    if rFailed is not None:
        failedTestResult = rFailed.groups()[0]
        tests = [ x for x in failedTestResult.split('\n') if x != '' ]
        for test in tests:
            testName = test.split(' ')[0].strip()
            testVersion = '4'
            if len([x for x in test.split(' ') if x.strip()]) == 2:
                testVersion = test.split(' ')[1]
            rets.append((testName + ' - IPv%s' % testVersion, 'FAILED'))
    return rets


def GetSkippedTestResultList(content):
    rets = []
    r = re.search('(?s)\*\* CONFIGURATION 0 vxsim0,vxsim1,vxsim2,vxsim3,vxsim4,vxsim5 \*\*(.*?)Total ETA:', content)
    if r is not None:
        rawSkippedTestResult = r.groups()[0].strip()
        tests = [ x for x in rawSkippedTestResult.split('\n') if x != '' ]
        for test in tests:
            if test.find(' ') != -1:    # defensive check to avoid silent quitting or exception
                testName = test.split(' ')[2].strip()
            else:
                testName = ''
            if IsKongTestCaseName(testName):
                rets.append((testName, 'SKIPPED'))     
    return rets


def CombineTestResult(testResultList1, testResultList2):
    """ if testName2 in testName1, then duplicated """
    for (testName2, testResult2) in testResultList2:
        for (testName1, testResult1) in testResultList1:
            if testName1.startswith(testName2):
                if testResult2.lower() == testResult1.lower():
                    i = testResultList2.index((testName2, testResult2))
                    testResultList2[i] = (testName2, 'duplicated')
            """
            if testName1 == (testName2 + ' - IPv4'):
                if testResult2.lower() == testResult1.lower():
                    i = testResultList2.index((testName2+' - IPv4', testResult2))
                    testResultList2[i] = (testName2+' - IPv4', 'duplicated')
            if testName1 == (testName2 + ' - IPv6'):
                if testResult2.lower() == testResult1.lower():
                    i = testResultList2.index((testName2+' - IPv6', testResult2))
                    testResultList2[i] = (testName2+' - IPv6', 'duplicated')
            """
    return testResultList1 + [(n, r) for (n, r) in testResultList2 if r != 'duplicated']



def FindRawTestResult(content):   
    # '(?s)Total ETA: .*?20\d\d\)(.*?)rounds:' find the first section
    # while '(?s)Total ETA: .*20\d\d\)(.*?)rounds:' finds the second section one if there is any failed test cases
    r = re.search('(?s)Total ETA: .*?20\d\d\)(.*?)rounds:', content)
    if r is not None:
        return r.groups()[0]
    else:
        raise 'ERROR: cannot find Kong raw test result'
    
    
def SplitRawTestResult(rawTestResult):
    """ return a list, each element is a string for one test case result """
    testCaseRawResults = []
    oneTestCase = []
    hasInterrupedTestName = False

    rawTestResult = PreContentHandler(rawTestResult) 

    if rawTestResult.find('ETA') == -1:
        return []
        
    for line in [x for x in rawTestResult.split('\n') if x != '']:
        if line.find('ETA') != -1:
            if oneTestCase == []:
                oneTestCase = [line]
            else: 
                testCaseRawResults.append('\n'.join(oneTestCase))
                oneTestCase = [line]
            if not IsKongTestCaseName(line.split(' ')[0]):
                hasInterrupedTestName = True
        else:
            oneTestCase.append(line)
    testCaseRawResults.append('\n'.join(oneTestCase)) # last one test case
    if hasInterrupedTestName:
        testCaseRawResults = SplitInterruptedRawTestResult(rawTestResult, testCaseRawResults)
    return testCaseRawResults


def PreContentHandler(rawTestResult):
    # handle the following exception printed within test results
    # Exception OSError: (9, 'Bad file descriptor') in <bound method spawn.__del__ of <pexpect.spawn instance at 0x1cc5d88>> ignored
    exceptPtn = 'Exception OSError:(.*?)ignored'
    founds = re.findall(exceptPtn, rawTestResult)
    if founds:
        for found in founds:
            middleStr = found
            if (middleStr.find('Bad file descriptor') != -1) and \
               (middleStr.find('bound method spawn.__del__ of') != -1) and \
               (middleStr.find('pexpect.spawn instance at') != -1):
                wholeStr = 'Exception OSError:' + middleStr + 'ignored\n'
                rawTestResult = rawTestResult.replace(wholeStr, '')
    return rawTestResult

    
def SplitInterruptedRawTestResult(rawTestResult, testCaseResults):
    tests = [ParseOneTestCaseResult(x) for x in testCaseResults]
    tests = [x for x in tests if x[1] is not None]
    interrupredTestNames = FindInterruptedTestName(testCaseResults)
    if len(interrupredTestNames) != 1:
        raise BaseException('ERROR num of interrupted test name =', len(interrupredTestNames))
    product = tests[0][0].split('.')[0]
    for x in testCaseResults:
        if not x.startswith(product):
            i = testCaseResults.index(x)
            testCaseResults[i] = interrupredTestNames[0] 
    return testCaseResults


def FindInterruptedTestName(testCaseResults):
    """ return a list, each element is a string for raw test result """
    rets = []    
    for x in testCaseResults:
        if not IsKongTestCaseName(x.split('ETA:')[0].strip()):
            i = testCaseResults.index(x)
            if x.find('ETA:') != -1:
                rets.append( testCaseResults[i-1] + '\n' + testCaseResults[i] )
    rawStrings = []
    for x in rets:
        tokens = x.split('\n')
        for t in tokens:
            if re.search('OK|failed|skipped', t) is not None:
                i = tokens.index(t)
                rawStrings.append( '\n'.join(tokens[i+1:]) )
                break
    # specific to Exception OSError:
    names = []
    for rawStr in rawStrings:
        lines = rawStr.split('\n')
        i = lines[0].find('Exception OSError:')
        if i != -1:
            j, _ = FindInList(lines, 'ETA:')
            if j is not None:
                name1 = lines[0][0:i]
                name2 = '\n'.join(lines[j:])
                names.append(name1 + name2)
            else:
                raise 'ERROR cannot find ETA in', rawStr
        else:
            names.append(rawStr)
    return names


def FindInList(theList, theKeyword):
    """ return i, element """
    rets = (None, None)
    for x in theList:
        if x.find(theKeyword) != -1:
            return (theList.index(x), x)
    return rets
    

def ParseOneTestCaseResult(testCase):
    testResult = None
    tokens = testCase.split('ETA:')
    testName = tokens[0].strip()
    if testCase.find('ETA:') == -1:
        return testCase, None
    resultTokens = [x.strip() for x in tokens[1].replace('\n', ' ').split(' ') if x != '']

    for lastToken in resultTokens:  # handle tokens from left to right
        if lastToken in ['OK', 'failed', 'skipped', 'OKException']:
            if lastToken == 'OKException':
                testResult = 'OK'
            else:
                testResult = lastToken
            break
    
    return testName, testResult


def CategorizeTestCaseResult(testCaseResults):
    assert type(testCaseResults) == list
    ok, failed, skipped = 0, 0, 0
    for (_, testResult) in testCaseResults:
        result = testResult.lower()
        if result == 'ok':
            ok = ok + 1
        elif result == 'failed':
            failed = failed + 1
        elif result == 'skipped':
            skipped = skipped + 1
        else:
            raise 'ERROR: unknow test result:', testResult
    return ok, failed, skipped

    
def ExtractTestSummary(content):
    """ return (ok, failed, skipped) """
    # rounds: 1.  tests_ok: 13.  tests_fail: 4.  tests_skipped: 2.
    ptnSummary = '(?s)rounds:(.*?)\n\n'
    f = re.search(ptnSummary, content)
    if f is not None:
        r = f.groups()[0]
        ok = re.search('tests_ok: (.*?)\.', r).groups()[0]
        failed = re.search('tests_fail: (.*?)\.', r).groups()[0]
        skipped = re.search('tests_skipped: (.*?)\.', r).groups()[0]
        return (int(ok), int(failed), int(skipped))
    else:
        return 'ERROR: cannot find Kong test result'
    
            
def IsKongTestCaseName(testCaseName):
    kongTestNameModules = ('vrrp', 
                           'qos', 
                           'send', 
                           'sshclient', 
                           'userauthldap', 
                           'rtnet', 
                           'snmp', 
                           'openssl_fips',
                           'core_safety',
                           'edoom',
                           '8021x',
                           'socktest',
                           'bond',
                           'iprohc_ip')
    if not (testCaseName.startswith('ip') or testCaseName.split('.')[0] in kongTestNameModules):
        return False
    if testCaseName.count('.') not in (2, 3):
        return False
    return True
     

def SelectTestResults(testResults, testFilter):
    # testResults = [ (testName, 'OK'), (testName2, 'FAILED'), (testName3, 'failed'), ... ]
    assert type(testResults) == list
    assert testFilter in ('pass', 'fail', 'skip')
    iptestengineResults = { 'pass' : 'ok',
                            'fail' : 'failed',
                            'skip' : 'skipped',
                          }
    return filter(lambda x: x[1].lower() == iptestengineResults[testFilter], testResults)
    
    
class JobTestResult(object):
    def __init__(self, jobName, buildId):
        self.job = jobName
        self.build = buildId
        self.passTests = []
        self.failTests = []
        self.mod = None
        self.bsp = None
        self.__ParseJobTest(self.job, self.build)
    
    def __ParseJobTest(self, jobName, buildId):
        try:
            testResults, bsp = AnalyzeJenkinsTestResult(self.job, self.build, jenkinsWeb)
            self.passTests = SelectTestResults(testResults, 'pass')
            self.failTests = SelectTestResults(testResults, 'fail')
            # must use ParseModule() instead of GetModName()
            self.mod = ParseModule(GetBuildConsole(jenkinsWeb, self.job, self.build, user, password))
            self.bsp = bsp
        except:
            print '=== EXCEPTION when analyzing project %s build %s test result' % (self.job, self.build)
            testResults = []
    
    def GetJobName(self):
        return self.job
    
    def GetBuildId(self):
        return self.build

    def GetMod(self):
        return self.mod
        
    def GetBsp(self):
        return self.bsp
    
    def GetPassTests(self):
        return self.passTests
    
    def GetFailTests(self):
        return self.failTests
    
    def __str__(self):
        return 'job=%s, ' % self.job + \
               'build=%s ' % self.build + \
               'mod=%s ' % self.mod + \
               'bsp=%s ' % self.bsp + \
               'passTests#=%s ' % len(self.passTests) + \
               'failTests#=%s ' % len(self.failTests)
               

def GetRunTestJobBuild(jenkinsWeb, multiJobName, multJobBuildId):
    jobBuilds = GetJobBuildsFromMultiJob(jenkinsWeb, multiJobName, multJobBuildId, user, password)
    return filter( lambda x: x[0].startswith(kongTestJobPrefix), sorted(jobBuilds, key=itemgetter(0)) )


def GetJobTestResult(jobBuilds):
    # testResults = { 'bsp1' : { 
    #                          'mod1' : [ (job1, build1, passedTestsList, failedTestsList),
    #                                     (job2, build2, passedTestsList, failedTestsList),
    #                                   ], 
    #                          'mod2' : [ JobTestResult1, JobTestResult2, ],
    #                          ...
    #                          },
    #               }
    testResults = {}
    for job, build in jobBuilds:
        jts = JobTestResult(job, build)
        mod = jts.GetMod()
        bsp = jts.GetBsp()
        InitDictionary(testResults, bsp, mod)
        testResults[bsp][mod].append( (job, build, jts.GetPassTests(), jts.GetFailTests()) )
    return testResults


def CreateRerunTest(testResults, predefinedTestResults):
    # rerunTests = { 'bsp1' : { 
    #                          'mod1' : failedTestsList, 
    #                          'mod2' : failedTestsList,
    #                          ...
    #                         },
    #              } 
    mergedTestResults = MergeJobTestResult(testResults)
    return CompareToPredefinedTests(mergedTestResults, predefinedTestResults)


def MergeJobTestResult(testResults):
    # retTestResults = { bsp1 : { mod1 : testResultsList (including both passed and failed), 
    #                             mod2: ..., ...}, 
    #                    bsp2 : {}, }
    retTestResults = {}
    for bsp in testResults:
        for mod in testResults[bsp]:
            InitDictionary(retTestResults, bsp, mod)
            totalPassTests, totalFailTests = [], []
            for _, _, passTests, failTests in testResults[bsp][mod]:
                totalPassTests = totalPassTests + passTests
                totalFailTests = totalFailTests + failTests
            newPassTests, newFailTests = MergePassFailTests(GetUniquePairs(totalPassTests), 
                                                            GetUniquePairs(totalFailTests))
            retTestResults[bsp][mod] = GetUniquePairs(newPassTests + newFailTests)
    return retTestResults


def MergeTestResult(testResults1, testResults2):
    # union of both testResults which comes from GetJobTestResult()
    # retTestResults = { bsp1 : { mod1 : testResultsList, mod2: ..., ...}, bsp2 : {}, }
    def FindUnion(list1, list2):
        return list( set(list1).union(set(list2)))
    
    mergedTestResults1 = MergeJobTestResult(testResults1)
    mergedTestResults2 = MergeJobTestResult(testResults2)
    retTestResults = mergedTestResults1.copy()
    unionBsps = FindUnion(mergedTestResults1, mergedTestResults2)
    
    for bsp in unionBsps:
        if bsp in retTestResults and bsp in mergedTestResults2:
            unionMods = FindUnion(retTestResults[bsp].keys(), mergedTestResults2[bsp].keys())
            for mod in unionMods:
                if mod in retTestResults[bsp] and mod in mergedTestResults2[bsp]:
                    retTestResults[bsp][mod] = GetUniquePairs(retTestResults[bsp][mod] + mergedTestResults2[bsp][mod])
                elif mod in retTestResults[bsp] and mod not in mergedTestResults2[bsp]:
                    continue
                elif mod not in retTestResults[bsp] and mod in mergedTestResults2[bsp]:
                    retTestResults[bsp][mod] = mergedTestResults2[bsp][mod]
        elif bsp in retTestResults and bsp not in mergedTestResults2:
            continue
        elif bsp not in retTestResults and bsp in mergedTestResults2:
            retTestResults[bsp] = mergedTestResults2[bsp]
    
    return retTestResults
    
        
def MergePassFailTests(passedTests, failedTests):
    def FindCommon(list1, list2):
        return list( set(list1).intersection(set(list2)) )
    
    def RemoveTest(testResults, testNames):
        keys = set(testNames)
        return [x for x in testResults if x[0] not in keys]
    
    passedUniques = GetUniquePairs(passedTests)
    failedUniques = GetUniquePairs(failedTests)
    
    passedTestNames = [x[0] for x in passedUniques]
    failedTestNames = [x[0] for x in failedUniques]
    commonTestNames = FindCommon(passedTestNames, failedTestNames)
    
    failedTests = RemoveTest(failedUniques, commonTestNames)
    return passedUniques, failedTests


def RerunTest(branch, commit, rerunTests, debugReruns=None):
    if kongRerunFlag:
        print '=== starting rerun test at %s' % time.asctime()
        if debugReruns is not None:
            print 'DEBUG: using debugging reruns'

        DebugOutput(rerunTests)

        if debugReruns is None:
            reruns = LaunchRerunTest(branch, commit, rerunTests)
        else:
            reruns = debugReruns
        print '\n=== reruns:', reruns

        runningJobs = GetJobNames(reruns)
        print '\n=== runningJobs:', runningJobs
        
        if debugReruns is None:
            time.sleep(10)   # wait for a while before QueryBuildRunning()
            
            for job in runningJobs:
                while QueryBuildRunning(jenkinsWeb, job, user, password):
                    time.sleep(60)
            
        print '=== ending rerun test at %s' % time.asctime()
    else:
        print '=== skipping rerun test'
        reruns = {}
    return reruns


def GetRerunTestCases(jenkinsWeb, multiJobProject, build):
    # rerunTests = { 'bsp1' : { 
    #                          'mod1' : [ buildList, passedTestsList, failedTestsList ], 
    #                          'mod2' : [ buildList, passedTestsList, failedTestsList ],
    #                          ...
    #                         },
    #              } 
    rerunTests = {}
    
    jobBuilds = GetJobBuildsFromMultiJob(jenkinsWeb, multiJobProject, build, user, password)
    utJobBuilds = [x for x in sorted(jobBuilds, key=itemgetter(0)) if x[0].startswith(kongTestJobPrefix)]
    for project, build in utJobBuilds:
        testCases = []
        try:
            testResults, bsp = AnalyzeJenkinsTestResult(project, build, jenkinsWeb)
        except:
            print '=== EXCEPTION when analyzing project %s build %s test result' % (project, build)
            testResults = []
        if bsp not in rerunTests:
            rerunTests[bsp] = {}
        testCases = testCases + testResults
        passedTestCases = filter(lambda x: x[1].lower() == 'ok', testCases)
        failedTestCases = filter(lambda x: x[1].lower() == 'failed', testCases)

        mod = GetModName(project)
        if mod not in rerunTests[bsp]:
            rerunTests[bsp][mod] = [[build], passedTestCases, failedTestCases]
        else:
            rerunTests[bsp][mod][0].append(build)
            if passedTestCases:
                rerunTests[bsp][mod][1].extend(passedTestCases)
            if failedTestCases:
                rerunTests[bsp][mod][2].extend(failedTestCases)

    return CompareToPredefinedTests(rerunTests)


def CompareToPredefinedTests(rerunTests, kongTestPlanToReport=kongTestPlanToReport):
    # retRerunTests = { bsp1 : { mod1 : failedTestResultsList, mod2 : ...}, bsp2 : {}, ...}
    # note: use passed tests to compare with predefined tests so that the blocked tests can be rerun
    retRerunTests = {}
    for bsp in rerunTests:
        for mod in rerunTests[bsp]:
            if mod in kongTestPlanToReport[bsp]:
                passedTests = SelectTestResults(rerunTests[bsp][mod], 'pass')
                failedTestNames = set( [x[0] for x in SelectTestResults(rerunTests[bsp][mod], 'fail')] )
                notPassedTestNames = GetNotPassedTest(kongTestPlanToReport[bsp][mod], passedTests)
                if notPassedTestNames:
                    notPassed2DotTestNames = list( set( [ChangeTo2DotTestName(x) for x in notPassedTestNames] ) )
                    InitDictionary(retRerunTests, bsp, mod)
                    for tn in sorted(notPassed2DotTestNames):
                        if tn in failedTestNames:
                            retRerunTests[bsp][mod].append( (tn, 'failed') )
                        else:
                            retRerunTests[bsp][mod].append( (tn, 'blocked') )
    return retRerunTests


def GetNotPassedTest(predefinedModTestDict, passedTests):
    passedTestNames = [x[0] for x in passedTests]
    predefinedTestNames = predefinedModTestDict.keys()
    return sorted( list( set(predefinedTestNames).difference( set(passedTestNames) ) ) )

    
def ChangeTo2DotTestName(testName):
    # testName : a.b.c[.d] - IPv4
    testName = testName.replace(' ', '')
    if '-IPv' in testName:
        testCase  = testName.split('-IPv')[0].strip()
        ipVersion = testName.split('-IPv')[1].strip()
        plasticName = '.'.join( testCase.split('.')[0:3] ) + ' - IPv' + ipVersion
        # return '.'.join( testCase.split('.')[0:3] ) + ' - IPv' + ipVersion
    else:
        plasticName = testName
    return plasticName

def InitDictionary(theDict, bsp, mod):
    assert type(theDict) == dict
    if bsp not in theDict:
        theDict[bsp] = {}
    if mod not in theDict[bsp]:
        theDict[bsp][mod] = []
        

def GetUniquePairs(thePairs):
    retPairs = {}
    for testName, testResult in thePairs:
        if testName not in retPairs:
            retPairs[testName] = (testName, testResult)
        else:
            if retPairs[testName][1] == testResult:
                continue
            else:
                # same test name with different test results
                if retPairs[testName][1].lower() == 'ok':
                    continue
                else:
                    print '|NOTE|: test name "%s" uses optimal test result "%s"' % (testName, testResult)
                    retPairs[testName] = (testName, testResult)
    pairList = retPairs.values()
    return sorted(pairList, key=itemgetter(0))

                
def MergeWithRerunTests(rerunTests, project, testResultMap):
    # merge kongProjectTest with rerunTests, which has (buildId, [(test1, result1), (test2, result2), ...])
    if len(testResultMap) != 0:
        rerunTestDict = ListToDict(rerunTests[project][2])  # failed tests
        tests = set( testResultMap.keys() )
        diffTests = tests.difference( set( rerunTestDict.keys() ) )
        for diffTest in diffTests:
            rerunTestDict[diffTest] = 'blocked'
        testList = DictToList(rerunTestDict)
        
        build = rerunTests[project][0]
        passedTests = rerunTests[project][1]
        failedTests = testList
        rerunTests[project] = (build, passedTests, failedTests)

    return rerunTests


def FindCommonTestCase(testCases):
    # combine a.b.c.d to a.b.c test cases
    modFileTests = ['.'.join(x.split('.')[0:3]) for x in testCases]
    return sorted( list( set(modFileTests) ) )
    
    
def ListToDict(theList):
    """ theList, with each element (a, b) """
    rets = {}
    for a, b in theList:
        rets[a] = b
    return rets


def DictToList(theDict):
    """ theDict, with each element theDict[a] = b """
    rets = []
    for k in theDict:
        rets.append( (k, theDict[k]) )
    return rets    
    

def test_ListToDict():
    theList = [(u'ipnet.frag.drop - IPv4', u'OK'), (u'ipnet.frag.drop - IPv6', u'OK')]
    theDict = ListToDict(theList)
    newList = DictToList(theDict)
    if theList == newList:
        print 'PASS'
    else:
        print 'FAIL'
        
            
def DebugOutput(rerunTests):
    for bsp in rerunTests:
        print '\nBSP=', bsp
        print '\tModules that not 100% passed'
        for mod in sorted(rerunTests[bsp].keys()):
            print '\t\t%s: failed #:%s, failed tests:%s\n' % (mod, len(rerunTests[bsp][mod]), rerunTests[bsp][mod])
        print '\tThe following modules will be rerun testing'
        for mod in sorted(rerunTests[bsp].keys()):
            print '\t\t%s' % mod


def ApplyRerunPolicy(rerunTests):
    plannedRerunTests = {}
    for job in rerunTests:
        build = rerunTests[job][0]
        passedTests = rerunTests[job][1]
        failedTests = rerunTests[job][2]
        if passedTests == []:
            plannedRerunTests[job] = (build, passedTests, failedTests)
        elif failedTests != []:
            if kongRerunFailedJob:
                plannedRerunTests[job] = (build, passedTests, failedTests)
    return plannedRerunTests


def OptimizeJobSequence(rerunTestsForOneBsp):
    # have to optimize the job running sequence due to vm # is greater than rm #
    vmJobs = [job for job in rerunTestsForOneBsp if kongTestServers.get( GetModName(job), 'ci-rerun-test') != 'ci-rerun-test-rm']        
    rmJobs = [job for job in rerunTestsForOneBsp if kongTestServers.get( GetModName(job), 'ci-rerun-test') == 'ci-rerun-test-rm']
    return vmJobs + rmJobs
 

def LaunchRerunTest(branch, commit, rerunTests):
    # reruns = {bsp1 : { mod1 : [ (rerunJob1, rerunBuild1), (rerunJob2, rerunBuild2), ...], 
    #                    mod2 : ...}, 
    #           bsp2 : {}, }
    reruns = {}
    print 'rerun times:%s' % kongRerunTestNum
    for bsp in rerunTests:
        for mod in OptimizeJobSequence(rerunTests[bsp]):
            InitDictionary(reruns, bsp, mod)
                
            failedTests = rerunTests[bsp][mod]
            if failedTests:
                # handle duplicated test cases such as a.b.c-IPv4, a.b.c-IPv6 
                # and 3-dot test cases like mod.file.testcase.subtestcase in RTNET module
                commonTestCases = FindCommonTestCase( [GetTestCaseName(x[0]) for x in failedTests] )
                tc = ','.join( commonTestCases )
            server = kongTestServers.get(mod, 'ci-rerun-test')
            
            for i in range(kongRerunTestNum):
                rerunJob, rerunBuild = LaunchTestJob(server, branch, commit, mod, tc, bsp)
                if i == 0:
                    reruns[bsp][mod] = [ (rerunJob, rerunBuild) ]
                    if bsp in [x for x in GetSupportedBsps() if x != 'vxsim_linux']:
                        print 'rerun 1 time on VLM targets'
                        break
                    if server == 'ci-rerun-test-rm': # real machine: now only 1 so only running 1 time
                        print 'rerun 1 time on the only 1 real machine pek-testharness-s1.wrs.com'
                        break
                else:
                    reruns[bsp][mod].append( (rerunJob, rerunBuild) )
    return reruns


def GetModName(jobName):
    mod = jobName.replace(kongTestJobPrefix, '')
    if mod == 'CRYPTO-FIPS-140-2':
        return mod
    if re.search('-\d+$', mod):
        ts = mod.split('-')
        return RemoveBspName('-'.join(ts[0:-1]))
    else:
        return RemoveBspName(mod)


def RemoveBspName(jobName):
    # ut-vxsim-RTNET-fsl_imx6 instead of ut-vxsim-RTNET-fsl_imx6-1
    fields = jobName.split('-')
    for bsp in GetSupportedBsps():
        if bsp in fields:
            fields.remove(bsp)
            return '-'.join(fields)
    return '-'.join(fields)


def GetTestCaseName(testResultName):            
    return testResultName.split(' - ')[0].strip()
         
    
def LaunchTestJob(server, branch, newCommit, module, testCase, bsp='vxsim_linux'):
    """ testCase is a string containing multiple test cases """
    # must run as svc-cmnet at pek-cc-pb02l since using user ssh authentication
    cmd = 'java -jar /net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/package/jenkins-cli.jar -s %s build %s \
          -p BRANCH=%s -p COMMIT=%s -p MODULE=%s -p TESTCASE=%s -p BSP=%s -v -w --username %s --password %s' % (jenkinsWeb, server, branch, newCommit, module, testCase, bsp, kongUser, kongPassword)
    print '\n%s @ %s' % (cmd, time.asctime())
    ret = getoutput(cmd)
    print ret
    lastLine = ret.split('\n')[-1].strip()
    if lastLine.startswith('Started '):
        words = lastLine.split(' ')
        return words[1], int(words[2].replace('#', ''))
    else:
        return server, None
    

def GetJobNames(reruns):
    # reruns = {bsp1 : { mod1 : [ (rerunJob, rerunBuild), (rerunJob2, rerunBuild2), ...], 
    #                    mod2 : ...}, }, 
    #           bsp2 : {}, }
    rerunJobs = []
    for bsp in reruns:
        for mod in reruns[bsp]:
            for job, _ in reruns[bsp][mod]:
                if job not in rerunJobs:
                    rerunJobs.append(job)
    return sorted(rerunJobs)


def CombineMultiJobTestResult(jobBuildDict):
    # jobBuildDict: {bsp1 : { mod1 : [ (job, build), ... ], mod2 : [...], }, ...}
    # testCases = {bsp1 : { mod1 : [ (testName, testResult), ... ], mod2 : [...], }, ...}
    testCases = {}
    for bsp in jobBuildDict:
        if bsp not in testCases:
            testCases[bsp] = {}
            
        for mod in jobBuildDict[bsp]:
            for job, build in jobBuildDict[bsp][mod]:
                tcs, _ = AnalyzeJenkinsTestResult(job, build, jenkinsWeb)
                mod = GetModName(job)
                if mod not in testCases[bsp]:
                    testCases[bsp][mod] = []
                testCases[bsp][mod] = testCases[bsp][mod] + tcs
    return CombineTestResultPairs(testCases)


def CombineTestResultPairs(testcaseResultPairs):
    # testCases = {bsp1 : { mod1 : [ (testName, testResult), ... ], mod2 : [...], }, ...}
    retPairs = []
    sortedPairs = sorted(testcaseResultPairs, key=itemgetter(0))
    length = len(sortedPairs)
    i = 0
    while i < length:
        tname, tresult = sortedPairs[i]
        if tresult is None:
            tresult = 'none'
        j = i + 1
        while j < length:
            tnNext, trNext = sortedPairs[j]
            if tname.lower() == tnNext.lower():
                tname, tresult = Combine2TestResult( tname, tresult, tnNext, trNext )
            else:
                break
            j += 1
        i = j
        retPairs.append( (tname, tresult) )                
    return retPairs


def Combine2TestResult(tn1, tr1, tn2, tr2):
    if tr1 is None:
        tr1 = 'none'
    if tr2 is None:
        tr2 = 'none'
        
    if tn1.lower() == tn2.lower():
        if tr1.lower() == 'ok':
            return tn1, tr1
        else:
            if tr2.lower() == 'ok':
                return tn1, tr2
            else:
                if tr1.lower() != tr2.lower():
                    print 'ERROR: the same test case %s with different test result: %s vs. %s' % (tn1, tr1, tr2)
                return tn1, tr1
    else:
        return tn1, tr1
    
    
def main():
    if len(sys.argv) != 4:
        print 'usage: %s ci-summary-build-id branch commit' % (os.path.basename(sys.argv[0]))
        exit(1)
        
    multiJobProject = 'ci-manager'
    jobName = 'ci-summary'
    buildId = int(sys.argv[1])
    branch = sys.argv[2]
    commit = sys.argv[3]

    parentBuildId = GetParentBuildIdFromMultiJob(jenkinsWeb, multiJobProject, jobName, buildId, user, password)
    reruns = RerunTest(jenkinsWeb, multiJobProject, parentBuildId, branch, commit)
    print reruns
    
    
if __name__ == '__main__':
    main()
