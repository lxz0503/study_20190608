# the tool function:
#   - monitor vxworks network Kong nightly test at LTAF
#   - rerun the failed test cases for several times
#   - check rerun test result
#   - update LTAF if test gets passed
#   - send email for notification

from datetime import date, datetime, timedelta
import os
import copy
import operator
import subprocess
import sys
import time
import pprint as pp
from commands import getoutput

requiredLibPaths = ('/folk/lchen3/share/Mail',
                    '/folk/lchen3/try/workspace/PdvTool/vx7tool/new',
                   )
for lib in requiredLibPaths:
    if lib not in sys.path:
        sys.path.insert(0, lib)

import LTAF as ltaf
import Mail
import KongConfig as kc
import KongUtil
from Jenkins import GetBuildStatus, GetJobBuildTimeStamp, GetJobLastBuildNumber, GetParentBuildIdFromMultiJob, GetBuildConsole
from KongTestSuite import RetrieveCiSummaryTestResult
from InstallSpin import GetSpinInfo
from KongStoreTestResult import GetSpinType
from KongRerunTest import AnalyzeJenkinsTestResult
from KongLTAF import ConvertTestNameToLTAF, ConvertTestResultToLTAF
from KongRerunTest import ChangeTo2DotTestName

rerunJobName = 'try-MODULE'
maxFailedTestCase = 1800
    
def isGitCommit(string):
    if any(x.isdigit() for x in string) and any(x.islower() for x in string):
        return True
    return False

class JenkinsException(Exception):
    pass

class RerunTest:
    def __init__(self, nightlyRecord, commit='none'):
        if commit in ('SPIN', 'CISPIN', '653SPIN'):
            self.branch = 'SPIN:' + kc.spinConfig[commit]['spinToDir'] + '/' + nightlyRecord.spin
        elif isGitCommit(commit): # git on pek-vx-nwk1
            self.branch = kc.GetGitDir('pek-vx-nwk1') # '/buildarea1/svc-cmnet/vxworks'
        else:
            raise BaseException('commit %s not recognized (should be SPIN, CISPIN or 653SPIN' % commit)
        self.newCommit = commit
        
        self.module = nightlyRecord.testSuite
        self.testCase = nightlyRecord.testName.split('-')[0]
        self.bsp = nightlyRecord.bsp
        
        self.nightlyRecord = [nightlyRecord] # use list to map test case vs. test names

    def __str__(self):
        return 'module=%s testCase=%s bsp=%s branch=%s newCommit=%s ' % (self.module, self.testCase, self.bsp, self.branch, self.newCommit)


