#!/usr/bin/env python

import itertools
import os
import shutil
import sys
import time
import pprint

from jenkins import Jenkins

from commands import getoutput
from datetime import datetime
from KongConfig import kongJenkins, kongUser, kongPassword
from HelixConfig import bspBuildJobs, bspTestJobs, bspReportJobs, jobExecutors, jobNodes, helixBuildModules, helixTestPlanToReport
from HelixCommon import helixSupportedBsps, helixBuildModules, getJenkinsUrl, getImagePath, createTestArgument
from HelixReport import reportSummary, combineWithPredefine, getNotPassedTests 


"""
tasks = {
         'bsp1' : { # na, SUCCESS, FAILURE, INPROGRESS
                    'mod1' : [ ['build', S_NA, S_NA, S_NA],
                               ['test', S_NA, S_NA, S_NA],
                               ['report', S_NA, S_NA, S_NA],
                               ['retest', S_NA, S_NA, S_NA],
                               ['rereport', S_NA, S_NA, S_NA],
                             ], 
                  }, 
        }
"""

S_NA = 'na'
S_SUCCESS = 'SUCCESS'
S_FAIL = 'FAILURE'
S_INPROGRESS = 'INPROGRESS'

class Task:
    def __init__(self, branch, newCommit):
        self.server = None
        self.runningJobs = None
        self.nodeStates = {}
        self.tasks = {}
        self.branch = branch
        self.newCommit = newCommit
    
    
    def initTask(self, helixBuildModules):
        self.server = Jenkins(kongJenkins, kongUser, kongPassword)
        self.getNodeStates()
        for bsp in helixBuildModules:
            self.tasks[bsp] = {}
            for module in helixBuildModules[bsp]:
                self.tasks[bsp][module] = [ ['build',  S_NA, S_NA, S_NA],
                                            ['test',   S_NA, S_NA, S_NA],
                                            ['report', S_NA, S_NA, S_NA],
                                            ['retest',   S_NA, S_NA, S_NA],
                                            ['rereport', S_NA, S_NA, S_NA],
                                          ]


    def runTask(self):
        done = True
        # update running jobs for one runTask()
        # or frequently-used get_running_build() caused Jenkins to quit
        self.getRunningJobs()
        time.sleep(30)
        self.getNodeStates()
        moduleBsps = createModuleBsps(helixBuildModules)
        for mod, bsp in moduleBsps:
            doneMod = self.handleModule(bsp, mod)
            #print('\n=== handle module %s %s done=%s @ %s' % (bsp, mod, doneMod, datetime.now()))
            done = done and doneMod
        return done
    
         
    def handleModule(self, bsp, mod):
        done = True
        modTasks = self.tasks[bsp][mod]
        n = len(modTasks)
        i = 0
        while i < n:
            name, job, build, status = self.getModTaskContent(modTasks, i)
            doneTask, status = self.handleOneTask(bsp, mod, name, job, build, status)
            done = done and doneTask
            goFlag = self.goNextTask(name, status)
            #print('\t--- handle (%s %s) %s %s %s %s goFlag=%s doneTask=%s @ %s' % (bsp, mod, name, job, build, status, goFlag, doneTask, datetime.now()))
            i += 1
            if goFlag:
                continue
            else:
                break
        return done
        
        
    def handleOneTask(self, bsp, module, name, job, build, status):
        # return modTasks, doneTask, status
        doneTask = False
        
        offline = self.__isNodeOffline(bspTestJobs[bsp])
        if offline:
            self.updateTask(bsp, module, name, job, build, S_SUCCESS)
            doneTask = True
            return doneTask, status
        
        if name == 'build':
            if status == S_NA:
                if self.canJobRun(bspBuildJobs[bsp]):
                    job, build = LaunchHelixBuildJob(self.branch, self.newCommit, module, bsp)
                    status = S_INPROGRESS
                    self.updateTask(bsp, module, name, job, build, status)
                    doneTask = False
                else:
                    #print('\t\t*** skip build na')
                    doneTask = False
            elif status == S_INPROGRESS:
                status = getBuildStatus(self.server, job, build)
                self.updateTask(bsp, module, name, job, build, status)
                if status in (S_SUCCESS, S_FAIL,):
                    doneTask = True
                elif status in (S_INPROGRESS):
                    doneTask = False
            elif status in (S_SUCCESS, S_FAIL,):
                doneTask = True
        elif name == 'test':
            if status == S_NA:
                if self.canJobRun(bspTestJobs[bsp]):
                    tests = createTestArgument(module)
                    print('=== tests=%s' % tests)
                    job, build = LaunchHelixTestJob(self.branch, tests, module, bsp)
                    status = S_INPROGRESS
                    self.updateTask(bsp, module, name, job, build, status)
                    doneTask = False
                else:
                    #print('\t\t*** skip test na')
                    doneTask = False
            elif status == S_INPROGRESS:
                status = getBuildStatus(self.server, job, build)
                self.updateTask(bsp, module, name, job, build, status)
                if status in (S_SUCCESS, S_FAIL,):
                    doneTask = True
                elif status in (S_INPROGRESS):
                    doneTask = False
            elif status in (S_SUCCESS, S_FAIL,):
                doneTask = True
        elif name == 'report':
            if status == S_NA:
                if self.canJobRun(bspReportJobs[bsp]):
                    _, testJob, testBuild, _ = self.getTaskContent(bsp, module, 'test')
                    job, build = LaunchHelixReportJob(testJob, testBuild, module, bsp)
                    status = S_INPROGRESS
                    self.updateTask(bsp, module, name, job, build, status)
                    doneTask = False
                else:
                    #print('\t\t*** skip report na')
                    doneTask = False
            elif status == S_INPROGRESS:
                status = getBuildStatus(self.server, job, build)
                self.updateTask(bsp, module, name, job, build, status)
                if status in (S_SUCCESS, S_FAIL,):
                    doneTask = True
                elif status in (S_INPROGRESS):
                    doneTask = False
            elif status in (S_SUCCESS, S_FAIL,):
                doneTask = True
        elif name == 'retest':
            if status == S_NA:
                _, testJob, testBuild, testStatus = self.getTaskContent(bsp, module, 'test')
                if testStatus == S_FAIL:
                    if self.canJobRun(bspTestJobs[bsp]):
                        notPassedTests = ','.join(getNotPassedTests(module, testJob, testBuild))
                        print('=== notPassedTests=%s' % notPassedTests)
                        job, build = LaunchHelixTestJob(self.branch, notPassedTests, module, bsp)
                        status = S_INPROGRESS
                        self.updateTask(bsp, module, name, job, build, status)
                        doneTask = False
                    else:
                        #print('\t\t*** skip test na')
                        doneTask = False
                elif testStatus == S_SUCCESS:
                    self.updateTask(bsp, module, 'retest', S_NA, S_NA, S_SUCCESS)
                    doneTask = True
            elif status == S_INPROGRESS:
                status = getBuildStatus(self.server, job, build)
                self.updateTask(bsp, module, name, job, build, status)
                if status in (S_SUCCESS, S_FAIL,):
                    doneTask = True
                elif status in (S_INPROGRESS):
                    doneTask = False
            elif status in (S_SUCCESS, S_FAIL,):
                doneTask = True
        elif name == 'rereport':
            if status == S_NA:
                _, testJob, testBuild, testStatus = self.getTaskContent(bsp, module, 'retest')
                if testJob != S_NA:
                    if self.canJobRun(bspReportJobs[bsp]):
                        job, build = LaunchHelixReportJob(testJob, testBuild, module, bsp)
                        status = S_INPROGRESS
                        self.updateTask(bsp, module, name, job, build, status)
                        doneTask = False
                    else:
                        #print('\t\t*** skip report na')
                        doneTask = False
                elif testStatus == S_SUCCESS:
                    self.updateTask(bsp, module, 'rereport', S_NA, S_NA, S_SUCCESS)
                    doneTask = True                    
            elif status == S_INPROGRESS:
                status = getBuildStatus(self.server, job, build)
                self.updateTask(bsp, module, name, job, build, status)
                if status in (S_SUCCESS, S_FAIL,):
                    doneTask = True
                elif status in (S_INPROGRESS):
                    doneTask = False
            elif status in (S_SUCCESS, S_FAIL,):
                doneTask = True
        return doneTask, status
    
    
    def getModTaskContent(self, tasks, n):
        return tasks[n]
    
    
    def getTaskContent(self, bsp, mod, index):
        assert index in ('build', 'test', 'report', 'retest', 'rereport')
        if self.tasks:
            for item in self.tasks[bsp][mod]:
                if item[0] == index:
                    return item
        else:
            raise Exception('the task content is empty')
    
    
    def updateTask(self, bsp, module, name, job, build, status):
        modTasks = self.tasks[bsp][module]
        newModTasks = []
        for items in modTasks:
            if items[0] == name:
                newModTasks.append([name, job, build, status])
            else:
                newModTasks.append(items)
        self.tasks[bsp][module] = newModTasks
        
        
    def goNextTask(self, name, status):
        if name == 'build':
            if status in (S_SUCCESS,):
                return True
            elif status in (S_NA, S_FAIL, S_INPROGRESS,):
                return False
        elif name == 'test':
            if status in (S_SUCCESS, S_FAIL,):
                return True
            elif status in (S_NA, S_INPROGRESS,):
                return False
        elif name == 'report':
            if status in (S_SUCCESS, S_FAIL,):
                return True
            elif status in (S_NA, S_INPROGRESS,):
                return False
        elif name == 'retest':
            if status in (S_SUCCESS, S_FAIL,):
                return True
            elif status in (S_NA, S_INPROGRESS,):
                return False
        elif name == 'rereport':
            if status in (S_SUCCESS, S_FAIL,):
                return True
            elif status in (S_NA, S_INPROGRESS,):
                return False
        else:
            raise Exception('ERROR: %s status %s not supported' % (name, status))


    def getRunningJobs(self):
        self.runningJobs = [x['name'] for x in self.server.get_running_builds()]
        #print('\trunning jobs=%s' % self.runningJobs)


    def getNodeStates(self):
        nodes = self.server.get_nodes()
        for x in nodes: 
            self.nodeStates[x['name']] = x['offline']
    

    def canJobRun(self, job):
        if job in jobExecutors:
            num = len(filter(lambda x:x == job, self.runningJobs))
            #print('\t\t*** %s:%s' % (job, num))
            if num < jobExecutors[job]:
                self.runningJobs.append(job)
                return True
            else:
                return False
        else:
            raise Exception('the job %s not found at jobExcutors in HelixConfig.py' % job)
  

    def __isNodeOffline(self, job):
        node = jobNodes[job]
        state = self.nodeStates[node]
        if state:
            print('ERROR: the node %s of job %s is offline' % (node, job))
        return state
    
    
