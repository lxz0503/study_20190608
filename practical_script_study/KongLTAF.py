#!/usr/bin/env python

import sys
import os, socket
import re
import time

from commands import getoutput
from datetime import datetime, timedelta

from Jenkins import GetJobBuildsFromMultiJob
from KongJira import JiraDefect
from KongUtil import sendMail, runShCmd, AfterTodayStr, TodayStr
import KongConfig

htmlEmailFile = '/tmp/ltaf_email.html'
ltafTrendFile = '/tmp/ltaf_trend.png'

testCaseFile = os.path.dirname(os.path.realpath(__file__)) + '/LTAF/' + 'test_case.conf.template'
testRunFile  = os.path.dirname(os.path.realpath(__file__)) + '/LTAF/' + 'test_run.conf.template'

ltafTestCase = {
                'default-branch' : {
                             'release' : 'VxWorks-Networking', # overrided by input
                             'testsuite' : None,
                             'component' : 'networking',
                             'testcasetype' : 'functional',
                             'feature' : 'KONG',
                            },
                'SPIN' :    {
                             'release' : 'vx7-SR0510-features',
                             'testsuite' : None,
                             'component' : 'networking',
                             'testcasetype' : 'functional',
                             'feature' : 'KONG',
                            },
               }            
               
         
ltafTestRun = {
                'default-branch' : {
                             'release' : 'VxWorks-Networking', # overrided by input
                             'test' : None,
                             'testsuite' : None,   # module
                             'component' : 'networking',
                             'domain' : '',
                             'sprint' : 'Nightly',
                             'week' : None,
                             'bsp' : 'vxsim_linux',
                             'spin' : '',
                             'status' : None,
                             'tags' : 'KONG-nightly',
                             'tester' : 'KONG',
                             'board' : 'KONG',
                             'build' : 'vx7-net',   # branch
                             'buildoptions' : None, # commit
                             'log' : '',
                            },
                'SPIN' :    {
                             'release' : 'vx7-SR0510-features',
                             'test' : None,
                             'testsuite' : None,
                             'component' : 'networking',
                             'domain' : 'networking',
                             'sprint' : 'Nightly',
                             'week' : None,
                             'bsp' : 'vxsim_linux',
                             'spin' : None,         # spin
                             'status' : None,
                             'tags' : 'KONG-nightly',
                             'tester' : 'KONG',
                             'board': 'KONG',
                             'build' : '',
                             'buildoptions' : '',
                             'log' : '',
                            },
            }                
 
          
emailConfig = {
               'productName' : 'VxWorks 7 Networking Nightly Test On Branch', 
               'git_branch' : 'vx7-net',
               'git_commit' : 'none', 
               'ltaf_release' : 'VxWorks-Networking', 
               'ltaf_component' : 'networking', 
               'ltaf_tag' : 'KONG-nightly',
               'ltaf_link' : '', 
               'test_server' : 'KONG VM cluster',
               'test_matrix' : 'n/a',
               
               'total_no' : '', 
               'pass_no' : '', 
               'pass_rate' : '', 
               'fail_no' : '', 
               'block_no' : '',
               'buildFail' : 0,
               'execFail' : 0,
               'timeout' : 0,
               'bootFail' : 0,
               'noTarget' : 0,
               'exception' : 0,

               'git_dir' : '/home/svc-cmnet/vxworks', 
               'wasspHome' : 'n/a',
               'wasspVersion' : 'n/a',
               'htmlLink' : '', 
               'total_time' : 100,
               }


