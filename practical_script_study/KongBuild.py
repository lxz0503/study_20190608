#!/usr/bin/env python

import os, sys, time
from commands import getoutput
from datetime import date

from Git import *
from Jenkins import GetLatestJobStatus, QueryBuildRunning
from KongConfig import *
from Jenkins import GetBuildStatusAndFullName

jenkinsSite = kongJenkins
user = 'svc-cmnet'
password = 'december2012!'
passwordFile = 'svc-cmnetPasswd.txt'


def CleanupImage():
    host = getoutput('hostname').strip()
    if host == GetImageServer():
        print 'clean up images at %s:%s' % (host, GetImageDir())
        os.chdir('%s' % GetImageDir())
        print getoutput('hostname; pwd; sudo rm -fr *')
        for bsp in GetSupportedBsps():
            print getoutput('hostname; pwd; mkdir -p %s' % bsp)
        
        
def SetSourceRepository(branch, commit):
    host = getoutput('hostname').strip()
    
    if host not in kongBuildServers: 
        print '%s is not build server' % host
        sys.exit(1)
        
    gitDir = kongBuildServers[host]['gitDir']
    if not os.path.exists(gitDir):
        print '%s:%s not existed' % (host, gitDir)
        sys.exit(2)
    
    git = Git(gitDir)
    if git.CurrentBranch() != branch:
        git.GotoBranch(branch, commit)
    elif git.CurrentCommitId() != commit:
        git.GotoBranch(branch, commit)
        
    currentBranch = git.CurrentBranch()
    currentCommit = git.CurrentCommitId()
    print '=== server:%s, branch:%s' % (host, currentBranch)
    print '=== server:%s, commit:%s' % (host, currentCommit)
    
    if currentBranch != branch:
        print 'cannot go to branch %s' % branch
        sys.exit(3)
    if currentCommit != commit:
        print 'cannot go to commit %s' % commit
        sys.exit(4)
    
    
def IsKongTestBusy():
    jenkinsWeb = 'http://128.224.159.246:8080'
    job = 'ci-manager'
    user = 'svc-cmnet'
    password = 'december2012!'
    status, _ = GetLatestJobStatus(jenkinsWeb, job, user, password)
    if status == 'INPROGRESS':
        return True
    else:
        return False

        
def LaunchBuildJob(branch, newCommit, module, bsp):
    """ return build Id """
    # must run as svc-cmnet at pek-cc-pb02l since using user ssh authentication 
    cmd = 'java -jar /net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/package/jenkins-cli.jar -s %s build %s \
          -p BRANCH=%s -p NEWCOMMIT=%s -p MODULE=%s -p BSP=%s -v -w --username %s --password %s' % (jenkinsSite, kongBuildJob, branch, newCommit, module, bsp, kongUser, kongPassword)
    print cmd
    ret = getoutput(cmd)
    print ret
    print
    lastLine = ret.split('\n')[-1].strip()
    if lastLine.startswith('Started '):
        words = lastLine.split(' ')
        return words[1], int(words[2].replace('#', ''))
    else:
        return kongBuildJob, None    


def WaitBuildJob():
    while QueryBuildRunning(kongJenkins, kongBuildJob, kongUser, kongPassword):
        time.sleep(60)


def CreateTarFile():
    for bsp in GetSupportedBsps():
        imgDir = '/net/%s/%s/%s' % (GetImageServer(), GetImageDir(), bsp)
        os.chdir(imgDir)
        for mod in kongBuildModules[bsp]:
            if os.path.exists(imgDir + '/' + mod):
                cvsPath = mod + '/cvs'
                CheckPath(cvsPath)
                vxworksPath = mod + '/%s_vip/default/vxWorks*' % bsp
                CheckPath(mod + '/%s_vip/default/vxWorks' % bsp)
                tool1 = mod + '/runtestsuite*.py'
                tool2 = mod + '/lockboard.py'
                CheckPath(tool2) 
                tool3 = mod + '/vlmTarget.py'
                CheckPath(tool3)
                tool4 = mod + '/shellUtils.py'
                CheckPath(tool4)
                os.system('rm -f %s.tar' % mod)
                if bsp == 'vxsim_linux':
                    if mod != 'SSH':
                        os.system('tar zcf %s.tar %s %s %s %s %s %s' % (mod, cvsPath, vxworksPath, tool1, tool2, tool3, tool4))
                    else:
                        os.system('tar zcf %s.tar %s %s %s %s %s' % (mod, mod + '/*', tool1, tool2, tool3, tool4))
                else:
                    imagePath = mod + '/%s_image' % bsp
                    CheckPath(imagePath)
                    if mod != 'SSH':
                        os.system('tar zcf %s.tar %s %s %s %s %s %s %s' % (mod, cvsPath, vxworksPath, tool1, tool2, tool3, tool4, imagePath))
                    else:
                        os.system('tar zcf %s.tar %s %s %s %s %s %s' % (mod, mod + '/*', tool1, tool2, tool3, tool4, imagePath))
                    
                os.system('chmod 755 *.tar')
            else:
                print 'required the built module %s not existed' % (imgDir + '/' + mod)
                #sys.exit(1)


def CheckPath(thePath):
    if not os.path.exists(thePath):
        print '%s not found' % thePath
        sys.exit(1)   

def test_CreateTarFile():
    CreateTarFile()

def CheckBuildJobResult(buildJobs):
    numFailure = 0
    for job, build in buildJobs:
        status, fullDisplayName = GetBuildStatusAndFullName(kongJenkins, job, build, user=kongUser, password=kongPassword)
        print '=== build:%s, status:%s' % (fullDisplayName, status)
        if status == 'FAILURE':
            numFailure += 1
    ratioFailure = '%s of %s' % (numFailure, len(buildJobs))
    print '=== summary: %s builds failed' % ratioFailure
    
    if numFailure < kongBuildFailureNum:
        return 0
    else:
        return -1
    
def BuildAllImage(branch, commit):
    if kongBuildFirstFlag:
        CleanupImage()
        
        buildJobs = []
        for bsp in GetSupportedBsps():
            # filter out SNTP_CLIENT to prevent concurrency from happening
            for mod in [x for x in kongBuildModules[bsp] if x != 'SNTP_CLIENT']:
                job, build = LaunchBuildJob(branch, commit, mod, bsp)
                buildJobs.append((job, build))
    
        WaitBuildJob()

        CreateTarFile()
        sys.exit( CheckBuildJobResult(buildJobs) )    
    
def main():
    if len(sys.argv) != 3:
        print 'usage: %s branch commit' % os.path.basename(sys.argv[0])
        sys.exit(1)
        
    branch = sys.argv[1]
    newCommit = sys.argv[2]
    BuildAllImage(branch, newCommit)

    
if __name__ == '__main__':
    #main()
    CreateTarFile()
    
