#!/usr/bin/env python

# store test results to LTAF and send nightly email

import os
import re
import sys
import time
from datetime import datetime

from Jenkins import *
from KongConfig import *
from KongLTAF import Store2LTAF, SendTestReportEmail
from KongRerunTest import GetModName, AnalyzeJenkinsTestResult, CombineTestResultPairs
from KongTestSuite import RetrieveCiSummaryTestResult, ExtractItem
from KongTestPlanToReport import kongTestPlanToReport
from KongJenkins import GetModTCBspFromLog
from InstallSpin import GetSpinInfo
from KongUtil import TodayStr
from Action import ExecCmd

def GetKongTestResult(ciManagerBuildId, branch, commit):
    """ return the dictionary with each module : testCases 
        Note: rerun not supported """
    assert type(ciManagerBuildId) == int

    # modTests      = { 'bsp1': { 'mod1' : [(tn1, tr1), (tn2, tr2), ...], }, ...} 
    # rerunModTests = { 'bsp1': { 'mod1' : [(tn1, tr1), (tn2, tr2), ...], }, ...}     
    modTests, rerunModTests = {}, {}
        
    multiJobProject = 'ci-manager'
    jobName = 'ci-summary'

    parentBuildId = GetParentBuildIdFromMultiJob(kongJenkins, multiJobProject, jobName, ciManagerBuildId, kongUser, kongPassword)
    jobBuilds = GetJobBuildsFromMultiJob(kongJenkins, multiJobProject, parentBuildId, kongUser, kongPassword)
    runTestJobBuilds = [x for x in jobBuilds if x[0].startswith(kongTestJobPrefix)]
    
    summarys = [x for x in jobBuilds if x[0] == 'ci-summary']
    rerunBuilds = GetRerunJobs(summarys[0][0], summarys[0][1])

    # handle run test results    
    for job, build in runTestJobBuilds:
        mod = GetModName(job)
        tcs0, bsp = AnalyzeJenkinsTestResult(job, build, kongJenkins)
        print 'handling %s %s...' % (bsp, job)
        if bsp not in modTests:
            modTests[bsp] = {} 
        tcs = [x for x in tcs0 if x[1].lower() != 'skipped']
        
        # filter out some test results according to kongReportFilteredOutTestCases at KongConfig.py
        tcs = filter(lambda x: x[0].split('-')[0].strip() not in kongReportFilteredOutTestCases, tcs)
        
        if mod in modTests[bsp]:
            modTests[bsp][mod] += tcs
        else:
            modTests[bsp][mod] = tcs

    # handle rerun test results
    for job, build in rerunBuilds:
        mod, bsp = GetModNameFromLog(job, build)
        print 'handling %s %s #%s (%s)...' % (bsp, job, build, mod)

        if mod != '':
            tcs0, _ = AnalyzeJenkinsTestResult(job, build, kongJenkins)
            tcs = [x for x in tcs0 if x[1].lower() != 'skipped']
            tcs = filter(lambda x: x[0].split('-')[0].strip() not in kongReportFilteredOutTestCases, tcs)

            if bsp not in rerunModTests:
                rerunModTests[bsp] = {}
                
            if mod in rerunModTests[bsp]:
                rerunModTests[bsp][mod] += tcs
            else:
                rerunModTests[bsp][mod] = tcs

    newModTests = CombineModTests(modTests, rerunModTests)
    return newModTests


def GetRerunJobs(summaryJob, summaryBuildId):
    """ return (job, buildId) pairs """
    try:
        content = GetBuildConsole(kongJenkins, summaryJob, summaryBuildId, kongUser, kongPassword)
        # find two Jenkins jobs : ci-rerun-test and ci-rerun-test-rm
        founds = re.findall('(?s)Started (ci-rerun-test.*?) \#(.*?)\n', content) # Started ci-rerun-test #19778
        if founds:
            return founds
        else:
            return []
    except:
        return []
    

def GetModNameFromLog(summaryJob, summaryBuildId):
    try:
        content = GetBuildConsole(kongJenkins, summaryJob, summaryBuildId, kongUser, kongPassword)
        mod = ExtractItem('(?s)MODULE=(.*?)\n', content)
        bsp = ExtractItem('(?s)BSP=(.*?)\n', content)
        return mod, bsp
    except:
        return '', ''


