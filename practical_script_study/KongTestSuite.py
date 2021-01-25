import os
import re
import sys

from Jenkins import GetBuildConsole, GetJobLastBuildNumber
from KongTestPlanToReport import kongTestPlanToReport
from KongConfig import *

from runtestsuite_conf import testable_packages


def RetrieveCiSummaryTestResult(buildId):
    jobName = 'ci-summary'
    log = GetBuildConsole(kongJenkins, jobName, buildId, user=kongUser, password=kongPassword)

    testResults = {}
    for bsp in kongTestPlanToReport.keys():
        if bsp not in testResults:
            testResults[bsp] = {}
            
        ptnTestCase = '(?s)Detailed test cases for %s: total .*?\n(.*?)Modules for %s:' % (bsp, bsp)
        ptnBranch = '(?s)\+ BRANCH=(.*?)\n'
        ptnCommit = '(?s)\+ NEWCOMMIT=(.*?)\n'
        testCase = ExtractItem(ptnTestCase, log)
        testCase = FilterOutNoise(testCase)
        branch = ExtractItem(ptnBranch, log)
        commit = ExtractItem(ptnCommit, log)
        
        testCases = [x.strip().split(',') for x in testCase.split('\n') if x.strip() != '']
        for testResult in testCases:
            try: 
                x, y = testResult
                name = x.strip()
                result = y.strip()
                if result.lower() == 'ok':  # conform to mangoDB test result
                    result = 'PASS'
                elif result.lower() == 'failed':
                    result = 'FAIL'
                elif result.lower() == 'skipped':
                    result = 'BLOCKED'
                else:
                    raise BaseException('wrong test result: %s' % result)
                testResults[bsp][name] = result
            except:
                pass
        
    return branch, commit, testResults
    

def FilterOutNoise(content):
    def FilterContent(content, filterOutKeywords):
        for s in filterOutKeywords:
            content = content.replace(s, '')
        return content
                 
    # ci-summary sometimes has some weird strings so to filter them out
    filterOutStr1s = ('close failed in file object destructor:\n',
                     )
    content = FilterContent(content, filterOutStr1s)
        
    filterOutPtn = 'sudo: unable to resolve host (.*?): Connection timed out\n'
    founds = re.findall(filterOutPtn, content)
    if founds:
        founds = list(set(founds))
        filterOutStr2s = ['sudo: unable to resolve host %s: Connection timed out\n' % x for x in founds]
        content = FilterContent(content, filterOutStr2s)
    return content

                                        
def ExtractItem(rePattern, content):
    found = re.search(rePattern, content)
    if found is not None:
        return found.groups()[0]
    else:
        raise BaseException('not found %s' % rePattern)


def CompareTestSuiteResult(testCaseResults):
    """ tc = any test case in testCaseResults 
        tcBenchmarkeds = all the test cases to be used as a benchmark
        if tc in tcBenchmarkeds, compare test result with benchmarked test case result
        if tc not in tcBenchmarkeds, tc makes no sense to test suite result
        TO-DO:  tcBenchmarkeds should be checked   
    """
    benchmarkTestCaseMap = FindBenchmarkTestCaseMap()
    retModResults = {}
    
    for mod in benchmarkTestCaseMap:
        retModResults[mod] = 'PASS'
        
        if benchmarkTestCaseMap[mod] == {}:
            continue
        
        for testName in testCaseResults:
            if testName in benchmarkTestCaseMap[mod]:
                #print '\t%s in benchmark test cases of mod: %s' % (testName, mod)
                if not CompareTestCaseResult(testName, benchmarkTestCaseMap[mod][testName], testName, testCaseResults[testName]):
                    retModResults[mod] = 'FAIL'
                    break
        #print
        
    return retModResults    
            

def CompareTestCaseResult(benchmarkName1, benchmarkNamResult1, name2, result2):
    assert benchmarkName1 == name2
    validStatuses = ['PASS', 'FAIL', 'BLOCKED'] 
    assert benchmarkNamResult1 in validStatuses
    assert result2 in validStatuses
    
    #print '\t\t%s, %s' % (benchmarkName1, benchmarkNamResult1)
    #print '\t\t%s, %s' % (name2, result2)
        
    if benchmarkNamResult1 == 'PASS':
        if result2 == 'PASS':
            return True
        else:
            return False
    else:
        return True


def FindBenchmarkTestCaseMap():
    """ create the map from module name to test cases from KongBenchmark.txt """
    rets = {}
    modEngineNames = GetTestEngineName()
    benchmarkFile = os.path.dirname(os.path.realpath(__file__)) + '/' + 'KongBenchmark.txt'
    testCaseResults = ReadBenchmark(benchmarkFile)
    for mod in modEngineNames:
        if rets.get(mod, None) == None:
            rets[mod] = {}
                    
        for engineName in modEngineNames[mod]:
            for name in testCaseResults:
                if name.split('.')[0] == engineName:
                    if rets[mod].get(name, None) == None:
                        rets[mod][name] = {}
                        rets[mod][name] = testCaseResults[name]
                    else:
                        rets[mod][name] = testCaseResults[name]

    return rets
                    
                    
def GetTestEngineName():
    rets = {}
    for mod in kongModules:
        rets[mod] = testable_packages[mod]['testengine_name']
    return rets
    

def CreateEngineName2Mod():
    rets = {}
    modEngineNames = GetTestEngineName()
    for mod in modEngineNames:
        engineNames = modEngineNames[mod]
        for engName in engineNames:
            rets[engName] = mod
    return rets
    

def WriteBenchmark(benchmarkFile, testCaseResults):
    with open(benchmarkFile, 'w') as fd:
        fc = ''
        for k in sorted(testCaseResults.keys()):
            fc = fc + '%s, %s\n' % (k, testCaseResults[k])
        fd.write(fc)


def ReadBenchmark(benchmarkFile):
    testCaseResults = {}
    with open(benchmarkFile, 'r') as fd:
        fc = fd.read()
        lines = [x for x in fc.split('\n') if x.strip() != '']
        for y in lines:
            name, result = y.split(',')
            testCaseResults[name.strip()] = result.strip()
    return testCaseResults
            

def main():
    buildId = GetJobLastBuildNumber(kongJenkins, 'ci-summary', kongUser, kongPassword)
    print '=== ci-summary #%s' % buildId
    
    branch, commit, testCaseResults = RetrieveCiSummaryTestResult(buildId)
    print '=== branch:%s, commit:%s' % (branch, commit)
    
    modResults = CompareTestSuiteResult(testCaseResults)
    for x in sorted(modResults.keys()): print x, modResults[x] 


def test_RetrieveCiSummaryTestResult():
    branch, commit, testCaseResults = RetrieveCiSummaryTestResult(2167)
    for bsp in testCaseResults: 
        for test in testCaseResults[bsp]:
            print('%s : %s' % (test, testCaseResults[bsp][test]))
            pass
    
if __name__ == '__main__':
    main()
    