def SendTestReportEmail(email_to, git_branch, git_commit, ltaf_release, ltaf_component, ltaf_tag, total_time, html_link, testDate=None):
    if testDate is not None:
        end_date = testDate
    else:
        end_date = TodayStr()
    start_date = AfterTodayStr(-13)

    # 1) get test summary from LTAF web page
    testresult_html_link = 'http://pek-lpgtest3.wrs.com/ltaf/nightly_interface.php?release_name=%s&f_type=info&date=%s&component=%s&tags=%s' % (ltaf_release, end_date, ltaf_component, ltaf_tag)
    if git_branch.startswith('SPIN:'):
        testresult_html_link += '&spin=%s' % git_branch
        emailConfig['productName'] = 'VxWorks 7 Networking Nightly Test On spin'
        assert git_commit in KongConfig.spinConfig.keys()
        if git_commit == 'SPIN':
            mail_branch = 'release spin'
        elif git_commit == 'CISPIN':
            mail_branch = 'ci-branch spin'
        elif git_commit == '653SPIN':
            mail_branch = '653 spin'
        else:
            mail_branch = git_commit
        mail_title = 'VxWorks 7 Nightly Testing Report (%s) - \"Networking KONG\" for %s' % (end_date, mail_branch)
        branch = git_branch.replace('SPIN:'+ KongConfig.spinConfig[git_commit]['spinToDir'] + '/', '')
    elif git_branch in KongConfig.kongReportBranches:
        testresult_html_link += '&build=%s' % git_branch
        mail_title = 'VxWorks 7 Networking KONG Nightly Testing Report (%s)' % end_date   
        branch = git_branch     
    else:
        print 'unsupported branch: %s' % git_branch
        sys.exit(1)
    
    saved_testresult_html_name = '/tmp/ltaf_nighlty_result.html'
    total_no, pass_no, pass_rate, fail_no, fail_rate, block_no, block_rate = GetLTAFTestResult(testresult_html_link, saved_testresult_html_name)
    print 'total:%s, pass:%s %s, fail:%s %s, block:%s %s' % (total_no, pass_no, pass_rate, fail_no, fail_rate, block_no, block_rate)
    
    # create intermediate email content with html format
    emailConfig['total_no'] = total_no
    emailConfig['pass_no'] = pass_no
    emailConfig['pass_rate'] = pass_rate
    emailConfig['fail_no'] = fail_no
    emailConfig['fail_rate'] = fail_rate
    emailConfig['block_no'] = block_no
    emailConfig['block_rate'] = block_rate

    emailConfig['git_branch'] = branch # Build <-> git branch
    emailConfig['git_commit'] = git_commit # Buildoptions <-> git commit
    
    emailConfig['total_time'] = total_time
    emailConfig['htmlLink'] = html_link
    
    emailConfig['ltaf_release'] = ltaf_release
    emailConfig['ltaf_component'] = ltaf_component
    emailConfig['ltaf_tag'] = ltaf_tag
        
    #if ltaf_release.startswith('vx7-SR'):  # 2) test report html link
    if git_commit in KongConfig.spinConfig.keys():
        emailConfig['ltaf_link'] = 'http://pek-lpgtest3.wrs.com/ltaf/nightly_results.php?releasename=%s&clearfilter=true&tf_tr_whentostart=%s&tf_test_component=%s&tf_tr_tags=%s&tf_tr_spin=%s' % (ltaf_release, end_date, ltaf_component, ltaf_tag, branch)
    else:
        emailConfig['ltaf_link'] = 'http://pek-lpgtest3.wrs.com/ltaf/nightly_results.php?releasename=%s&clearfilter=true&tf_tr_whentostart=%s&tf_test_component=%s&tf_tr_tags=%s&tf_tr_build=%s' % (ltaf_release, end_date, ltaf_component, ltaf_tag, git_branch)

    runShCmd('rm -f %s' % htmlEmailFile)
    with open(htmlEmailFile, 'a') as htmlFd:
        CreateReportEmail (htmlFd, emailConfig, testDate)
    
    # create MIME email
    #email_to = 'libo.chen@windriver.com'
    (rtn_code, mail_body) = runShCmd('cat %s' % htmlEmailFile)

    mail_content = {'from': 'VxWorks7 Nightly NEVER_REPLY <target@windriver.com>',
                   'to': email_to,
                   'subject': mail_title,
                   'body': str(mail_body),
                   'file': '%s' % ltafTrendFile,
                   'server': 'prod-webmail.corp.ad.wrs.com'} # smtp-na.wrs.com not work
    
    # send email
    sendMail(mail_content)


