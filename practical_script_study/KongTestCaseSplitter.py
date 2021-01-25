#!/usr/bin/env python

import re, time, collections, sets, commands, os
from sys import exit
from operator import itemgetter

from Jenkins import *
from Git import *
from Mail import *
from Config import *
from KongConfig import *
from KongRerunTest import AnalyzeJenkinsTestResult

jenkinsWeb = 'http://128.224.159.246:8080'
user = 'svc-cmnet'
password='december2012!'

def GetTestCases(jenkinsWeb, job, build):
    try:
        testResults, _ = AnalyzeJenkinsTestResult(job, build, jenkinsWeb)
    except:
        testResults = []
    return testResults


def GetOneTestCaseDuration(testCase, consoleHtml):
    testName = testCase[0]
    testResult = testCase[1]
    if testResult.lower() in ['failed', 'skipped']:
        return (testName, testResult, 0)
    durationPtn = '(?s)%s.*?%s (.*?)\n' % (testName, testResult)
    #print durationPtn
    found = re.search(durationPtn, consoleHtml)
    if found:
        #print found.groups()
        duration = Convert2Sec(found.groups()[0])
        return (testName, testResult, duration)
    else:
        return (testName, testResult, -1)

    
def Convert2Sec(durationString):
    """ durationString : Xm Ys"""
    durationString = durationString.strip()
    if durationString.find(' ') == -1:
        s = durationString[0:-1]
        return int(s)
    else:
        m, s = durationString.split(' ')
        m = int(m[0:-1])
        s = int(s[0:-1])
        return 60*m + s


def CombineIPv4v6TestResult(testCaseDurations):
    tns = sets.Set( [GetTestCaseName(x[0]) for x in testCaseDurations] )
    tns = sorted(list(tns))
    combinedTestCaseDurations = []
    for testName in tns:
        duration = 0
        testResult = ''
        for (tn, tr, td) in testCaseDurations:
            if tn.startswith(testName):
                duration += td
                if testResult == '':
                    testResult = tr 
        combinedTestCaseDurations.append( (testName, testResult, duration) )
    return combinedTestCaseDurations


def GetTestCaseName(testResultName):            
    return testResultName.split(' - ')[0].strip()

    
def SplitTestCases(testCaseDurations, n):       
    """ testCaseDurations: one element (testName, testResult, testDuration) """
    tcDurations = collections.deque(testCaseDurations)
    totalDuration = sum([x[2] for x in testCaseDurations])
    plannedDuration = totalDuration / n
    tcGroups = []
    tcGroupTotal = 0
    retTestDurations = []

    while True:
        (tn, tr, td) = tcDurations.popleft()
        tcGroups.append((tn, tr, td))
        tcGroupTotal = tcGroupTotal + td
        if tcGroupTotal > plannedDuration:
            # this will make n+1 groups
            #if abs(tcGroupTotal - plannedDuration) < abs(plannedDuration - (tcGroupTotal - td)):
            #    tcDurations.appendleft( tcGroups.pop() )
            retTestDurations.append(tcGroups)
            tcGroups = []
            tcGroupTotal = 0
        if tcDurations == collections.deque([]):
            retTestDurations.append(tcGroups)
            break
    return retTestDurations


def GetCommandLineMax():
    return int( commands.getoutput('getconf ARG_MAX') ) - 2048


def CheckCommandLength(shCmd):
    cmd = """/net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/tools/vx7-util-scripts/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --vxworks="board=vxsim_linux_1_0_0_0,target=simlinux,version=7,wrenv=7,path=/home/svc-cmnet/vxworks" --speed --no-rebuild"""
    if (GetCommandLineMax() - len(cmd) - len(shCmd)) > 0:
        return True
    else:
        return False
    
    
def Output(testCases):
    print testCases
    print 'total:', len(testCases)


def debug():
    job = 'ut-vxsim-IPSEC-IPCRYPTO'
    #job = 'ut-vxsim-IKE'
    build = 60
    
    tcs = GetTestCases(jenkinsWeb, job, build)
    Output(tcs)

    consoleHtml = GetBuildConsole(jenkinsWeb, job, build, user, password)
    tds = []
    for x in tcs:
        oneTd = GetOneTestCaseDuration(x, consoleHtml)
        tds.append(oneTd)
        print oneTd
    print len(tds)
    print '*'*20
    
    allTds = []
    groups = SplitTestCases(CombineIPv4v6TestResult(tds), 4)
    for g in groups:
        for t in g: print t
        print sum(x[2] for x in g)
        print '='*10
        allTds = allTds + g
    
    uniqueTestNames = sets.Set( [GetTestCaseName(x[0]) for x in tds] )
    print 'should be equal:%s, %s, %s' % (len(tds), len(uniqueTestNames), len(allTds))
    
    for g in groups:
        testNameStr = ','.join( [x[0] for x in g] )
        print testNameStr, CheckCommandLength(testNameStr)    


def main():
    # KongTestCase.py job build n-to-splitted
    if len(sys.argv) != 4:
        print '%s job build n-to-splitted' % os.path.basename(sys.argv[0])
        exit(1)
    
    job, build, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
    consoleHtml = GetBuildConsole(jenkinsWeb, job, build, user, password)    
    testCases = GetTestCases(jenkinsWeb, job, build)

    testDurations = []
    for x in testCases:
        oneTd = GetOneTestCaseDuration(x, consoleHtml)
        testDurations.append(oneTd)
    
    testGroups = SplitTestCases(CombineIPv4v6TestResult(testDurations), n)

    # check
    allTds = []
    uniqueTestNames = sets.Set( [GetTestCaseName(x[0]) for x in testDurations] )
    for g in testGroups:
        for t in g: print t
        allTds = allTds + g    
    if len(uniqueTestNames) != len(allTds):
        print '2nd should == 3rd below'
        print 'should be equal:%s, %s, %s' % (len(testDurations), len(uniqueTestNames), len(allTds))
        #exit(1)
    
    print '\n== Divided into %s ==' % n
    commandOK = True
    for g in testGroups:
        testNameStr = ','.join( [x[0] for x in g] )
        commandOK = commandOK & CheckCommandLength(testNameStr)
        print testNameStr
        print "within command line length:%s" % CheckCommandLength(testNameStr)
        print
      
    if not commandOK:
        print 'WARNING: some testcases length exceed Linux command line max limit'
    
if __name__ == '__main__': main()