class RerunManager:
    def __init__(self, jenkinsJob, rerunTests):
        assert isinstance(rerunTests[0], RerunTest)
        self.jenkinsJob = jenkinsJob
        self.rerunTests = rerunTests
        self.runningTests = self.__Map2RunningTest(self.rerunTests)
    
    def Run(self):
        for rt in self.runningTests:
            self.jenkinsJob.AddTest(rt)

        self.jenkinsJob.LaunchTest()
        jobResults = self.jenkinsJob.ReportResult()
        
        # create fake data
        #print 'launch fake Jenkins jobs'
        
        #nightlyRecord1 = ltaf.NightlyRecord('rtnet.socktest.udp.udp_bind_invalid_namelen-IPv4', 'RTNET', '2018-12-31', 'Pass', 'http://pek-testharness-s1.wrs.com:8080/view/KONG-rerun/job/try-MODULE/2979', 'networking', 'KONG', 'Auto', '', 'networking', 'fsl_imx6', 'KONG', 'vx20181123201603_vx7-native', 'KONG-nightly', '2018-11-27 11:06:45', '0', '1', '', 'marked as fail for experiment',)
        #nightlyRecord2 = ltaf.NightlyRecord('rtnet.socktest.udp.ioctl_FIONBIO-IPv4',            'RTNET', '2018-12-31', 'Pass', 'http://pek-testharness-s1.wrs.com:8080/view/KONG-rerun/job/try-MODULE/2979', 'networking', 'KONG', 'Auto', '', 'networking', 'fsl_imx6', 'KONG', 'vx20181123201603_vx7-native', 'KONG-nightly', '2018-11-27 11:06:45', '0', '1', '', 'marked as fail for experiment')
        #rerunTest1 = RerunTest(nightlyRecord1, 'SPIN')
        #rerunTest1.nightlyRecord.append(nightlyRecord2)
        #jobResults = {2979: {'test': rerunTest1, 'result': 'Pass', 'log': 'http://pek-testharness-s1.wrs.com:8080/view/KONG-rerun/job/try-MODULE/2979'}}

        return self.__Map2RerunTest(self.rerunTests, jobResults)
    
    def __Map2RunningTest(self, rerunTests):
        # testName a.b.c[.d]-IPvX
        # testCase a.b.c[.d]
        # uniqueTestCases = {uniqueId : [nightlyRecord1, ...], }
        # where [nightlyRecord1, ...] refers to handle a.b.c.d -> a.b.c
        uniqueTestCases = {}
        for rt in rerunTests:
            if len(rt.testCase.split('.')) == 4:  # for special test case a.b.c.d
                newTestCase = self.__ToNormalTestCase(rt.testCase)
                uniqueId = self.__CreateUniqueId(rt.module, newTestCase, rt.bsp)

                newNightlyRecord = rt.nightlyRecord[0]
                newRt = RerunTest(newNightlyRecord, rt.newCommit)
                
                testCase = self.__TestName2TestCase(rt.nightlyRecord[0].testName)
                newRt.testCase = self.__ToNormalTestCase(testCase)
                if uniqueId in uniqueTestCases:
                    uniqueTestCases[uniqueId].nightlyRecord.append(newRt.nightlyRecord[0])
                else:
                    uniqueTestCases[uniqueId] = newRt
            else: # for normal test case a.b.c
                uniqueId = self.__CreateUniqueId(rt.module, rt.testCase, rt.bsp)
                uniqueTestCases[uniqueId] = rt
        return uniqueTestCases.values()
    
    def __Map2RerunTest(self, rerunTests, jobResults):
        # jobResults = { buildId : { 'test' : rerunTest, 'result' : 'Pass', 'log': ..., }, ...}
        rtnRerunTests = []
        
        for buildId in jobResults:
            # use the original test name, it might be a.b.c.d
            rt = jobResults[buildId]['test']
            nightlyRecords = rt.nightlyRecord
            if len(nightlyRecords) == 1 and nightlyRecords[0].testSuite != 'SOCKTEST': # for a.b.c
                print('=== 0 -- nightlyRecords[0].testSuite=%s' % nightlyRecords[0].testSuite)
                rt.nightlyRecord[0].status = jobResults[buildId]['result']
                rt.nightlyRecord[0].log = jobResults[buildId]['log']
                rtnRerunTests.append(rt)
            elif len(nightlyRecords) > 1 or nightlyRecords[0].testSuite == 'SOCKTEST': # for a.b.c.d
                print('=== 1 -- nightlyRecords[0].testSuite=%s' % nightlyRecords[0].testSuite)
                rts = self.__AnalyzeRerunTest(rerunJobName, buildId, jobResults[buildId])
                rtnRerunTests.extend(rts)
            else:
                raise BaseException('rt.nightlyRecord len == 0')

        return rtnRerunTests
    
    def __AnalyzeRerunTest(self, jobName, buildId, jobResult):
        rerunTests = []
        testResults, _ = AnalyzeJenkinsTestResult(jobName, buildId, kc.kongJenkins)
        if not testResults:
            return []
        nightlyRecords = jobResult['test'].nightlyRecord
        commit = jobResult['test'].newCommit
        
        for nr in nightlyRecords:
            for testName, result in testResults:
                if ChangeTo2DotTestName(testName)== nr.testName:
                    newnr = ltaf.NightlyRecord(nr.testName, nr.testSuite, nr.runDate, 
                          nr.status, nr.log, nr.component, nr.tester,  nr.automation, 
                          nr.requirement, nr.trDomain, nr.bsp, nr.board, nr.spin, 
                          nr.tags, nr.updateTime, nr.funcPass, nr.funcFail, nr.defects, 
                          nr.comment, nr.tech, nr.configLabel, nr.configuration)
                    newnr.testName = ConvertTestNameToLTAF(testName)
                    newnr.status = ConvertTestResultToLTAF(result)
                    newnr.log = jobResult['log']
                    rerunTests.append( RerunTest(newnr, commit) )
        return rerunTests          
    
    def __CreateUniqueId(self, module, testCase, bsp):
        sep = '^'
        return module + sep + testCase + sep + bsp
    
    def __ToNormalTestCase(self, testCaseOfmodFileClassCfunc):
        return '.'.join( testCaseOfmodFileClassCfunc.split('.')[0:3] )
    
    def __TestName2TestCase(self, testName):
        return testName.split('-')[0]
    
    def __TestName2TestVersion(self, testName):
        return testName.split('-')[1]
    
    def __TestCaseVersion2TestName(self, testCase, testVersion):
        return testCase + '-' + testVersion
    