def CreateReportEmail(fd, emailConfig, testDate):
    # trend graph
    #if emailConfig['ltaf_release'].startswith('vx7-SR') or \
    #   emailConfig['ltaf_release'].startswith('vx7-CR') or \
    #   emailConfig['ltaf_release'].startswith('vx7-CI-features'):
    if emailConfig['git_commit'] in KongConfig.spinConfig.keys():
        graph_page = GetLTAFTrendGraph(testDate, emailConfig['ltaf_release'], emailConfig['ltaf_component'], emailConfig['ltaf_tag']) 
    else:
        graph_page = GetLTAFTrendGraph(testDate, emailConfig['ltaf_release'], emailConfig['ltaf_component'], emailConfig['ltaf_tag'], emailConfig['git_branch']) 
    graph_page = graph_page.replace(' ', '%20') # Replace the space in "VxWorks 7.0" with %20
           
    # Title
    Msg2Html(fd, '<basefont face="arial" size="4">')
    Msg2Html(fd, '<head><style>body {background-repeat:no-repeat;background-position:right top;}')
    Msg2Html(fd, 'table, td, th{border:1px solid black;}th{background-color:powderblue;color:blue;}</style></head>')

    # Show the product name and branch name in the e-mail html
    Msg2Html(fd, '<font face="arial" size="6"> %s : %s </font><br><br>' % (emailConfig['productName'], emailConfig['git_branch']))

    # Testing Summary
    Msg2Html(fd, '<b><font face="arial">1. Testing Summary</b>')
    Msg2Html(fd, '<br>')
    Msg2Html(fd, '<b><br></b>')
    Msg2Html(fd, '<table style="font-family:Arial"><thead><tr><th width="100">Total</th><th width="100">Pass</th><th width="100">Passrate</th></tr></thead>')
    Msg2Html(fd, '''<tbody><tr><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td></tr></tbody></table>''' % (emailConfig['total_no'], emailConfig['pass_no'], emailConfig['pass_rate']))
    Msg2Html(fd, "</tbody></table><br>" )
    Msg2Html(fd, '<table style="font-family:Arial"><thead><tr><th width="100">BuildFail</th><th width="100">ExecFail</th><th width="100">Fail</th><th width="100">Timeout</th><th width="100">BootFail</th><th width="100">NoTarget</th><th width="100">WASSP Exception</th><th width="100">Blocked</th></tr></thead>')
    Msg2Html(fd, '<tbody><tr><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td><td align="center"> %s</td><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td></tr></tbody></table><br>' % (emailConfig['buildFail'], emailConfig['execFail'], emailConfig['fail_no'], emailConfig['timeout'], emailConfig['bootFail'], emailConfig['noTarget'], emailConfig['exception'], emailConfig['block_no']))

    # Get graph trend
    Msg2Html(fd, '<a href=%s><img src="cid:chartImage" width=800 height=400/></a>' % graph_page)
    Msg2Html(fd, '<br><br>')
    Msg2Html(fd, '<b><br></b>')

    # LTAF link
    Msg2Html(fd, '<table style="font-family:Arial"><tr><th width="100">LTAF Link</th><td><a href=%s> %s </a></td></tr></table>' % (emailConfig['ltaf_link'], emailConfig['ltaf_link']))
    Msg2Html(fd, '<br><br>')
    Msg2Html(fd, '<b><br></b>')

    # Defect list
    """
    if int(emailConfig['fail_no']) != 0:  
        GetDefectList('defectlist.html', '21806')
        cmd = "cat defectlist.html"
        (rtn_code, defect_list) = runShCmd(cmd)
        Msg2Html(fd, '<b><font face="arial">Open Defects:</b>')
        Msg2Html(fd, '<table style="font-family:Arial"><tbody>')
        Msg2Html(fd, '<tr><td></td> %s </tr>' % str(defect_list))
        Msg2Html(fd, '</tbody></table><br>')
    """
    
    # Testing Details
    Msg2Html(fd, '<b><font face="arial">2. Testing Details:</b>')
    Msg2Html(fd, '<br>')
    Msg2Html(fd, '<b><br></b>')
    Msg2Html(fd, '<table style="font-family:Arial"><tbody>')
    Msg2Html(fd, '<tr><th width="100">GIT HEAD</th><td><a>%s</a></td></tr>' % emailConfig['git_commit'])
    Msg2Html(fd, '<tr><th width="100">Test Server</th><td>%s</td></tr>' % emailConfig['test_server'])
    Msg2Html(fd, '<tr><th width="100">WIND_HOME</th><td><a>%s</a></td></tr>' % emailConfig['git_dir'])
    Msg2Html(fd, '<tr><th width="100">Test Matrix</th><td><a href="%s">%s</a></td></tr>' % (emailConfig['test_matrix'], emailConfig['test_matrix']))
    Msg2Html(fd, '<tr><th width="100">Total Time</th><td><a>%s</a></td></tr>' % emailConfig['total_time'])
    Msg2Html(fd, '<tr><th width="100">WASSP HOME</th><td><a>%s</a></td></tr>' % emailConfig['wasspHome'])
    Msg2Html(fd, '<tr><th width="100">WASSP VERSION</th><td><a>%s</a></td></tr>' % emailConfig['wasspVersion'])
    Msg2Html(fd, '<tr><th width="100">HTML Log</th><td><a>%s</a></td></tr>' % emailConfig['htmlLink'])
    Msg2Html(fd, '</tbody></table><br>')
    
    # Append failed test cases if any
    if int(emailConfig['fail_no']) != 0:
        failedCases = GetFailCases(emailConfig['ltaf_release'], emailConfig['ltaf_component'], emailConfig['ltaf_tag'])
        if failedCases != []:
            jira = JiraDefect()
            Msg2Html(fd, '<b><font face="arial">3. Failed Test Cases</b>')
            Msg2Html(fd, '<table style="font-family:Arial"><tbody>')
            for x in failedCases:
                defectKey, defectStatus = jira.GetDefect(x)
                Msg2Html(fd, '<tr><td> %s </td><td> %s </td><td> %s </td></tr>' % (x, defectKey, defectStatus))
            Msg2Html(fd, '</tbody></table><br>')


