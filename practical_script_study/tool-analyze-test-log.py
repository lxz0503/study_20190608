#!/usr/bin/env python

# features:
#    -analyze rerun test log module.log to display test results 

import argparse
import os
import re
import sys

def GetAllTestResultList(content):
    rets = []
    rawTestResult = FindRawTestResult(content)
    testCaseRawStrs = SplitRawTestResult(rawTestResult)
    for oneTestCaseStr in testCaseRawStrs:
        testName, testResult = ParseOneTestCaseResult(oneTestCaseStr)
        if testResult is not None: # None means that the testName is not valid, so remove it
            rets.append((testName, testResult))
    return rets
    
def FindRawTestResult(content):   
    # '(?s)Total ETA: .*?20\d\d\)(.*?)rounds:' find the first section
    # while '(?s)Total ETA: .*20\d\d\)(.*?)rounds:' finds the second section one if there is any failed test cases
    r = re.search('(?s)Total ETA: .*?20\d\d\)(.*?)rounds:', content)
    if r is not None:
        return r.groups()[0]
    else:
        raise Exception('ERROR: cannot find Kong raw test result')

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
        raise Exception('ERROR num of interrupted test name =', len(interrupredTestNames))
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
                raise Exception('ERROR cannot find ETA in', rawStr)
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
                           'iprohc_ip')
    if not (testCaseName.startswith('ip') or testCaseName.split('.')[0] in kongTestNameModules):
        return False
    if testCaseName.count('.') not in (2, 3):
        return False
    return True

def ConsolidateTestResult(tests):
    testDict = {}
    for tn, ts in tests:
        if tn not in testDict:
            testDict[tn] = ts
        else:
            if ts == 'OK':
                testDict[tn] = ts
    return testDict

    
def PrintModTestResult(mod, tests):
    if type(tests) == list:
        for testName, testStatus in tests:
            print '%s, %s, %s' % (mod, testName, testStatus)
    if type(tests) == dict:
        for testName in tests:
            testStatus = tests[testName]
            print '%s, %s, %s' % (mod, testName, testStatus)
            

def IsLogFile(fileName, extName='.log'):
    _, ext = os.path.splitext(fileName)
    return ext == extName

def GetModName(fileName):
    return os.path.basename(fileName).split('.')[0]
        
def main():
    parser = argparse.ArgumentParser(description='analyze nightly test log')
    parser.add_argument('--path', action='store', dest='logPath', help='the path that *.log locates (required)')
    args = parser.parse_args()

    if args.logPath is None:
        parser.print_help()
        exit(1)
    
    logFiles = sorted([os.path.join(args.logPath, x) for x in os.listdir(args.logPath) if IsLogFile(x)])

    for logFile in logFiles:
        mod = GetModName(logFile)
        with open(logFile, 'r') as fd:
            content = fd.read()
            try:
                tests = GetAllTestResultList(content)
                PrintModTestResult(mod, ConsolidateTestResult(tests))
            except Exception, e:
                print('%s : %s' % (mod, str(e)))
                continue

if __name__ == '__main__':
    main()
