#!/usr/bin/env python

import os, sys, argparse, time, re, sets
from commands import getoutput
from logging import *
#from dateutil import parser

class Git(object):
    def __init__(self, gitDir):
        self.prevDir = os.getcwd()
        if not os.path.exists(gitDir):
            print '%s not exist' % gitDir
            sys.exit(1)
        else:
            output = getoutput('cd %s; git log -1 HEAD' % gitDir)
            if output.find('Not a git repository') != -1:
                print '%s is not a git repository' % gitDir
                sys.exit(2)
            else:
                self.gitDir = gitDir

    def GotoBranch(self, branch, commit=None):
        os.chdir(self.gitDir)
        getoutput('git pull')   # git pull first to sync up with remote repository
        getoutput('git checkout %s' % branch)
        if commit is not None:
            getoutput('git reset --hard %s' % commit)

    def CurrentBranch(self):
        os.chdir(self.gitDir)
        result = getoutput('git branch')
        lines = [x.strip() for x in result.split('\n') if x.strip().startswith('*')]
        return lines[0].replace('*', '').strip()
                      
    def CurrentCommitId(self):
        os.chdir(self.gitDir)
        result = getoutput('git log -1 HEAD')
        os.chdir(self.prevDir)
        cmts = result.split(os.linesep)
        return cmts[0][7:].strip()


    def CommitInfo(self, commitId):
        """ return: login, author, email, date, result """
        os.chdir(self.gitDir)
        result = getoutput('git log -1 %s' % commitId)
        os.chdir(self.prevDir)
        if result.find('fatal: ') != -1:
            return ()
        pattern = 'commit(.*?)Author:(.*?)Date:(.*?)'

        commid, author, email, dateStr, mergeCommit = '', '', '', '', False
        lines = result.split('\n')
        for line in lines:
            if lines.index(line) == 0:
                commitId = line.replace('commit ', '').strip()
            elif line.startswith('Merge:'):
                mergeStr = line.replace('Merge: ', '').strip()
                mergeCommit = True
            elif line.startswith('Author'):
                s = re.search('Author: (.*?)<', line)
                if s is not None: 
                    author = s.groups()[0].strip()
                else:
                    author = ''
                s = re.search('.*<(.*?)>', line)
                if s is not None:
                    email = s.groups()[0].strip()
                else:
                    email = ''
            elif line.startswith('Date'):
                dateStr = line.replace('Date: ', '').strip()
                date = parser.parse(dateStr) # keep original format and not converted to UTC
                i = lines.index(line)
        return (commitId, author, email, dateStr, result, mergeCommit)


    def CheckinFiles(self, commitId):
        """ return a list of changed files for a commit; each list member is [file, numAdd, numDel] """
        parent = commitId + '^'
        os.chdir(self.gitDir)
        ret = getoutput('git diff --numstat %s %s' % (parent, commitId))
        os.chdir(self.prevDir)
        retList = []
        if ret.find('fatal: ') != -1:
            return retList
        files = ret.split('\n')
        for eachFile in files:
            eachFileList = eachFile.split('\t')
            retList.append([eachFileList[2], eachFileList[0], eachFileList[1]])
        return retList


    def GetAllCommitIds(self):
        rets = []
        os.chdir(self.gitDir)
        result = getoutput('git log')
        os.chdir(self.prevDir)
        for line in result.split('\n'):
            if line.startswith('commit '):
                commitId = line.replace('commit ', '').strip()
                rets.append(commitId)
        return rets


    def GetCommitIds(self, numDayAgo):
        rets = []
        os.chdir(self.gitDir)
        result = getoutput('git log --since=\"%s days ago\"' % numDayAgo)
        os.chdir(self.prevDir)
        for line in result.split('\n'):
            if line.startswith('commit '):
                commitId = line.replace('commit ', '').strip()
                rets.append(commitId)
        return rets
                        
                        
    def GetAuthors(self, oldCommitId, newCommitId):
        """ return a list of (author, authorEmail) between 2 commits 
        ISSUE: git log old..new --format=xx Has problem when there is a Merge between old and new commits
        """
        if oldCommitId == newCommitId:
            (_, author, email, _, _, _) = self.CommitInfo(newCommitId)
            return [(author, email)]
        retSet = sets.Set()
        commits = self.GetAllCommitIds()
        try:
            fr = commits.index(newCommitId)
            to = commits.index(oldCommitId)
        except ValueError:
            return []        
        for c in commits[fr:to]:
            (_, author, email, _, _, _) = self.CommitInfo(c)
            retSet.add( (author, email) )        
        return list(retSet)
        
    
    def UpdateBranch(self, branch):
        """ return True (updated), oldCommit, newCommit, result 
        ISSUE: oldCommit is always be the first commit if 'git reset --soft HEAD~n' is accrossing Merge
        """
        print
        print '== update branch'
        os.chdir(self.gitDir)
        
        # when git checkout or git reset --hard different branches in the same git, these commands
        # might get failed due to index.lock
        ret = ''
        ret = self.__GitCmdWaitLock('git stash')
        print '\t==git stash'

        if self.CurrentBranch() != branch:
            ret = self.__GitCmdWaitLock('git checkout %s' % branch)
            print '\t==git checkout %s\n\t%s' % (branch, ret)
        
        ret = self.__GitCmdWaitLock('git reset --hard')   # remove local changes before git pull
        print '\t==git reset --hard\n\t%s' % ret
        
        oldCommit = self.CurrentCommitId()
        ret = self.__GitCmdWaitLock('cd %s;git pull' % self.gitDir) # without 'cd dir', the command 'git pull' does not work
        print '\t==cd %s;git pull\n\t%s' % (self.gitDir, ret)
        newCommit = self.CurrentCommitId()
        
        os.chdir(self.prevDir)
        if oldCommit != newCommit:
            ret = True
        else:
            ret = False
        return ret, oldCommit, newCommit
        

    def __GitCmdWaitLock(self, cmd):
        ret = ''
        while True:
            ret = getoutput(cmd)
            if ret.startswith('fatal: ') and ret.find('index.lock\': File exists'):
                time.sleep(1)
            else:
                break
        return ret
    
    
    def IsRemoteUpdated(self, branch):
        # check if remote branch is updated
        # but not update the local branch
        # git diff way is not always work
        #cmd = 'git diff origin/' + branch
        #r = getoutput(cmd)
        #if r == '':
        #    return False
        #else:
        #    return True
        os.chdir(self.gitDir)
        cmd = 'git status'
        status = getoutput(cmd)
        yourBranchInfo = [x for x in status.split('\n') if x.startswith('Your branch is ')]
        if not yourBranchInfo:
            print 'ERROR to find your branch info in git status command; output is %s' % status
            sys.exit(1)
        if yourBranchInfo[0].startswith('Your branch is up-to-date'):
            return False
        else:
            return True
        
        
