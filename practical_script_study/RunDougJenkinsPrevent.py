#!/usr/bin/env python

import os, re, time

from sys import exit
from commands import getoutput
from operator import itemgetter

from jenkinsapi.jenkins import Jenkins
from jenkinsapi import api

from Jenkins import GetQueuedJobs, GetBuildConsole, GetUpStreamBuildId
from Coverity import ExtractPreventSummary
from Mail import SendEmail
from Git import *
from Config import *

class config:
    jenkinsUrl = 'http://ala-analysis.wrs.com:8080'
    job = 'Feature Branch File Build - Coverity'
    user = 'target'
    password = 'vxTarget'


def main():
    branch = ParseArgument()
    emails = GetEmail()
    print 'toemails:', emails
    RunDougJenkinsPrevent(branch, emails)


def ParseArgument():
    if len(sys.argv) != 2:
        print 'usage: %s branch' % os.path.basename(sys.argv[0])
        exit(1)
    return sys.argv[1]
       
        
def GetEmail():
    # get send-to-emails Jenkins upstream job; format is == email to: ;libo.chen@windriver.com
    defaultEmail = 'libo.chen@windriver.com'
    buildId = int(os.environ.get('BUILD_NUMBER', '-1'))
    print 'BUILD_NUMBER=', buildId
    if buildId == -1:
        print '=== not running at a Jenkins job'
        return defaultEmail
    
    jobName = 'vx7-dev-branch-run-Doug-prevent'        
    upStreamJob = 'vx7-dev-branch-truely-build'
    usBuildId = GetUpStreamBuildId('http://pek-mcbuild2.wrs.com:8070', jobName, buildId, upStreamJob, config.user, config.password)
    usResult = GetBuildConsole('http://pek-mcbuild2.wrs.com:8070', upStreamJob, usBuildId)
    found = re.search('== email to:(.*?)\n', usResult)
    if found is not None:
        emails = found.groups()[0].strip()
    else:
        emails = defaultEmail
    return emails
    

def RunDougJenkinsPrevent(branch, emails):
    while True:
        currentQueueJobs = RetrieveQueue()
        LaunchFeatureBranchPreventBuild(branch)
        buildId = GetLaunchedBuildId(currentQueueJobs)
        print 'build id: %s' % buildId
        if buildId != -1:
            break
        nsec = 60*5
        print 're-launched the build after waiting %s seconds' % nsec
        time.sleep(nsec)

    WaitTriggeredBuild(buildId)
    NotifyUser(branch, buildId, emails)
    

def RetrieveQueue():
    j = Jenkins(config.jenkinsUrl, username=config.user, password=config.password)
    q = j.get_queue()
    return GetQueuedJobs(q)
    
    
def LaunchFeatureBranchPreventBuild(branch):
    target1 = 'buildvsb_vsbbsp_smp-bsp6x_itl_x86-gnu' # buildvsb_vsbbsp-itl_64-gnu-SMP
    target2 = 'buildvsb_vsbbsp-fsl_p1p2-diab' # buildvsb_vsbbsp-bsp6x_fsl_p2020_rdb-diab
    target3 = 'buildvsb_vsbbsp-fsl_imx6-diab'
    if branch == 'fr64-vx7-ppc64':
        target1 = 'buildvsb_vsbAllLayerbsp_lp64-fsl_p3p4p5-diab'
        target2 = 'buildvsb_vsbAllLayerbsp_lp64-fsl_t2t4-diab'
        target3 = 'buildvsb_vsbAllLayerbsp_lp64-fsl_t1-diab'
        target4 = 'buildvsb_vsbAllLayerbsp_lp64-qsp_ppc-diab'
        cmd = 'java -jar /folk/lchen3/package/jenkins-cli.jar -s %s build \"%s\" -p BRANCH2BUILD=%s -p MAKE_TARGETS=\"%s %s %s %s\" -v --username %s --password %s' % (config.jenkinsUrl, config.job, branch, target1, target2, target3, target4, config.user, config.password)
    else:
        cmd = 'java -jar /folk/lchen3/package/jenkins-cli.jar -s %s build \"%s\" -p BRANCH2BUILD=%s -p MAKE_TARGETS=\"%s %s %s\" -v --username %s --password %s' % (config.jenkinsUrl, config.job, branch, target1, target2, target3, config.user, config.password)
    print cmd
    print getoutput(cmd)


