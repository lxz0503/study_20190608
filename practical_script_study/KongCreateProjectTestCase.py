from Jenkins import *
from KongConfig import *
from KongLTAF import Store2LTAF, SendTestReportEmail
from KongRerunTest import GetModName, AnalyzeJenkinsTestResult, CombineTestResultPairs
from KongTestSuite import RetrieveCiSummaryTestResult
from KongTestPlanToReport import kongTestPlanToReport

def GetProjectTestCaseMap(project, maxBuildId):
    projectTestCases = {}
    
    buildId = GetSuccessProject(project, maxBuildId)
    if buildId is None:
        print '=== %s not found success job, try to get max tests' % project
        maxTest = 0
        for i in xrange(20):
            newBuildId = maxBuildId - i
            testCases, _ = AnalyzeJenkinsTestResult(project, newBuildId, kongJenkins)
            if len(testCases) > maxTest:
                maxTest = len(testCases)
                maxBuildId = newBuildId
        
        testCases, _ = AnalyzeJenkinsTestResult(project, maxBuildId, kongJenkins)
        projectTestCases[project] = {}
        for test, result in testCases:
            projectTestCases[project][test] = result
    else:
        testCases, _ = AnalyzeJenkinsTestResult(project, buildId, kongJenkins)
        projectTestCases[project] = {}
        for test, result in testCases:
            projectTestCases[project][test] = result

    return projectTestCases
        
    
def GetSuccessProject(project, maxBuildId, maxSearchDepth=30):
    i = 0
    buildId = maxBuildId
    
    while i < maxSearchDepth:
        print '=== ', project, buildId
        try:
            status = GetBuildStatus(kongJenkins, project, buildId, kongUser, kongPassword)
            if status == 'SUCCESS':
                break
            buildId -= 1
            i += 1
        except:
            buildId = None
            break
    else:
        buildId = None 
        
    return buildId
        

def Output(projectTests):
    for project in projectTests.keys():
        print '\'%s\' : {' % project
        for test in projectTests[project]:
            print '    \'%s\' : \'%s\',' % (test, projectTests[project][test])
        print '}, '


def test_GetProjectTestCaseMap():
    project = 'ut-vxsim-SNTP_SERVER'
    maxBuildId = 947
    projectTests = GetProjectTestCaseMap(project, maxBuildId)
    
    Output(projectTests)
    

def main():
    parentJobName = 'ci-manager'
    jobName = 'ci-summary'
       
    buildId = GetJobLastBuildNumber(kongJenkins, jobName, kongUser, kongPassword)
    parentBuildId = GetParentBuildIdFromMultiJob(kongJenkins, parentJobName, jobName, buildId, kongUser, kongPassword)
    print '=== This is to create the map from project to test cases for rerunning blocked test cases"
    print '=== ci-manager #%s\n' % parentBuildId
    print '=== ci-summary #%s\n' % buildId

    jobBuilds = GetJobBuildsFromMultiJob(kongJenkins, parentJobName, parentBuildId, kongUser, kongPassword)    
    for job, build in sorted(jobBuilds):
        if job.startswith('ut-vxsim-'):
            projectTests = GetProjectTestCaseMap(job, build)
            Output(projectTests)

    
if __name__ == '__main__':
    #test_GetProjectTestCaseMap()
    main()
        