def getBuildStatus(theJenkins, jobName, buildId):
    """ return the status of a build of a Jenkins job
        status: SUCCESS, FAILURE, INPROGRESS (None) and latest job number
    """
    if buildId is None:
        return ''
    
    retJson = theJenkins.get_build_info(jobName, buildId)

    if retJson.has_key('result') and retJson.has_key('number'):
        status = retJson['result']
        if status is None:
            status = 'INPROGRESS'
        return status
    else:
        print '%s has no keys for either result or number' % jobName
        return ''


def LaunchHelixBuildJob(branch, newCommit, module, bsp):
    job = 'helix-build-slave'
    print('\t\t*** launch build job for %s %s' % (bsp, module))
    return LaunchHelixJob(job, branch, newCommit, module, bsp)


def LaunchHelixTestJob(branch, newCommit, module, bsp):
    assert bsp in helixSupportedBsps
    print('\t\t*** launch test job for %s %s' % (bsp, module))
    if bsp == 'itl_generic':
        job = 'helix-test-itl_generic'
    elif bsp == 'nxp_layerscape_a72':
        job = 'helix-test-nxp_layerscape_a72'
    elif bsp == 'xlnx_zynqmp':
        job = 'helix-test-xlnx_zynqmp'
    #newCommit = createTestArgument(module)
    return LaunchHelixJob(job, branch, newCommit, module, bsp)


