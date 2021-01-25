#!/usr/bin/env python

# TO-DO :
#    1) not cover the case below
#ipnet.windview.udp                        FAILED
#ipnet.windview.udp - IPv4 ETA: 1s                                           ipnet.windview.udp test case failed  failed
#ipnet.windview.udp - IPv6 ETA: 1s                                           OK 1s
#
#    2) not consider extracting the skipped test cases

import re, sets, commands
from sys import exit
from operator import itemgetter

from Jenkins import *
from Git import *
from Mail import *
from Config import *
from KongRerunTest import *
from KongConfig import *


def NotifyEmail(branch, commit, modules, testCases, buildUrl, buildInfo):
    fromEmail, toEmail, subject, body = PrepareEmail(branch, commit, modules, testCases, buildUrl, buildInfo)
    if kongDebugOn:
        print 'toEmail:%s' % toEmail
        toEmail = 'libo.chen@windriver.com'
    print '%s to send email' % SendEmail(fromEmail, toEmail, subject, body)
    

def PrepareEmail(branch, commit, modules, testCases, buildUrl, buildInfo):
    if branch.startswith('SPIN:'):
        assert commit in spinConfig.keys()
        spin = branch.replace('SPIN:'+ spinConfig[commit]['spinToDir'] + '/', '')
        fromEmail = 'libo.chen@windriver.com'
        toEmail = 'libo.chen@windriver.com'
        subject = 'KONG Vx7 TEST REPORT FOR SPIN %s' % spin
        body = 'NETWORK KONG TEST REPORT FOR SPIN %s\n\n' % spin
    else:
        fromEmail, toEmail, author, commitInfo = CreateEmailList(branch, commit, commit)
        subject = 'KONG Vx7 TEST REPORT FOR BRANCH %s COMMIT %s BY %s' % (branch, commit[0:7], author)
        body = 'NETWORK KONG TEST REPORT FOR THE FOLLOWING COMMIT\n\n'
        body = body + '\t The branch is %s\n\n' % branch 
        body = body + '\n'.join(['\t%s' % x for x in commitInfo.split('\n')]) + '\n\n'
        body = body + 'IS:\n'  
    p, f, s = CategorizeTestCaseResult(testCases)
    body = body + '\tTOTAL: %s all, %s ok, %s failed, %s skipped. See %s\n' % (p+f+s, p, f, s, buildUrl)
    if buildInfo != '':
        body = body + '\tWARNING: %s\n\n' % buildInfo
    body = body + '\tDetailed test cases:\n'
    for x in testCases: body = body + '\t\t%s, %s\n' % (x[0], x[1])
    body = body + '\tModules:\n'
    for x in modules: body = body + '\t\t%s\n' % x
    return fromEmail, toEmail, subject, body


def CreateEmailList(branch, oldCommit, newCommit):
    currentHost = commands.getoutput('hostname').split('.')[0]
    firstHost = kongBuildServers.keys()[0]
    if currentHost == firstHost:
        git = Git(kongBuildServers[firstHost]['gitDir'])
    else:
        git = Git('/net/%s' % firstHost + kongBuildServers[firstHost]['gitDir'])
        
    git.GotoBranch(branch, newCommit)
    _, theAuthor, _, _, commitInfo, mergeCommitFlag = git.CommitInfo(newCommit)
    authorEmails = git.GetAuthors(oldCommit, newCommit)
    
    mgrEmails, toEmails = sets.Set(), sets.Set()
    for an, ae in authorEmails:
        if not ae.endswith('@windriver.com'):
            author = an
            authorEmail = ae
            
            authorCorpEmail = GetCorpEmail(author)
            if authorEmail != '':
                toEmails.add(authorCorpEmail)
            else:
                toEmails.add(authorEmail)
                
            mgrEmail = GetMgrEmail(author)
            if mgrEmail != '':
                mgrEmails.add(mgrEmail)
        else:
            toEmails.add(ae)
            
    fromEmail = 'libo.chen@windriver.com'
    mgrMails = sets.Set()
    if (list(toEmails) + list(mgrEmails)):
        toEmail = ';'.join(list(toEmails) + list(mgrEmails)) + ';' + kongAdminEmail
    else:
        toEmail = kongAdminEmail
        
    if mergeCommitFlag:
        toEmail = 'ENG-VxNET-China@windriver.com' + ';' + kongAdminEmail
    else:
        toEmail = toEmail + ';ENG-VxNET-China@windriver.com'
    toEmail = ';'.join( UniqueList( map(lambda x: x.strip(), toEmail.split(';')) ) )
    return fromEmail, toEmail, theAuthor, commitInfo