def GetLTAFTestResult(testresult_html_link, saved_testresult_html_name):
    cmd='wget -O %s "%s"' % (saved_testresult_html_name, testresult_html_link)
    print 'Get LTAF at %s' % testresult_html_link 
    runShCmd(cmd)
    f = open('%s' % saved_testresult_html_name, 'r')
    content = f.readlines()
    f.close()

    pass_no=0
    fail_no=0
    total_no=0
    block_no=0
    pass_rate=0
    fail_rate=0
    total_rate=0
    block_rate=0

    for line in content:
        if 'Pass = ' in line:
            pass_no = line.split("Pass = ")[1].split(' ')[0]
        if 'Fail = ' in line:
            fail_no = line.split("Fail = ")[1].split(' ')[0]
        if 'Blocked = ' in line:
            block_no = line.split("Blocked = ")[1].split(' ')[0]
        if 'Total = ' in line:
            total_no = line.split("Total = ")[1].split(' ')[0]

    if total_no != 0:
        pass_percentage = float(pass_no) / float(total_no) * 100
        pass_rate = "%.2f%%" % pass_percentage
    return total_no, pass_no, pass_rate, fail_no, fail_rate, block_no, block_rate
            

def GetLTAFTrendGraph(testDate, ltaf_release, ltaf_component, ltaf_tag=None, ltaf_build=None):
    start_date = AfterTodayStr(-13)
    end_date = testDate
    
    ltaf_trend_html_link = 'http://pek-lpgtest3.wrs.com/ltaf/nightly_interface.php?release_name=%s&f_type=chart&start_date=%s&end_date=%s&component=%s' % (ltaf_release, start_date, end_date, ltaf_component)
    if ltaf_tag is not None:
        ltaf_trend_html_link += '&tags=%s' % ltaf_tag
    if ltaf_build is not None:
        ltaf_trend_html_link += '&build=%s' % ltaf_build
    cmd = 'wget -O %s "%s"' % (ltafTrendFile, ltaf_trend_html_link)
    print '--- trend graph cmd:', cmd
    runShCmd(cmd)
    
    return ltaf_trend_html_link


def GetDefectList (html_filename, jira_id):
    exePath = os.path.dirname(os.path.realpath(__file__))
    exeCmd = exePath + '/' + 'listDefects.sh'
    defectListFile = exePath + '/' + html_filename
    cmd = exeCmd + ' ' + defectListFile + ' ' + jira_id 
    runShCmd(cmd)
    

def Msg2Html (fd, msg):
    fd.write(str(msg))
    fd.write("\n")