class JenkinsJob:
    def __init__(self, jenkinsWeb, jobName, userName, password):
        self.jenkinsWeb = jenkinsWeb
        self.jobName = jobName
        self.userName = userName
        self.password = password
        self.jobs = {}
        self.runningBuildIds = []
        self.logTmpl = 'http://pek-testharness-s1.wrs.com:8080/view/KONG-rerun/job/%s/{buildId}' % self.jobName
        
    def AddTest(self, rerunTest):
        assert isinstance(rerunTest, RerunTest)
        i = 'x' + str(len(self.jobs))
        self.jobs[i] = { 'test' : rerunTest, 'result' : None, 'log' : '' } 
        
    def LaunchTest(self):
        for k in self.jobs:
            if type(k) == str and k.startswith('x'):
                _, buildId = self.__LaunchJob(self.jobs[k]['test'].branch, self.jobs[k]['test'].newCommit, 
                                              self.jobs[k]['test'].module, self.jobs[k]['test'].testCase,
                                              self.jobs[k]['test'].bsp)
                if buildId is not None:
                    self.jobs[buildId] = self.jobs[k]
                    self.runningBuildIds.append(buildId)
                    self.jobs.pop(k)
                else:
                    raise JenkinsException('buildId is None when launching %s' % self.jobs[k]['test'].testCase)
        
    def __LaunchJob(self, branch, newCommit, module, testCase, bsp):
        # must run as svc-cmnet at pek-cc-pb02l since using user ssh authentication
        jenkinsCli = '/net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/package/jenkins-cli.jar'
        cmd = 'java -jar %s -s %s build %s -p BRANCH=%s -p NEWCOMMIT=%s -p MODULE=%s \
               -p TESTCASE=%s -p BSP=%s -v -w --username %s --password %s' % (jenkinsCli, 
                                                                              self.jenkinsWeb, 
                                                                              self.jobName, 
                                                                              branch, 
                                                                              newCommit, 
                                                                              module, 
                                                                              testCase,
                                                                              bsp, 
                                                                              self.userName, 
                                                                              self.password)
        print '\n%s @ %s' % (cmd, time.asctime())
        
        ret = getoutput(cmd)
        print ret
        lastLine = ret.split('\n')[-1].strip()
        if lastLine.startswith('Started '):
            words = lastLine.split(' ')
            return words[1], int(words[2].replace('#', ''))
        else:
            return self.jobName, None        
        
    def ReportResult(self):
        # jobs[i] = { 'test' : rerunTest, 'result' : None, 'log' : '' }
        while True:
            if not self.runningBuildIds:
                break
            print '%s.' % self.runningBuildIds,
            for buildId in self.runningBuildIds:
                status = GetBuildStatus(self.jenkinsWeb, self.jobName, buildId, 
                                        user=self.userName, password=self.password)
                if status != 'INPROGRESS':
                    print '\n=== build %s %s : %s' % (buildId, self.jobs[buildId]['test'].testCase, status)
                    # double check the build status since sometimes GetBuildStatus() returns incorrect status
                    status1 = GetBuildStatusFromContent(self.jenkinsWeb, self.jobName, buildId, 
                                                        user=self.userName, password=self.password)
                    print '=== debug: build %s GetBuildStatusFromContent() returns status: %s' % (buildId, status1)
                    if status != status1:
                        print '\tstatus NOT MATCHED, try GetBuildStatusFromContent() again'
                        
                        # wait 120 seconds until the jenkins job has test output
                        args = {'jenkinsWeb' : self.jenkinsWeb,
                                'jobName' : self.jobName,
                                'buildId' : buildId,
                                'user' : self.userName,
                                'password' : self.password,
                               }
                        KongUtil.waitFuncReady(findTestOutput, args, True, timeout=120, interval=5)
                        
                        status1 = GetBuildStatusFromContent(self.jenkinsWeb, self.jobName, buildId, 
                                                            user=self.userName, password=self.password, debug=True)
                        print '=== debug: build %s GetBuildStatusFromContent() 2nd time returns status: %s' % (buildId, status1)
                    ltafResult = 'Pass' if status1 == 'SUCCESS' else 'Fail'
                    self.jobs[buildId]['result'] = ltafResult
                    self.jobs[buildId]['log'] = self.logTmpl.format(buildId=buildId)
                    self.runningBuildIds.remove(buildId)
            time.sleep(60)
        return self.jobs