def CombineModTests(modTests, rerunModTests):
    # modTests      = { 'bsp1': { 'mod1' : [(tn1, tr1), (tn2, tr2), ...], }, ...} 
    # rerunModTests = { 'bsp1': { 'mod1' : [(tn1, tr1), (tn2, tr2), ...], }, ...}     
    for bsp in modTests.keys():    
        newModTests = modTests.copy()
        if bsp in modTests and bsp in rerunModTests:
            commonMods = set(modTests[bsp].keys()).intersection( set(rerunModTests[bsp].keys()) )
            #print '=== commonMods:', commonMods
            for mod in commonMods:
                testResults = modTests[bsp][mod]
                rerunTestResults = rerunModTests[bsp][mod]
                combinedTestResults = CombineTestResultPairs(testResults + rerunTestResults)
                newModTests[bsp][mod] = combinedTestResults
                #if True or mod == 'IPNET':
                #    print '\t=== mod:', mod
                #    print '\t--- modTests     :', testResults
                #    print '\t--- rerunModTests:', rerunTestResults
                #    print '\t--- combined     :', newModTests[mod]
                #    print
            #print '\t--- final return:', newModTests
    return newModTests


def MarkTestPlan(modTests):
    """ mark test result to kong test plan template """
    # modTests      = { 'bsp1': { 'mod1' : [(tn1, tr1), (tn2, tr2), ...], }, ...} 
    # modTestsDict  = { 'bsp1': { 'mod1' : { 'tn1':'tr1', 'tn2':'tr2', ...}, ...}
    
    # translate the format and unicode to string
    modTestsDict = {}
    for bsp in modTests:
        if bsp not in modTestsDict:
            modTestsDict[bsp] = {}
        for mod in modTests[bsp]:
            modTestsDict[bsp][mod.encode('ascii', 'ignore')] = {}
            for tn, tr in modTests[bsp][mod]:
                modTestsDict[bsp][mod][tn.encode('ascii', 'ignore')] = tr.encode('ascii', 'ignore')

    # mark test result   
    for bsp in modTestsDict.keys():
        if bsp in kongTestPlanToReport and bsp in modTestsDict:
            commonMods = set(kongTestPlanToReport[bsp].keys()).intersection( set(modTestsDict[bsp].keys()) )
            for mod in commonMods:
                commonTestNames = set(kongTestPlanToReport[bsp][mod]).intersection( set(modTestsDict[bsp][mod]) )
                for testName in commonTestNames:
                    kongTestPlanToReport[bsp][mod][testName] = modTestsDict[bsp][mod][testName]

    # translate the format
    retModTests = {}
    for bsp in kongTestPlanToReport:
        if bsp not in retModTests:
            retModTests[bsp] = {}
        for mod in kongTestPlanToReport[bsp]:
            retModTests[bsp][mod] = []
            for tn in kongTestPlanToReport[bsp][mod]:
                retModTests[bsp][mod].append( (tn, kongTestPlanToReport[bsp][mod][tn]) )
    # retModTests = { 'bsp1': { 'mod1' : [ (tn1, tr), (tn2, tr2), ... ], ...}, ...}
    return retModTests
    
    
def GetTotalTimeFromMultiJob(parentJobName, parentBuildId):
    """ return minutes """
    startTime, endTime = None, None

    jobBuilds = GetJobBuildsFromMultiJob(kongJenkins, 'ci-manager', parentBuildId, kongUser, kongPassword)
    for jobName, buildId in jobBuilds:
        if jobName == 'ci-build-manager':
            startTime = GetJobBuildTimeStamp(kongJenkins, jobName, buildId, kongUser, kongPassword)
        if jobName == 'ci-summary':
            endTime = GetJobBuildTimeStamp(kongJenkins, jobName, buildId, kongUser, kongPassword, duration=True)

    if startTime is not None and (endTime is not None):
        minute = (endTime - startTime) / 60.0 + 3.0
        delta = '%.2f' % minute
        return float(delta)
    else:
        return None
    

def test_GetTotalTime():
    print GetTotalTimeFromMultiJob('ci-manager', 801)
    
       
def OutputModTest(modTests):
    print '\n=== test module and test cases to report to LTAF'
    total = 0
    
    for bsp in sorted(modTests.keys()):
        i = 0
        print '\nbsp=', bsp
        for mod in sorted(modTests[bsp].keys()):
            print '\t', mod
            for tc in modTests[bsp][mod]:
                i += 1
                print '\t\t', tc       
        print '\tbsp=%s total module: %s, test cases: %s\n' % (bsp, len(modTests.keys()), i)
        total += i
    print 'Total test cases: %s for bsps %s\n' % ( total, sorted(modTests.keys()) )

def GetRunDate(commit):
    return GetSpinInfo(commit, 'date')