def GetFailCases(ltaf_release, ltaf_component, ltaf_tag=None):
    report_date = TodayStr()
    #report_date = AfterTodayStr(-1)

    if ltaf_tag is not None:
        cmd = "curl -F show_type=nightly -F release_name=\"%s\" -F filter_rundate=%s -F filter_component=%s -F filter_tags=%s -F filter_status=Fail -F show_fields=test_name http://pek-lpgtest3.wrs.com/ltaf/show_result_fields.php" % (ltaf_release, report_date, ltaf_component, ltaf_tag)
    else:
        cmd = "curl -F show_type=nightly -F release_name=\"%s\" -F filter_rundate=%s -F filter_component=%s -F filter_status=Fail -F show_fields=test_name http://pek-lpgtest3.wrs.com/ltaf/show_result_fields.php" % (ltaf_release, report_date, ltaf_component)
    return map( lambda x: x.strip(),
                filter(lambda x: x.strip() != '', getoutput(cmd).split('\n')[3:]) )


def Store2LTAF(modTests, spin_type, branch, commit, ltaf_release, testDate=None, requirement=None):
    """ testDate is string like "2017-01-01" """
    # modTests = { 'bsp1': { 'mod1' : [ (tn1, tr), (tn2, tr2), ... ], ...}, ...}
    assert spin_type in ('native', 'helix', 'git')
    if commit in ('SPIN', 'CISPIN',):
        release = ltaf_release
        testCaseType = ltafTestCase['SPIN']['testcasetype']
        feature = ltafTestCase['SPIN']['feature']
        
        component = ltafTestRun['SPIN']['component']
        sprint = ltafTestRun['SPIN']['sprint']
        #bsp = ltafTestRun['SPIN']['bsp']
        assert commit in KongConfig.spinConfig.keys()
        spin = branch.replace('SPIN:'+ KongConfig.spinConfig[commit]['spinToDir'] + '/', '')
        tag = ltafTestRun['SPIN']['tags']
        tester = ltafTestRun['SPIN']['tester']
        board = ltafTestRun['SPIN']['board']
        build = ltafTestRun['SPIN']['build']
        buildOption = ltafTestRun['SPIN']['buildoptions']
        domain = ltafTestRun['SPIN']['domain']
    else:
        release = ltaf_release
        testCaseType = ltafTestCase['default-branch']['testcasetype']
        feature = ltafTestCase['default-branch']['feature']
        
        component = ltafTestRun['default-branch']['component']
        sprint = ltafTestRun['default-branch']['sprint']
        #bsp = ltafTestRun[branch]['bsp']
        spin = ''
        tag = ltafTestRun['default-branch']['tags']
        tester = ltafTestRun['default-branch']['tester']
        board = ltafTestRun['default-branch']['board']
        build = branch
        buildOption = commit
        domain = ltafTestRun['SPIN']['domain']
    
    if testDate is not None:
        week = testDate
    else:
        week = TodayStr()
    
    ciWasspReportBuildId = os.getenv('BUILD_NUMBER', '')
    if ciWasspReportBuildId:
        log = 'http://pek-testharness-s1.wrs.com:8080/view/KONG-CI/job/ci-wassp-report/{buildId}/console'.format(buildId=ciWasspReportBuildId)
    else:
        log = ltafTestRun[branch]['log']
                
    for bsp in modTests.keys():
        for mod in modTests[bsp]:
            tcs = modTests[bsp][mod]
            testsuite = mod
            
            # add test cases to LTAF
            #tempTCFile = CreateTestCaseFile(testCaseFile, release, testsuite, component, testCaseType, feature, [ConvertTestNameToLTAF(x[0]) for x in tcs], week)
            #cmd = 'curl -F testfile=@%s http://pek-lpgtest3.wrs.com/ltaf/upload_test.php' % tempTCFile
            #print cmd
            #print getoutput(cmd)
            
            # add test run results to LTAF
            for tc in tcs:
                testName   = ConvertTestNameToLTAF(tc[0])
                testResult = ConvertTestResultToLTAF(tc[1])
                if testResult == 'Pass':
                    funcPass, funcFail = 1, 0
                else:
                    funcPass, funcFail = 0, 1
                tempTRFile = CreateTestRunFile(testRunFile, spin_type, release, testName, testsuite, component, domain,  
                                               sprint, week, bsp, spin, testResult, tag, tester, board, build, 
                                               buildOption, log, funcPass, funcFail, requirement)
                cmd = 'curl -F resultfile=@%s http://pek-lpgtest3.wrs.com/ltaf/upload_nightly_results.php' % tempTRFile
                print '\nupload %s to LTAF' % testName
                print getoutput(cmd)
            print