class VxWorksGit(Git):
    def __init__(self, gitDir):
        super(VxWorksGit,self).__init__(gitDir)
            
    def NeedSetuptool(self):
        cmd = 'git status | grep "modified:" | grep "new commits"'
        os.chdir(self.gitDir)
        result = getoutput(cmd)
        if result.find('modified:') != -1 and result.find('(new commits)') != -1:
            return True
        else:
            return False
        
    def Setuptool(self):
        os.chdir(self.gitDir)
        cmds = ('./setup-tools -clean -site pek',
                './setup-tools -site pek',
               )
        for cmd in cmds:
            print '\t==%s' % cmd
            result = getoutput(cmd)
            print '\t%s\n' % result
        
    def UpdateBranch(self, branch):
        """ return True (updated), oldCommit, newCommit, result 
        ISSUE: oldCommit is always be the first commit if 'git reset --soft HEAD~n' is accrossing Merge
        """
        print
        print '== update branch'
        os.chdir(self.gitDir)
        
        if True or self.CurrentBranch() != branch:
            # when git checkout or git reset --hard different branches in the same git, these commands
            # might get failed due to index.lock
            print '\t==git checkout %s' % branch
            ret = self.__GitCmdWaitLock('git checkout %s' % branch)
            print '\t%s\n' % ret
        
            print '\t==git clean -fdxf'
            ret = self.__GitCmdWaitLock('git clean -fdxf') # remove all untracked files
            print '\t%s\n' % ret
    
        oldCommit = self.CurrentCommitId()
        print '\t==cd %s;git pull' % self.gitDir
        ret = self.__GitCmdWaitLock('cd %s;git pull' % self.gitDir) # without 'cd dir', the command 'git pull' does not work
        print '\t%s\n' % ret
        
        newCommit = self.CurrentCommitId()
        
        if True or self.CurrentBranch() != branch:
            self.Setuptool()
            
        os.chdir(self.prevDir)
        if oldCommit != newCommit:
            ret = True
        else:
            ret = False
        return ret, oldCommit, newCommit

    def __GitCmdWaitLock(self, cmd):
        ret = ''
        while True:
            ret = getoutput(cmd)
            if ret.startswith('fatal: ') and ret.find('index.lock\': File exists'):
                time.sleep(1)
            else:
                break
        return ret
