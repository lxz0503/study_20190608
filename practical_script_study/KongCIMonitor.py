#!/usr/bin/env python

# run at pek-cc-pb02l instead of pek-cc-pb05l

import os, sys, time
import KongConfig

from commands import getoutput
from datetime import date, datetime

from Git import *
from KongUtil import ElapsedTime
from Jenkins import GetLatestJobStatus

import KongConfig
from InstallSpin import InstallSpin, InstallLicense, GetSpinInfo
from InstallKongPatch import InstallKongPatch

jenkinsSite = 'http://pek-testharness-s1.wrs.com:8080'
user = 'svc-cmnet'
password = 'december2012!'

gitToMonitor = '/buildarea1/svc-cmnet/vxworks-latest' # locat at pek-vx-nwk1

                     
def IsKongTestBusy():
    job = 'ci-manager'
    user = 'svc-cmnet'
    password = 'december2012!'
    status, _ = GetLatestJobStatus(jenkinsSite, job, user, password)
    if status == 'INPROGRESS':
        return True
    else:
        return False


def IsCertJobBusy():
    job = 'vxcert-ci-manager'
    status, _ = GetLatestJobStatus(jenkinsSite, job, user, password)
    if status == 'INPROGRESS':
        return True
    else:
        return False
        
        
def LaunchJenkinsJob(branch, oldCommit, newCommit):
    """ return build Id """
    print('=== LaunchJenkinsJob(): branch=%s, oldCommit=%s, newCommit=%s' % (branch, oldCommit, newCommit))
    if branch == 'vx7-cert':
        job = 'vxcert-ci-manager'
        branch = 'vx7-cert'
        cmd = 'java -jar /folk/lchen3/package/jenkins-cli.jar -s %s build %s \
               -p BRANCH=%s -p NEWCOMMIT=%s -v -w --username %s --password %s' % (jenkinsSite, job, branch, \
               newCommit, user, password)
    else:
        if newCommit in ('HELIXSPIN', 'HELIXCISPIN'):
            job = 'helix-manager'
        else:
            job = 'ci-manager'
        cmd = 'java -jar /folk/lchen3/package/jenkins-cli.jar -s %s build %s \
               -p BRANCH=%s -p NEWCOMMIT=%s -v -w --username %s --password %s' % (jenkinsSite, job, branch, \
               newCommit, user, password)
    print cmd
    ret = getoutput(cmd)
    print ret
    

@ElapsedTime
def main():
    now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    
    nightlyOn = False
    
    if (len(sys.argv) == 3) and (sys.argv[1] == '--nightly'):
        nightlyOn = True
        print '\n\n====== %s NIGHTLY TEST RUN ======' % now
    else:
        print '\n\n====== %s COMMIT TEST RUN ======' % now
        
    if nightlyOn:
        branch = sys.argv[2]
        if branch in KongConfig.branchesForNightly:
            if branch in KongConfig.spinConfig.keys():
                spin = GetSpinInfo(branch, 'name')
                spinIndicator = branch
                                        
                if spin:
                    print '=== start to install %s spin:%s' % (spinIndicator, spin)
                    ret, result = InstallSpin(KongConfig.spinConfig[branch]['fromBaseDir'],
                                              KongConfig.spinConfig[branch]['spinToDir'], 
                                              spin, 
                                              KongConfig.spinConfig[branch]['profile'])
                    if ret != 0:
                        print '=== fail  to install %s spin:%s' % (spinIndicator, spin)
                        print '=== result:', result
                        sys.exit(1)
                    print '=== done  to install %s spin:%s' % (spinIndicator, spin)

                    print '=== start to install license'
                    ret, result = InstallLicense(KongConfig.spinConfig[branch]['spinToDir'], spin)
                    if ret != 0:
                        print '=== fail  to install license'
                        print '=== result:', result
                        sys.exit(1)
                    print '=== done  to install license'
                    
                    print '=== start to install Kong patch from the branch %s' % KongConfig.spinConfig[branch]['gitPathRef']
                    if branch == '653SPIN':
                        version = 653
                    else:
                        version = 7
                    InstallKongPatch(KongConfig.spinConfig[branch]['spinToDir'] + '/' + spin, 
                                     KongConfig.spinConfig[branch]['gitPathRef'], 
                                     KongConfig.spinConfig[branch]['spinBranch'],
                                     version)
                    print '=== done  to install Kong patch'

                    LaunchJenkinsJob('SPIN:' + KongConfig.spinConfig[branch]['spinToDir'] + '/' + spin, 'none', branch)
                else:
                    print '=== no %s spin to install' % spinIndicator

            else:
                if IsKongTestBusy():
                    print 'Kong test is busy now, quit'
                    sys.exit(0)            

                git = Git(gitToMonitor)
                os.chdir(gitToMonitor)
                updated, oldCommit, newCommit = git.UpdateBranch(branch)
                print '==== nightly: branch %s changed from commit %s to %s ====' % (branch, oldCommit, newCommit)
                LaunchJenkinsJob(branch, oldCommit, newCommit)
        else:
            print '=== nightly: branch %s not in the list of branchesForNightly' % branch
            
    else:
        for branch in KongConfig.branchesToMonitor:
            if branch != 'vx7-cert':
                if IsKongTestBusy():
                    print 'Kong test is busy now, quit'
                    sys.exit(0)            
            else:
                if IsCertJobBusy():
                    print 'Cert job is busy now, quit'
                    sys.exit(0)

            git = Git(gitToMonitor)
            os.chdir(gitToMonitor)                    
            updated, oldCommit, newCommit = git.UpdateBranch(branch)
            if updated:
                print '==== branch %s changed from commit %s to %s ====' % (branch, oldCommit, newCommit)
                LaunchJenkinsJob(branch, oldCommit, newCommit)
                break # check only one branch code changes


if __name__ == '__main__':
    main()
