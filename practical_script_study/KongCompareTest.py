# Compare the test result to the defined test cases at KongTestPlanToReport.py
# and list all the different test for new test result

import os
import sys

from KongConfig import *
from Jenkins import GetJobLastBuildNumber, GetParentBuildIdFromMultiJob
from KongStoreTestResult import GetKongTestResult, MarkTestPlan
from KongTestSuite import RetrieveCiSummaryTestResult

def CompareToTestPlan(markedModTests, originModTests):
    """ mark test result to kong test plan template """
    # modTests : { mod1: [ (tn1, tr1), (tn2, tr2), ... ], mod2:... }

    modTestsDict = TranslateUnicodeToString(markedModTests)    
    originModTestsDict = TranslateUnicodeToString(originModTests)

    # common modules
    print '\n== different tests for ci-summary build\n'
    commonMods = set(modTestsDict.keys()).intersection( set(originModTestsDict.keys()) )
    for mod in commonMods:
        # common test name, different test results
        commonTestNames = set(originModTestsDict[mod]).intersection( set(modTestsDict[mod]) )
        for testName in commonTestNames:
            if modTestsDict[mod][testName] != originModTestsDict[mod][testName]:
                print mod, testName, originModTestsDict[mod][testName]
                
        # non-common test name that originModTest has
        diffTestNames = set(originModTestsDict[mod]).difference( set(modTestsDict[mod]) )
        for testName in diffTestNames:
            print mod, testName, originModTestsDict[mod][testName]
        

    # non-common modules that originModTests has
    diffMods = set(originModTestsDict.keys()).difference( set(modTestsDict.keys()) )
    for mod in diffMods:
        for testName in originModTestsDict[mod]:
            print mod, testName, originModTestsDict[mod][testName]


def TranslateUnicodeToString(modTests):
    # translate the format and unicode to string
    modTestsDict = {}
    for mod in modTests:
        modTestsDict[mod.encode('ascii', 'ignore')] = {}
        for tn, tr in modTests[mod]:
            modTestsDict[mod][tn.encode('ascii', 'ignore')] = tr.encode('ascii', 'ignore')
    return modTestsDict 


def OutputModTest(modTests):
    print '\n=== test module and test cases to report to LTAF'
    i, failed = 0, 0
    for mod in sorted(modTests.keys()):
        #print mod
        for tc in modTests[mod]:
            i += 1
            if tc[1] != 'OK':
                print '\t', tc
                failed += 1      
    print 'total module: %s, test cases: %s, failed: %s\n' % (len(modTests.keys()), i, failed)
    
        
def main():
    parentJobName = 'ci-manager'
    jobName = 'ci-summary'
    
    if len(sys.argv) != 2:
        print 'usage: %s ci-summary-build-id' % os.path.basename(sys.argv[0])
        sys.exit(1)
        
    #buildId = GetJobLastBuildNumber(kongJenkins, jobName, kongUser, kongPassword)
    buildId = int(sys.argv[1])
    parentBuildId = GetParentBuildIdFromMultiJob(kongJenkins, parentJobName, jobName, buildId, kongUser, kongPassword)
    print '=== ci-manager #%s\n' % parentBuildId
    print '=== ci-summary #%s\n' % buildId
    
    branch, commit, testCaseResults = RetrieveCiSummaryTestResult(buildId)
    print '=== branch:%s, commit:%s\n' % (branch, commit)
    
    if branch in kongReportBranches:
        originModTests = GetKongTestResult(buildId, branch, commit)
        markedModTests = MarkTestPlan(originModTests)
        
        CompareToTestPlan(markedModTests, originModTests)

        OutputModTest(markedModTests)

if __name__ == '__main__':
    main()