def findTestOutput(jenkinsWeb, jobName, buildId, user, password):
    content = GetBuildConsole(jenkinsWeb, jobName, buildId, user, password).encode('utf-8')
    if content.find('Info: tinderbox: status:') != -1:
        return True
    else:
        return False
    
        
def GetBuildStatusFromContent(jenkinsWeb, jobName, buildId, user, password, debug=False):
    content = GetBuildConsole(jenkinsWeb, jobName, buildId, user, password).encode('utf-8')
    if debug:
        print 'jenkinsWeb=%s, jobName=%s, buildId=%s, user=%s, password=%s' % (jenkinsWeb, jobName, buildId, user, password)
        print '=== content ==='
        print content
        print '='*22
    passFlag = 'Info: tinderbox: status: success'
    if content.find(passFlag) != -1:
        return 'SUCCESS'
    else:
        return 'FAILURE'
    
    
class Notifier:
    def __init__(self, toEmail='libo.chen@windriver.com', 
                 fromEmail='libo.chen@windriver.com', 
                 server='smtp-na.wrs.com'):
        self.toEmail = toEmail
        self.fromEmail = fromEmail
        self.server = server
        self.oldNightlyRecords = None
        self.newNightlyRecords = None
        self.notpassedTests = None
        
    def AddOldNightlyRecord(self, nightlyRecords):
        notpassedTests = filter(lambda x:x.status != 'Pass', nightlyRecords)
        #print notpassedTests
        # tip: copy.deepcopy() has to be used here since each element is an object of a class
        self.oldNightlyRecords = map(lambda x: copy.deepcopy(x), notpassedTests)
        self.notpassedTests = [self.__GetUniqueTest(x) for x in self.oldNightlyRecords]
        
    def AddNewNightlyRecord(self, nightlyRecords):
        self.newNightlyRecords = sorted(list([x for x in nightlyRecords if self.__GetUniqueTest(x) in self.notpassedTests]), 
                                        key=operator.attrgetter('testName'), reverse=False)
    
    def Notify(self):
        if self.oldNightlyRecords is not None and \
           self.newNightlyRecords is not None and \
           self.oldNightlyRecords != self.newNightlyRecords:
            msg = ''
            spin = ''

            msg += str('Old nightly records:\n')
            for x in self.oldNightlyRecords:
                msg += str('\t%s %s : %s\n' % (x.testName, x.testSuite, x.status))
                if not spin:
                    spin = x.spin
            msg += str('\n')
            
            msg += str('New nightly records:\n')
            for x in self.newNightlyRecords:
                msg += str('\t%s %s : %s %s\n' % (x.testName, x.testSuite, x.status, x.log))
                if not spin:
                    spin = x.spin
            msg += str('\n')
                
            subject = 'Kong rerun test result for %s based on LTAF' % spin
            content = str(msg)
            Mail.SendEmail(self.fromEmail, self.toEmail, subject, content)
        else:
            print 'same nightly record before and after rerunning'

    def __GetUniqueTest(self, nightlyRecord):
        return nightlyRecord.testName + '@' + nightlyRecord.testSuite
        
    
