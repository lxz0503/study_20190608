#!/usr/bin/env python

from Git import Git
from Utility import String2Datetime

class config:
    gitDir = '/buildarea2/lchen3/workspace/vx7-dev-nightly/vx-git-net'
    gitBranch = 'vx7-release'
    # 3 teams : Lun Zhang, Huabing Chu, Kitty Kong
    authors = ['blan', 'ffeng', 'hma', 'jxu', 'myang', 'rwu1', 'txu', 'whu', 'xliu3', 'ywang7', 'yma1', 'yli1',  'zyang0', \
               'csun', 'hxu0', 'jren', 'jwang9', 'jli7', 'lyang3', 'lwang7', 'xjiang1', 'yli10', 'zan', \
               'wpaul', 'sekhar', 'cwong0', 'dlkrejsa', 'hkoike', 'jbrotsos', 'rrama', 
              ]
    startDate = '2014-04-20 00:00:00'
    endDate = '2015-04-20 00:00:00'


def GetCodeChange(git, commits, authors, startDate, endDate):
    authorCodePairs = {}
    for x in authors:
        authorCodePairs[x] = 0
    print authorCodePairs
    sd = String2Datetime(startDate)
    ed = String2Datetime(endDate)

    for c in commits:
        num = 0
        (commitId, a, email, dateStr, _, mergeCommit) = git.CommitInfo(c)
        dstr = ' '.join(dateStr.split(' ')[0:-1])
        d = String2Datetime(dstr, '%a %b %d %H:%M:%S %Y')
        if (a in authorCodePairs) and (d > sd) and (d < ed) and (not mergeCommit):
            fileChanges = git.CheckinFiles(commitId)
            num = sum( int(x[1])+int(x[2]) for x in fileChanges if (x[1] != '-') and (x[2] != '-') )
            authorCodePairs[a] = authorCodePairs[a] + num
            print '%s, %s, %s, %s, %s' % (a, commitId, dateStr, fileChanges, num)
            print
    
    for k in authors:
        print '==%s:%s' % (k, authorCodePairs[k])


def main():
    git = Git(config.gitDir)
    git.GotoBranch(config.gitBranch)
    commits = git.GetAllCommitIds()
    
    GetCodeChange(git, commits, config.authors, config.startDate, config.endDate)
    
    
if __name__ == '__main__':
    main()
