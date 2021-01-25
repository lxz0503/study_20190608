#!/usr/bin/env python

import os, sys, time
from commands import getoutput
from logging import *

from Config import *
from Git import *
from VsbBuild import *
from Utility import time_elapsed
from Jenkins import *
from ServerStatus import *


def LaunchJenkinsJob(branch, server, oldCommit, newCommit):
    """ return build Id """
    cmd = 'java -jar /folk/lchen3/package/jenkins-cli.jar -s http://pek-mcbuild2.wrs.com:8070 build vx7-dev-branch-build -p SERVER=%s -p BRANCH=%s -p OLDCOMMIT=%s -p NEWCOMMIT=%s  -v -w --username target --password vxTarget' % (server, branch, oldCommit, newCommit)
    print cmd
    buildId = 0
    ret = getoutput(cmd)
    print ret
    for line in ret.split('\n'):
        if line.startswith('Started '):
            buildId = (line.split('#'))[1]
    return int(buildId) # ? should return truely-build id
    

def CheckJobStatus(serverStatus):
    servers = serverStatus.GetServers()
    print serverStatus.status
    for svr in servers:
        buildId = serverStatus.GetServerStatus(svr)
        if buildId != 0:
            buildStatus = GetBuildStatus('http://pek-mcbuild2.wrs.com:8070', JenkinsJob.downstreamJob, buildId)
            if buildStatus != 'INPROGRESS':
                serverStatus.SetIdleServer(svr)
    

def InitServerStatus(svrStatus):
    rets = QueryBuildRunning('http://pek-mcbuild2.wrs.com:8070', JenkinsJob.downstreamJob)
    for (svr, status) in rets:
        svrStatus.SetBusyServer(svr, status)


def FindIdleServer(svrStatus):
    server = ''
    while True:
        server = svrStatus.GetIdleServer()
        print '\nget idle server=', server
        if server is None:
            CheckJobStatus(svrStatus)
            time.sleep(60*2)
        else:
            break
    return server


def SetServerStatus(svrStatus, server, buildId):
    jenkinsUrl = "http://pek-mcbuild2.wrs.com:8070"
    while (GetBuildStatus(jenkinsUrl, JenkinsJob.triggerJob, buildId) == 'INPROGRESS'):
        time.sleep(5)
    time.sleep(10)                    
    dsBuildId = GetDownStreamBuildId(jenkinsUrl, JenkinsJob.triggerJob, buildId, JenkinsJob.downstreamJob)
    if dsBuildId != 0:
        svrStatus.SetBusyServer(server, dsBuildId)
    else:
        print 'cannot find downstream build id'
        sys.exit(1)

        
@time_elapsed
def main():
    #basicConfig(level=INFO)
    svrStatus = ServerStatus()
    InitServerStatus(svrStatus)

    masterGit = Git(masterGitPath)
    os.chdir(masterGitPath)

    debugFlag = False
    for branch in branches:
        updatedFlag, oldCommit, newCommit = masterGit.UpdateBranch(branch)
        if updatedFlag or debugFlag:
            print '==== branch %s changed from commit %s to %s ====' % (branch, oldCommit, newCommit)
            server = FindIdleServer(svrStatus)
            buildId = LaunchJenkinsJob(branch, server, oldCommit, newCommit)
            SetServerStatus(svrStatus, server, buildId)


if __name__ == '__main__':
    main()