def ReadNightlyTest(release, component, tags, monitorDate, perPage=3000):
    fetcher = ltaf.NightlyTestReader(release, component, tags, monitorDate, perPage)
    html = fetcher.GetHtml()
    
    nightlyResult = ltaf.LTAFTestResult()
    nightlyRecords = nightlyResult.GetRecords(html)

    return nightlyRecords
    

def WriteNightlyTest(spinType, release, nightlyRecords, branch, commit):
    assert isinstance(nightlyRecords[0], ltaf.NightlyRecord)
    print '\n=== updating LTAF nightly record status'

    writer = ltaf.NightlyReportWriter(spinType, release, nightlyRecords[0].runDate, build=branch, buildOption=commit)
    for nr in nightlyRecords:
        if nr.status == 'Pass':
            nr.funcPass, nr.funcFail = 1, 0
        else:
            nr.funcPass, nr.funcFail = 0, 1
        print '\t%s %s %s %s %s' % (nr.testName, nr.testSuite, nr.status, nr.funcPass, nr.funcFail)
        writer.AddTestResult(nr)
    writer.Store()  
    

def CompressTest(nightlyRecords):
    def CompressTestName(nightlyRecord):
        shortTestName = ChangeTo2DotTestName(nightlyRecord.testName)
        nightlyRecord.testName = shortTestName
        return nightlyRecord
    
    records = map(lambda x:CompressTestName(x), nightlyRecords)
    
    compressedRecords = []
    for r in records:
        if not r.testName.startswith('rtnet.') and r not in compressedRecords:
            compressedRecords.append(r)
    
    return compressedRecords
    
        
def CheckNightlyRecord(records, commit):
    if not records:
        print '=== %s records found' % len(records)
        sys.exit(0)

    notPassedRecords = CompressTest([x for x in records if x.status != 'Pass'])        
    rerunTests = [RerunTest(x, commit) for x in notPassedRecords]

    if len(rerunTests) == 0:
        print '=== %s records found with %s not passed' % (len(records), len(rerunTests))
        sys.exit(0)
    
    if len(rerunTests) > maxFailedTestCase:
        print '%s test cases not passed : too many rerunning (> %s), exit and report' % (len(rerunTests), maxFailedTestCase)
        sys.exit(1)
    
    print 'DBUG: len(rerunTests)=', len(rerunTests)
    return rerunTests


def GetMultiJobInfo():
    parentJobName = 'ci-manager'
    jobName = 'ci-summary'
       
    buildId = GetJobLastBuildNumber(kc.kongJenkins, jobName, kc.kongUser, kc.kongPassword)
    parentBuildId = GetParentBuildIdFromMultiJob(kc.kongJenkins, parentJobName, jobName, buildId, 
                                                 kc.kongUser, kc.kongPassword)
    branch, commit, _ = RetrieveCiSummaryTestResult(buildId)
    testDate = time.strftime('%Y-%m-%d', time.localtime(GetJobBuildTimeStamp(kc.kongJenkins, 
                                                                             parentJobName, 
                                                                             parentBuildId, 
                                                                             kc.kongUser, 
                                                                             kc.kongPassword)))
    return branch, commit, testDate