def get_vxworks_env(install_path):
    base4relx = install_path + '/vxworks'
    if os.path.exists(base4relx):
        envdir = os.listdir(base4relx)
        envstr = 'vxworks/' + envdir[0]
        wrenv_prefix = '%s/wrenv.sh -p %s' % (install_path, envstr) 
        # get pkgs_path from $WIND_PKGS
        cmd = wrenv_prefix + ' env | grep WIND_PKGS='
        ret, result = ExecCmd(cmd)
        pkgs_path = result.strip().lstrip('WIND_PKGS=')
    elif os.path.exists(install_path + '/vxworks-7'):
        pkgs_path = install_path + '/vxworks-7/pkgs_v2'
        wrenv_prefix = '%s/wrenv.sh -p vxworks-7' % install_path
    elif os.path.exists(install_path + '/helix/guests/vxworks-7'):
        pkgs_path = install_path + '/helix/guests/vxworks-7/pkgs_v2'
        wrenv_prefix = '%s/wrenv.sh -p helix' % install_path
    elif os.path.exists(install_path + '/vxworks-653'):
        pkgs_path = install_path + '/vxworks-653/pkgs'
        wrenv_prefix = '%s/wrenv.sh -p vxworks-653' % install_path
    else:
        raise BaseException('%s not correct since vxworks-7, vxworks-653 and helix/guests/vxworks-7 was not found' % install_path)
    return pkgs_path, wrenv_prefix


def GetSpinType(install_path):
    _, wrenv_prefix = get_vxworks_env(install_path)
    if wrenv_prefix.split(' ')[-1] == 'vxworks-7':
        return 'native'
    elif 'vxworks' in wrenv_prefix.split(' ')[-1]:
        return 'native'
    elif wrenv_prefix.split(' ')[-1] == 'helix':
        return 'helix'
    else:
        raise BaseException('|%s| should contain either vxworks-7 or helix' % wrenv_prefix)
    

def PrintModTest(modTests):
    for bsp in modTests:
        print '\n', bsp
        for mod in modTests[bsp]:
            print '\n\t', mod
            for tc in modTests[bsp][mod]:
                print '\t\t', tc
                    
def main():
    parentJobName = 'ci-manager'
    jobName = 'ci-summary'
       
    buildId = GetJobLastBuildNumber(kongJenkins, jobName, kongUser, kongPassword)
    parentBuildId = GetParentBuildIdFromMultiJob(kongJenkins, parentJobName, jobName, buildId, kongUser, kongPassword)
    print '=== ci-manager #%s\n' % parentBuildId
    print '=== ci-summary #%s\n' % buildId
    
    branch, commit, _ = RetrieveCiSummaryTestResult(buildId)
    print '=== branch:%s, commit:%s\n' % (branch, commit)

    if branch in kongReportBranches or commit in ('SPIN', 'CISPIN',):
        originModTests = GetKongTestResult(buildId, branch, commit)
        modTests = MarkTestPlan(originModTests)

        if branch.startswith('SPIN:'):  # for spin
            ltaf_release = GetSpinInfo(commit, 'release')
            ltaf_component = 'networking'
            ltaf_tag = 'KONG-nightly'
        else:                           # hardcoded for branch
            ltaf_release = 'vx7-integration-native'
            ltaf_component = 'networking'
            ltaf_tag = 'KONG-nightly'
        
        if commit in ('SPIN', 'CISPIN',):
            testDate = GetRunDate(commit)
        else:
            testDate = TodayStr()
        if not testDate:
            print '=== run date is empty, so using Jenkins first job date'
            testDate = time.strftime('%Y-%m-%d', time.localtime(GetJobBuildTimeStamp(kongJenkins, parentJobName, parentBuildId, kongUser, kongPassword)))

        print '\n=== ltaf_release=%s | testDate=%s ' % (ltaf_release, testDate)

        if commit in ('SPIN', 'CISPIN',):
            spinType = GetSpinType('/net/%s' % GetImageServer() + branch.replace('SPIN:', ''))
        elif any(x.isdigit() for x in commit) and any(x.isalpha() for x in commit):
            spinType = 'native'
        else:
            spinType = 'native'
        print '\nwriting to LTAF using %s @ %s for spin type=%s' % (testDate, datetime.today(), spinType)
        
        if ltaf_release in kongLTAFRequirements:
            Store2LTAF(modTests, spinType, branch, commit, ltaf_release, testDate=testDate, requirement=kongLTAFRequirements[ltaf_release])
        else:
            Store2LTAF(modTests, spinType, branch, commit, ltaf_release, testDate=testDate)
            #print 'DEBUG: seem to store to LTAF...'

        OutputModTest(modTests)

        total_time = GetTotalTimeFromMultiJob(parentJobName, parentBuildId)
        if total_time is not None:
            total_time = str(total_time) + ' minutes'
        else:
            total_time = '100 minutes'
        html_link = 'http://pek-testharness-s1.wrs.com:8080/view/KONG-CI/job/ci-manager/%s/' % parentBuildId

        if kongDebugOn:
            toEmail = 'libo.chen@windriver.com'
        else:
            toEmail = kongReportEmail
        SendTestReportEmail(toEmail, branch, commit, ltaf_release, ltaf_component, ltaf_tag, total_time, html_link, testDate=testDate)    


if __name__ == '__main__':
    main()
    #test_GetTotalTime()
    