def GetLaunchedBuildId(currentQueueJobs):
    print '=== old queue:%s\n' % currentQueueJobs
    j = Jenkins(config.jenkinsUrl, username=config.user, password=config.password)
    newQueueJobs = RetrieveQueue()
    print '=== new queue:%s\n' % newQueueJobs
    
    if len(newQueueJobs) == 0:
        return j.get_job(config.job).get_last_buildnumber()
    else:
        diffJobs = DiffList(currentQueueJobs, newQueueJobs)
        diffJobs = sorted(diffJobs, key=itemgetter(3))  
        print '=== diff queue:%s\n' % diffJobs

        n = len(diffJobs)
        if n == 0:
            print '=== WARNING: the build is not launched'
            return -1   # -1 means not launched
        elif n > 1:
            print '=== WARNING: difficult to identify which job is just launched since %s different jobs' % n
        return j.get_job(config.job).get_last_buildnumber() + len(newQueueJobs)


def DiffList(list1, list2):
    # return a list which is list2 is different than list1
    rets = []
    if len(list1) > len(list2):
        l1, l2 = list2, list1
    else:
        l1, l2 = list1, list2
    for x in l2:
        if x not in l1:
            rets.append(x)
    return rets   


def WaitTriggeredBuild(buildId):
    while True:
        j = Jenkins(config.jenkinsUrl, username=config.user, password=config.password)
        job = j.get_job(config.job)
        if job.get_last_buildnumber() >= buildId:
            break
        print 'waiting build %s to run...' % buildId
        time.sleep(60*5)

    j = Jenkins(config.jenkinsUrl, username=config.user, password=config.password)
    job = j.get_job(config.job)
    build = job.get_build(buildId)

    print job.is_running()
    print build.is_running()
    print build.get_status()
    
    while build.get_status() is None: # None means job is running
        j = Jenkins(config.jenkinsUrl, username=config.user, password=config.password)
        job = j.get_job(config.job)
        build = job.get_build(buildId)    
        print 'waiting running build %s to finish...' % buildId
        time.sleep(60*5)
    

def NotifyUser(branch, buildId, toEmail):
    fromEmail = 'libo.chen@windriver.com'
    consoleOutput = GetBuildConsole(config.jenkinsUrl, config.job, buildId)
    preventSummary = ExtractPreventSummary(consoleOutput)
    subject = 'Doug Egan Jenkins Prevent Checking for Vx7 branch %s build %s is done' % (branch, buildId)
    buildUrl = config.jenkinsUrl + '/job/' + config.job + '/' + str(buildId)
    content = '<' + buildUrl + '>' + '\n\n' + preventSummary
    print '== subject:', subject
    print '== summary:', content
    print '== email to: %s' % toEmail
    
    debugFlag = False
    if debugFlag:
        toEmail = fromEmail
        status = SendEmail(fromEmail, toEmail, subject, content)
    else:
        status = SendEmail(fromEmail, toEmail, subject, content)
        
    if status:
        print 'Succeed to send email'
    else:
        print 'Failed to send email'     


def RunWait():
    buildId = 297
    j = Jenkins(config.jenkinsUrl, username=config.user, password=config.password)
    job = j.get_job(config.job)
    build = job.get_build(buildId)    
    while build.get_status() is None: # None means job is running
        j = Jenkins(config.jenkinsUrl, username=config.user, password=config.password)
        job = j.get_job(config.job)
        build = job.get_build(buildId)    
        print 'waiting running build %s to finish...' % buildId
        time.sleep(10)
            
if __name__ == '__main__':    
    main()        
    #RunWait()
    