def LaunchHelixReportJob(branch, newCommit, module, bsp):
    print('\t\t*** launch report job for %s %s' % (bsp, module))
    return LaunchHelixJob('helix-report', branch, newCommit, module, bsp)


def LaunchHelixJob(job, branch, newCommit, module, bsp):
    """ return build Id """
    # must run as svc-cmnet at pek-cc-pb02l since using user ssh authentication 
    cmd = 'java -jar /net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/package/jenkins-cli.jar -s %s build %s \
          -p BRANCH=%s -p NEWCOMMIT=%s -p MODULE=%s -p BSP=%s -v -w --username %s --password %s' % (kongJenkins, job, branch, newCommit, module, bsp, kongUser, kongPassword)
    print('%s @ %s' % (cmd, datetime.now()))
    startTime = time.time()
    ret = getoutput(cmd)
    print('%s @ using %.1f seconds' % (ret, time.time() - startTime))

    lastLine = ret.split('\n')[-1].strip()
    if lastLine.startswith('Started '):
        words = lastLine.split(' ')
        theJob = words[1]
        theBuild = int(words[2].replace('#', ''))
        print('%s\n' % getJenkinsUrl(theJob, theBuild))
        return theJob, theBuild
    else:
        return job, None    


def createModuleBsps(helixBuildModules):
    buildModules = []
    n = 0
    for bsp in helixBuildModules:
        buildModules.append( zip(list(helixBuildModules[bsp]), [bsp] * len(helixBuildModules[bsp])) )
        n += len(helixBuildModules[bsp])
    
    retModules = buildModules.pop()
    for bspMods in buildModules:
        retModules = list(itertools.chain.from_iterable(itertools.izip_longest(retModules, bspMods)))
    retModules = filter(lambda x: x is not None, retModules)
    
    assert n == len(retModules)
    return retModules