def UniqueList(theList):
    return list( sets.Set( theList ) )


def SumModTest(mergedTestResults):
    # sumTestResults = { bsp1 : [ allTestResults ], bsp2 : [ allTestResults ], ... }
    def __GetUniquePairs(thePairs):
        retPairs = {}
        for testName, testResult in thePairs:
            if testName not in retPairs:
                retPairs[testName] = (testName, testResult)
            else:
                if retPairs[testName][1] == testResult:
                    continue
                else:
                    # same test name with different test results
                    if retPairs[testName][1].lower() == 'ok':
                        continue
                    else:
                        print '|NOTE|: test name "%s" uses optimal test result "%s"' % (testName, testResult)
                        retPairs[testName] = (testName, testResult)
        pairList = retPairs.values()
        return sorted(pairList, key=itemgetter(0))
    
    sumTestResults = {}
    for bsp in mergedTestResults:
        if bsp not in sumTestResults:
            sumTestResults[bsp] = []
        for mod in mergedTestResults[bsp]:
            sumTestResults[bsp] += mergedTestResults[bsp][mod]
        print '\nsum len=', len(sumTestResults[bsp])
        sumTestResults[bsp] = __GetUniquePairs(sumTestResults[bsp])
        print 'sum unique len=', len(sumTestResults[bsp])
    return sumTestResults


def PrintSummary(mergedTestResults):
    # mergedTestResults : see the definition at MergeTestResult()
    totalOk, totalFail, totalSkip = 0, 0, 0
    sumTestResults = SumModTest(mergedTestResults)
    for bsp in sumTestResults.keys():
        numOk, numFail, numSkip = CategorizeTestCaseResult(sumTestResults[bsp])
        totalOk   += numOk
        totalFail += numFail
        totalSkip += numSkip
    print '\nTOTAL for bsp %s:\ntotal %s, pass %s, fail %s, skip %s' % (sumTestResults.keys(), totalOk + totalFail + totalSkip, 
                                                                      totalOk, totalFail, totalSkip)

    for bsp in sumTestResults.keys():
        numOk, numFail, numSkip = CategorizeTestCaseResult(sumTestResults[bsp])
        total = numOk + numFail + numSkip
        print '\nDetailed test cases for %s: total %s, pass %s, fail %s, skip %s' % (bsp, total, numOk, numFail, numSkip)
        for x in sumTestResults[bsp]: print '\t%s, %s' % (x[0], x[1])
        print
        print 'Modules for %s:' % bsp
        for x in mergedTestResults[bsp]: print '\t%s' % x
            
            
def FindUniqueJob(reruns):
    rerunJobBuilds = []
    for bsp in reruns:
        for mod in reruns[bsp]:
            for job, build in reruns[bsp][mod]:
                rerunJobBuilds.append( (job, build) )
    return rerunJobBuilds
    
def main():
    if len(sys.argv) != 4:
        print 'usage: %s buildNumber branch commit' % (os.path.basename(sys.argv[0]))
        exit(1)
        
    multiJobProject = 'ci-manager'
    jobName = 'ci-summary'
    buildId = int(sys.argv[1])
    branch = sys.argv[2]
    commit = sys.argv[3]

    parentBuildId = GetParentBuildIdFromMultiJob(kongJenkins, multiJobProject, jobName, buildId, kongUser, kongPassword)
    print 'parentBuildId:', parentBuildId

    utJobBuilds = GetRunTestJobBuild(jenkinsWeb, multiJobProject, parentBuildId)
    # parse run-test jobs
    testResults = GetJobTestResult(utJobBuilds)
    # create rerun tests
    rerunTests = CreateRerunTest(testResults, kongTestPlanToReport)
    # run rerun tests
    reruns = RerunTest(branch, commit, rerunTests, debugReruns=None)
    
    rerunJobBuilds = FindUniqueJob(reruns)
    # parse rerun test
    rerunTestResults = GetJobTestResult(rerunJobBuilds)    
    # summarize both run-test ad rerun tests
    mergedTestResults = MergeTestResult(testResults, rerunTestResults)
    # output final test results
    PrintSummary(mergedTestResults)
    

if __name__ == '__main__':
    main()
