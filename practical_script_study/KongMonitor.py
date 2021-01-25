#!/usr/bin/env python

import os, sys, time
from commands import getoutput
from datetime import date

from Git import *
from Utility import time_elapsed
from Jenkins import IsAnyProjectRunning

jenkinsSite = 'http://128.224.159.246:8080'

gitToMonitor = '/buildarea2/lchen3/workspace/vx7-dev-nightly/vxworks'

branchesToMonitor = ['fr43-crypto-fips',
                     'vx7-network-defect-sprint27',
                     'fr43-crypto-fips',
                     'vx7-netperf-exp',
                     'vx7-release',
                     'vx7-network-defect-sprint27',
                     'fr43-crypto-fips',
                     ]


def ScheduleBranch(branches):
    # return a list with each element as the first element in turns
    # the more same branch, the higher priority to check with
    assert type(branches) == list
    n = len(branches)
    i = date.today().toordinal() % n
    #i = branchesToMonitor.index('vx7-release')
    return branches[i:] + branches[0:i]
    
    
def LaunchJenkinsJob(branch):
    """ return build Id """
    cmd = 'java -jar /folk/lchen3/package/jenkins-cli.jar -s http://128.224.159.246:8080 build vxworks-vx7-install -p BRANCH=%s -v -w --username svc-cmnet --password december2012!' % branch
    print cmd
    ret = getoutput(cmd)
    print ret
    

@time_elapsed
def main():
    git = Git(gitToMonitor)
    os.chdir(gitToMonitor)
    user = 'svc-cmnet'
    password = 'december2012!'
    
    while( IsAnyProjectRunning(jenkinsSite, user, password) ):
        secs = 60
        #print 'waiting %s seconds ...' % secs
        time.sleep(secs)
        
    for branch in ScheduleBranch(branchesToMonitor):
        updated, oldCommit, newCommit = git.UpdateBranch(branch)
        if updated:
            print '==== branch %s changed from commit %s to %s ====' % (branch, oldCommit, newCommit)
            LaunchJenkinsJob(branch)
            time.sleep(30) # only handle one branch according to the sequence in branchesToMonitor
            if IsAnyProjectRunning(jenkinsSite, user, password): 
                break


if __name__ == '__main__':
    main()