def cleanupBuildImage():
    imagePath = getImagePath()
    shutil.rmtree(imagePath)
    os.mkdir(imagePath)


def checkHelixConfig():
    # check bsp*Jobs and jobExecutors
    jobs = list( set(bspBuildJobs.values() + bspTestJobs.values() + bspReportJobs.values()) )
    for j in jobs:
        if j not in jobExecutors:
            raise Exception('%s from bspBuildJobs / bspTestJobs / bspReportJobs not in jobExecutors' % j)
    # check helixBuildModules and helixSupportedBsps
    for bsp in helixBuildModules:
        if bsp not in helixSupportedBsps:
            raise Exception('%s from helixBuildModules not in helixSupportedBsps' % bsp)
    # check helixBuildModules and helixTestPlanToReport
    for bsp in helixBuildModules:
        for mod in helixBuildModules[bsp]:
            if mod not in helixTestPlanToReport:
                raise Exception('%s from helixBuildModules not in helixTestPlanToReport' % mod)
            
    
def main():
    # HelixManager.py $BRANCH $NEWCOMMIT
    # check arguments
    if len(sys.argv) != 3:
        print('\nusage:%s $BRANCH $NEWCOMMIT')
        sys.exit(1)
    
    branch, newCommit = sys.argv[1], sys.argv[2]

    cleanupBuildImage()
    checkHelixConfig()

    t = Task(branch, newCommit)
    t.initTask(helixBuildModules)
    pp = pprint.PrettyPrinter(indent=2, width=126)
    pp.pprint(t.tasks)    
    waitTime = 60
    printWaitTime = 300
    i = 0
    
    while True:
        done = t.runTask()
        if i >= printWaitTime:
            print('\n%s' % datetime.now())
            pp.pprint(t.tasks)
            i = 0
        if done:
            break
        else:
            time.sleep(waitTime)
            i += waitTime
    
    #reportSummary(t.tasks)

if __name__ == '__main__':
    main()
    