def run_shell_cmd(cmd):
    print 'cmd %s', cmd
    p = subprocess.Popen(cmd,bufsize=1,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    std_out, _ = p.communicate()
    print 'std_out : %s' % std_out
    return (p.returncode, std_out)


def get_fail_case_list(ltaf_release_name, ltaf_component):
    exePath = os.path.dirname(os.path.realpath(__file__))
    failcaselist_filename = exePath + '/' + 'failcaselist.wassp'
    # remove existing fail case list file
    cmd = 'rm -f ' + failcaselist_filename
    run_shell_cmd(cmd)

    # generate the fail case list file
    mefa_spin_date = os.getenv('MEFA_SPIN_DATE', default=datetime.today().strftime("%Y-%m-%d"))
    year, month, day =  mefa_spin_date.split('-')
    local_time = date(int(year), int(month), int(day))
    #local_time = datetime.today()
    report_time = local_time + timedelta(days = 0)
    report_date = report_time.strftime("%Y-%m-%d")
    #report_date = '2016-01-14' # Test result with one MIB failure

    cmd = "curl -F show_type=nightly -F release_name='%s' -F filter_rundate=%s -F filter_component=%s -F filter_status=Fail -F show_fields=test_name http://pek-lpgtest3.wrs.com/ltaf/show_result_fields.php > " % (ltaf_release_name, report_date, ltaf_component) + failcaselist_filename
    run_shell_cmd(cmd)

    failcase_num = 0
    failcaselistFd = open(failcaselist_filename, 'r')
    html_content = failcaselistFd.readlines()
    for _ in html_content:
        failcase_num = failcase_num + 1
    failcaselistFd.close()
    print 'Fail case number: %s' % failcase_num

    if failcase_num == 0:
        cmd = 'rm -f ' + failcaselist_filename
        run_shell_cmd(cmd)


def main():
    #monitorDate = KongUtil.AfterTodayStr(-1)
    branch, commit, _ = GetMultiJobInfo()
    if isGitCommit(commit):
        runcommit = commit
        commit = 'GIT'

    print '=== commit = %s' % commit
    assert commit in kc.spinConfig.keys()
        
    release = GetSpinInfo(commit, 'release')
    spinIndicator = commit
    monitorDate = GetSpinInfo(commit, 'date')
    
    if isGitCommit(commit):
        commit = runcommit

    #DEBUG
    #release = 'vx7-SR0660-features-native' 
    #release = 'vx7-integration-native' 
    #branch = 'SPIN:/buildarea1/svc-cmnet/SPIN/vx20201211021312_vx_21_03'
    #commit = 'SPIN'
    #spinIndicator = 'SPIN'
    #monitorDate = '2020-12-12'
        
    print 'branch=%s, commit=%s, monitorDate=%s' % (branch, commit, monitorDate)

    print '\n=== fetching %s LTAF record %s nightly test result' % (spinIndicator, monitorDate)
    component = 'networking'
    tags = 'KONG-nightly'

    nightlyRecords = ReadNightlyTest(release, component, tags, monitorDate)
    
    notifier = Notifier(toEmail='libo.chen@windriver.com; peng.bi@windriver.com; dapeng.zhang@windriver.com; yanyan.liu@windriver.com')
    notifier = Notifier(toEmail='yanyan.liu@windriver.com; xiaozhan.li@windriver.com')
    notifier.AddOldNightlyRecord(nightlyRecords)
    
    rerunTests = CheckNightlyRecord(nightlyRecords, commit)
    
    print '\n=== the following %s test cases required rerunning' % len(rerunTests)
    for rt in rerunTests:
        for nr in rt.nightlyRecord:
            print '\t%s %s %s %s' % (nr.bsp, nr.testName, nr.testSuite, nr.status) 
    
    job = JenkinsJob(kc.kongJenkins, rerunJobName, kc.kongUser, kc.kongPassword)
    rerunMgr = RerunManager(job, rerunTests)
    newRerunTests = rerunMgr.Run()

    if isGitCommit(commit):
        spinType = 'git'
        WriteNightlyTest(spinType, release, [x.nightlyRecord[0] for x in newRerunTests], branch, commit)          
    else:
        spinType = GetSpinType('/net/%s' % kc.GetImageServer() + branch.replace('SPIN:', ''))
        WriteNightlyTest(spinType, release, [x.nightlyRecord[0] for x in newRerunTests], branch = '', commit = '')          
    
    newNightlyRecords = ReadNightlyTest(release, component, tags, monitorDate)
    notifier.AddNewNightlyRecord(newNightlyRecords)
    notifier.Notify()

    
if __name__ == '__main__':
    main()