def ConvertTestNameToLTAF(kongTestName):
    return kongTestName.replace(' ', '')


def ConvertTestResultToLTAF(kongTestResult):
    """ LTAF : Pass, Fail, Blocked, Notstarted """
    if kongTestResult.lower() == 'ok':
        return 'Pass'
    elif kongTestResult.lower() == 'failed':
        return 'Fail'
    elif kongTestResult.lower() == 'blocked':
        return 'Blocked'
    else:
        return None


def CreateTestCaseFile(testCaseTemplateFile, release, testsuite, component, testCaseType, feature, testNames, testDate):
    tempFile = '/tmp/ltaf_' + os.path.basename( testCaseTemplateFile.replace('.template', '.temp') )
           
    with open(testCaseTemplateFile, 'r') as fd:
        fc = fd.read()
        fc = fc.replace('R_RELEASENAME_R', release)
        fc = fc.replace('R_TESTSUITE_R', testsuite)
        fc = fc.replace('R_COMPONENT_R', component)
        fc = fc.replace('R_TESTCASETYPE_R', testCaseType)
        fc = fc.replace('R_FEATURE_R', feature)
        fc = fc.replace('R_ALLTESTCASE_R', '\n'.join(testNames))
        fc = fc.replace('R_CREATEDATE_R', testDate)
    
    with open(tempFile, 'w') as fd:
        fd.write(fc)
        
    return tempFile
    

def CreateTestRunFile(testCaseTemplateFile, spin_type, release, testName, testsuite, component, domain,
                      sprint, week, bsp, spin, testResult, tag, tester, board, build, buildOption, 
                      log, funcPass, funcFail, requirement=None):
    tempFile = '/tmp/ltaf_' + os.path.basename( testCaseTemplateFile.replace('.template', '.temp') ) 
           
    with open(testCaseTemplateFile, 'r') as fd:
        fc = fd.read()
        fc = fc.replace('R_RELEASENAME_R', release)
        
        fc = fc.replace('R_TESTCASE_R', testName)
        fc = fc.replace('R_TESTSUITE_R', testsuite)
        fc = fc.replace('R_COMPONENT_R', component)
        fc = fc.replace('R_DOMAIN_R', domain)
        
        fc = fc.replace('R_SPRINT_R', sprint)
        fc = fc.replace('R_WEEK_R', week)
        
        fc = fc.replace('R_BSP_R', bsp)
        fc = fc.replace('R_SPIN_R', spin)
        
        fc = fc.replace('R_TESTRESULT_R', testResult)
        fc = fc.replace('R_TAGS_R', tag)
        fc = fc.replace('R_TESTER_R', tester)
        fc = fc.replace('R_BOARD_R', board)

        fc = fc.replace('R_BUILD_R', build)
        fc = fc.replace('R_BUILDOPTIONS_R', buildOption)
        fc = fc.replace('R_LOG_R', log)
        
        fc = fc.replace('R_FUNCPASS_R', str(funcPass))
        fc = fc.replace('R_FUNCFAIL_R', str(funcFail))
        fc = fc.replace('R_SPINTYPE_R', str(spin_type))

        if requirement is not None:
            fc = fc.replace('R_REQUIREMENT_R', requirement)
        else:
            fc = fc.replace('R_REQUIREMENT_R', '')
    
    with open(tempFile, 'w') as fd:
        fd.write(fc)
        
    return tempFile


def GetTrendPng(fileName, release, tag, lastDayNum):
    startDate = AfterTodayStr(1-lastDayNum)
    endDate = TodayStr()
    cmdTrendPng = 'wget --timeout=7200 -O %s \"http://pek-lpgtest3.wrs.com/ltaf/nightly_interface.php?release_name=%s&f_type=chart&start_date=%s&end_date=%s&tags=%s\"' % (fileName, release, startDate, endDate, tag) 
    getoutput(cmdTrendPng)
    
