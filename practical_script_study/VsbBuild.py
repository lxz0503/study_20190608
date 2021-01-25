#!/usr/bin/env python

"""
vx7 build environment must be set up before using the script
    the script will use the env var WIND_BASE
"""

import os, sys, re
import argparse
from logging import *
from commands import getoutput

from Action import ExecCmd
from VxAction import VxAction
from Config import *
from Git import *
from Coverity import *
from BuildWarning import *
from XUnitTestResult import SearchInfo
from Mail import *
from Cleanup import *

class Report:
    reports = []
    
class BspBuildCmd(object):
    def __init__(self, server, buildDir, branch, bsp, tool, cpu):
        self.__CheckGitEnv()
        self.branch = branch
                    
        serverCfg = Vx7Config(server)
        self.currentGitPath, _, self.preventRunDir, self.preventTmpDir = serverCfg.GetDirs()

        currentGit = Git(self.currentGitPath)
        currentGit.GotoBranch(branch)
        _, oldCmt, newCmt = currentGit.UpdateBranch(branch)
        print '== update branch %s at %s' % (branch, os.uname()[1])
        print '== server:%s, old commit:%s, new commit:%s' % (server, oldCmt, newCmt)
        
        print '== BUILDCMD server:%s, dir:%s' % (getoutput('hostname'), getoutput('pwd'))
        print '== BUILDCMD git branch:\n%s' % getoutput('git branch')
        print '== BUILDCMD latest commit:\n%s' % getoutput('git log -1 HEAD')        
        del currentGit

        self.buildDir = buildDir
        self.bsp = bsp # bsp name without version
        self.tool = tool
        self.cpu = cpu
                
        self.__layers = []
        self.__comps = []
        self.__make = 'make -j 24'
        self.__cmds = []
        self.parallelBuild = True
        self.preventBuild = False
        self.hasComponents = False

              
    def AddFeatureByKeyword(self, keywords):
        if len(keywords) != 0:
            if len(keywords) == 1:
                cmd = 'vxprj vsb listAll | grep -E \"%s\"' % keywords[0]
            else:
                cmd = 'vxprj vsb listAll '
                for eachKeyword in keywords:
                    cmd = cmd + ' | grep -E \"%s\"' % eachKeyword
            #print '==cmd:%s' % cmd            
            result = getoutput(cmd)
            self.__layers = self.__layers + map(lambda x: 'vxprj vsb add %s' % x.strip(), result.split('\n'))


    def AddLayers(self, layers):
        if len(layers) != 0:
            self.__layers = self.__layers + map(lambda x: 'vxprj vsb add %s' % x, layers)
                    
    def AddComps(self, components):
        if len(components) != 0:
            self.hasComponents = True
            self.__comps = components

    def SetParallelBuild(self, flag):
        assert type(flag) == bool
        self.parallelBuild = flag


    def SetPreventBuild(self, flag):
        assert type(flag) == bool
        self.preventBuild = flag
        

    def SetCPU(self, cpu):
        self.cpu = cpu

    def SetSMP(self, smp):
        assert type(smp) == bool
        self.smp = smp
                        
    def CreateCmd(self):
        path = self.buildDir + '/' + self.branch
        if not os.path.exists(path):
            getoutput('mkdir %s' % path)
            
        bspName = self.__GetBspName()
        if bspName == '':
            print 'cannot find bsp full name by bsp %s' % self.bsp
            sys.exit(4)

        sep = '@'
        if self.cpu != '':
            bspDir = path + '/' + self.branch + sep + self.bsp + sep + self.tool + sep + self.cpu
        else:
            bspDir = path + '/' + self.branch + sep + self.bsp + sep + self.tool 

        self.__cmds.append('rm -fr %s' % bspDir)
        self.__cmds.append('cd %s' % path)
        
        # some changes might need to postinstall
        postInstallCmd = self.currentGitPath + '/setup/postinstall.sh'
        wrenvFullPath = self.currentGitPath + '/wrenv.linux'
        wrenvCmd = 'eval `%s -p vxworks-7 -o print_env -f sh`' % wrenvFullPath
        createBspCmd = 'vxprj vsb create -bsp %s %s -S' % (bspName, bspDir)
        cdCmd = 'cd %s' % self.currentGitPath
        #wholeCmd = postInstallCmd + '; ' + wrenvCmd + '; ' + createBspCmd
        wholeCmd = createBspCmd
        self.__cmds.append(wholeCmd)

        cdToBspDir = 'cd %s' % bspDir
        if self.__layers != []:
            self.__cmds = self.__cmds + map(lambda x: cdToBspDir + '; ' + x, self.__layers)
            # walkaround: DEBUG_AGENT with USB makes build failed
            self.__cmds.append(cdToBspDir + '; ' + 'vxprj vsb remove DEBUG_AGENT')
            # walkaround: remove VXTEST
            if self.branch.startswith('fr55-vx7-quark-dev') or self.branch == 'vx7-usb':
                # for i in `vxprj vsb listAll| grep USB | grep FUNCTION`;do vxprj vsb add $i;done
                cmdToRemoveVxTest = """for i in `vxprj vsb listAll| grep ^VXTEST | grep USB`;do vxprj vsb remove $i;done"""
                self.__cmds.append(cdToBspDir + '; ' + cmdToRemoveVxTest)

        if self.branch == 'vx7-dev-f1976':
            for cmd in ['vxprj vsb config -s -add _WRS_CONFIG_VXTEST_BUILD=y',
                        'vxprj vsb config -s -remove _WRS_CONFIG_BENCHMARKS',
                        'vxprj vsb config -s -remove _WRS_CONFIG_KSHELLTEST',
                        'vxprj vsb config -s -remove _WRS_CONFIG_VXTEST',
                        'vxprj vsb config -s -remove _WRS_CONFIG_VXTEST_UTIL',
                        'vxprj vsb config -s -remove _WRS_CONFIG_VXTESTV2',
                        ]:
                self.__cmds.append(cdToBspDir + '; ' + cmd)
        """ not working 
        if self.branch == 'jliu1-vadk-f2848':
            vipName = os.path.basename(bspDir) + '_vip'
            vipDir = cdToBspDir + '/../' + vipName
            vipCreate = 'vxprj create -vsb %s -inet6 -c INCLUDE_IPFTPS -c INCLUDE_IPTFTPS -c INCLUDE_IPCOM -c INCLUDE_IPDHCPC -c INCLUDE_IPDHCPC6 -c INCLUDE_IPD_CMD -c INCLUDE_IFCONFIG -c INCLUDE_IPCOM_SYSVAR_CMD -c INCLUDE_IPCOM_CPU_CMD -c INCLUDE_IPFTP_CMD -c INCLUDE_IPDNSC' % vipName
            self.__cmds.append(cdToBspDir + '/..'+ ' ; ' + vipCreate)
            vipBuild = 'vxprj build'
            self.__cmds.append(vipDir + '; ' + vipBuild)
        """
        if self.parallelBuild:
            self.__make = cdToBspDir + '; ' + 'make -j 24'
        else:
            self.__make = cdToBspDir + '; ' + 'make'     
        # make -j24 or
        # make -j24 CPU=ARMARCH7 TOOL=diab [VXBUILD=SMP]       
        if self.cpu != '':
            self.__make = self.__make + ' CPU=%s TOOL=%s' % (self.cpu, self.tool)
        elif self.tool != '':
            self.__make = self.__make + ' TOOL=%s' % self.tool
        else:
            self.__make = self.__make

        if self.smp:
            self.__make = self.__make + ' VXBUILD=SMP'
            
        if self.preventBuild:
            prevEnv = """export CHECKER_OVERRIDE="--checker-option CHECKED_RETURN:stat_threshold:0" """
            cmds = self.__make.split(';')
            self.__cmds.append(cmds[0] + '; ' + cmds[1])
            windBase = self.currentGitPath + '/vxworks-7'
            for comp in self.__comps:
                currentDir = windBase + comp
                appendNullLineCmd = 'cd %s; git ls-files' % currentDir + """ | grep -E "\.c$|\.cpp$" | xargs -t -i bash -c 'echo "" >> $1' -- {} \;"""
                self.__cmds.append(appendNullLineCmd)
            self.__cmds.append(cmds[0] + '; ' + ' prevent.pl ' + cmds[1])
        else:
            self.__cmds.append(self.__make)
        
        # restore all the files appended a null line
        os.chdir(windBase + comp)
        for comp in self.__comps:
            currentDir = windBase + comp
            #restoreCmd = 'find ' + (windBase + comp) + """ -type f | grep -E "\.c$|\.cpp$" | xargs -t -i git checkout {}"""
            restoreCmd = 'cd %s; git ls-files' % currentDir + """ | grep -E "\.c$|\.cpp$" | xargs -t -i git checkout {}"""
            self.__cmds.append(restoreCmd)
            
        #lastCmd = 'cat /buildarea1/target/nightly/CoverityRuns/prevent-11Aug-23:32:53/debug-prevent-index.txt'
        #self.__cmds = [lastCmd]
        
        if self.hasComponents:
            self.__cmds.append('COMPONENTS:' + ' '.join(self.__comps))
            
        return self.__cmds

                    
    def __CheckGitEnv(self):
        if os.getenv("WIND_BASE") is None:
            error('environment WIND_BASE not found')
            exit(1)

    
    def __GetBspName(self):
        if self.cpu != '':
            return self.bsp
            
        result = getoutput('cd $WIND_BASE; vxprj vsb listBsps -all')
        print '==result:%s' % result
        r1 = getoutput('cd $WIND_BASE; pwd')
        print '==pwd:%s' % r1
        r = re.search('(?s)Valid BSPs:(.*)', result)
        if r is not None:
            bspList = r.groups()[0]
            validBsps = set(bspList.split())
        else:
            print 'failed to run vxprj vsb listBsps -all'
            sys.exit(2)
        for eachBsp in validBsps:
            if eachBsp.find(self.bsp) != -1:
                return eachBsp
        return ''        

# end of BspBuildCmd


class VsbBuild(VxAction):
    def __init__(self, branch, server, cmds, oldCommit, newCommit):
        debug('entering class VsbBuild::__init__')
        super(VsbBuild, self).__init__()
        assert type(cmds) == list

        print '== master git old commit:%s, new commit:%s' % (oldCommit, newCommit)
        
        print '== VSBBUILD server:%s, dir:%s' % (getoutput('hostname'), getoutput('pwd'))
        print '== VSBBUILD git branch:\n%s' % getoutput('git branch')
        print '== VSBBUILD latest commit:\n%s' % getoutput('git log -1 HEAD')        

        self.branch = branch
        self.server = server 

        if cmds[-1].startswith('COMPONENTS:'):
            self.cmds = cmds[:-1]
            self.components = cmds[-1].replace('COMPONENTS:', '').split(' ')
        else:   
            self.cmds = cmds
            self.components = []
        print '== components:%s' % self.components
        self.preventHTML = ''
                
        self.oldCommit = oldCommit
        self.newCommit = newCommit
        self.hasPreventCmd = self.__HasPreventCmd()
        
                
    def BeforeRun(self):
        debug('entering class VsbBuild::BeforeRun')
        super(VsbBuild, self).BeforeRun()
        print '\n== build commands:'
        Report.reports.append('== build commands at %s:' % getoutput('hostname'))
        
        for cmd in self.cmds:
            self.AddCmd(cmd)
            Report.reports.append(cmd)
            print cmd
        print
        #DEBUG sys.exit(0)            

        print 'PREVENT_RUN_DIR: %s TMPDIR: %s\n' % (os.environ['PREVENT_RUN_DIR'], os.environ['TMPDIR'])
        print 'CHECKER_OVERRIDE: %s' % os.environ['CHECKER_OVERRIDE']
        if os.environ['PREVENT_RUN_DIR'] == '' or os.environ['TMPDIR'] == '':
            sys.exit(1)
            
    # override HandleOutput

    def HandleOutput(self, cmd, retCode, retContent):
        debug('entering class VsbBuild::HandleOutput')
        super(VsbBuild, self).HandleOutput(cmd, retCode, retContent)
        if self.hasPreventCmd:
            if cmd.find('prevent.pl ') != -1:
                errorInfo = SearchInfo(retContent, 'Open this file in a browser to see your defects:', after=1)
                if errorInfo != '':
                    preventHTML = (errorInfo.split('\n'))[1].strip()
                else:
                    preventHTML = ''
                if preventHTML == '':
                    print 'not find prevent-index.html'
                    exit(1)
                self.preventHTML = preventHTML
        if retCode != 0 and ( (cmd.find('vxprj vsb create -bsp') != -1) or (cmd.find('vxprj vsb add') != -1) ):
            self.__OutputEnv()
            

    def __OutputEnv(self):
        print '== current server:%s' % getoutput('hostname')
        print '== current path:%s' % os.getcwd()
        print '== git branch:\n%s' % getoutput('git branch')
        print '== current commit id:\n%s' % getoutput('git log -1 HEAD')
        print '== vxprj vsb listBsps -all'
        print getoutput('vxprj vsb listBsps -all')
        print '== vxprj vsb listAll'
        print getoutput('vxprj vsb listAll')                
        
    # override AfterRun    
    def AfterRun(self):
        debug('entering class VsbBuild::AfterRun')
        print '=== AfterRun()'
        print '=== retCode: %s, hasPreventCmd:%s' % (self.retCode, self.hasPreventCmd)
        if self.retCode == 0:
            if self.hasPreventCmd:
                print 'preventHTML=',self.preventHTML
                warningFile = FindWarningFile(self.preventHTML)
                buildLogFile = FindBuildLogFile(self.preventHTML)

                gitReports = ReportGitChange(self.oldCommit, self.newCommit)

                warnNum, warnReports = ReportWarning(warningFile)
                covNum, covReports = ReportCoverity(self.preventHTML)
                compReportList = []
                if self.components != []:
                    indexHtml = os.path.dirname(self.preventHTML) + '/c/output/errors1/index.html'
                    for comp in self.components:
                        compName = comp.replace('/', '-')
                        newIndexHtml = os.path.dirname(self.preventHTML) + '/c/output/errors1/index_4' + compName + '.html'
                        _, aCompReportList = ReportComponentCoverity(indexHtml, newIndexHtml, comp)
                        compReportList = compReportList + [' '] + aCompReportList                        

                if IsBuildPassed(warningFile):                        
                    buildLogInfo = 'WARNING-REPORT: refer to %s for detail' % CreateHtmlPath(buildLogFile)
                    warnReports.insert(1, buildLogInfo)
                    Report.reports = gitReports + [' '] + Report.reports + [' '] + warnReports + [' '] + covReports + [' '] + compReportList
                else:
                    warningInfo = 'Build ERROR: refer to %s for detail' % CreateHtmlPath(warningFile)
                    print warningInfo
                    Report.reports = gitReports + [' '] + Report.reports + [' '] + [warningInfo]
                    
                fromEmail, toEmail = CreateEmailList(self.branch, self.oldCommit, self.newCommit)  
                NotifyPeople(fromEmail, toEmail, self.branch, self.oldCommit, self.newCommit, warnNum, covNum, Report.reports) 


    def __HasPreventCmd(self):
        for cmd in self.cmds:
            if cmd.find('prevent.pl ') != -1:
                return True
        return False

# end of VsbBuild

def CreateEmailList(branch, oldCommit, newCommit):
    masterGit = Git(masterGitPath)
    masterGit.GotoBranch(branch)
    authorEmails = masterGit.GetAuthors(oldCommit, newCommit)
    
    mgrEmails, toEmails = sets.Set(), sets.Set()
    for author, email in authorEmails:
        if not email.endswith('@windriver.com'):
            authorCorpEmail = GetCorpEmail(author)
            if email != '':
                toEmails.add(authorCorpEmail)
            else:
                toEmails.add(email)
        else:
            toEmails.add(email)
        mgrEmail = GetMgrEmail(author)
        if mgrEmail != '':
            mgrEmails.add(mgrEmail)
            
    fromEmail = 'libo.chen@windriver.com'
    adminEmail = 'libo.chen@windriver.com'
    if (list(toEmails) + list(mgrEmails)):
        #toEmail = ';'.join(list(toEmails) + list(mgrEmails)) + ';' + adminEmail
        toEmail = ';'.join(list(toEmails)) + ';' + adminEmail
    else:
        toEmail = adminEmail
    return fromEmail, toEmail
    
                
def NotifyPeople(fromEmail, toEmail, branch, oldCommit, newCommit, warnNum, covNum, reports):
    # subject: build warnings & coverity issues for branch {branch} from commit {oldCommit} to {newCommit}
    #SendEmail(sender, to, subject, body, mailServer='prod-webmail.corp.ad.wrs.com')        
    
    subject = 'Vx7 branch ' + branch + ': ' + str(warnNum) + ' compiler warnings & ' \
              + str(covNum) + ' coverity issues ' \
              + ' from commit ' + oldCommit + ' to ' + newCommit
    content = '\n'.join(reports)

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


def ReportGitChange(oldCommit, newCommit):
    reports = []
    os.chdir(masterGitPath)
    old = getoutput('git log -1 %s' % oldCommit)
    new = getoutput('git log -1 %s' % newCommit)
    reports.append('From old commit:')
    reports.append( '\n'.join( map(lambda x: '\t' + x, old.split('\n')) ) )
    reports.append('\nTo new commit:')
    reports.append( '\n'.join( map(lambda x: '\t' + x, new.split('\n')) ) )
    return reports
    

def CreateBuildCmd(server, buildDir, branch, bsp, tool, cpu, keywords, parallelBuild, preventBuild, smp, layers, components):
    bspBuild = BspBuildCmd(server, buildDir, branch, bsp, tool, cpu)
    bspBuild.AddFeatureByKeyword(keywords)
    bspBuild.AddLayers(layers)
    bspBuild.AddComps(components)
    bspBuild.SetParallelBuild(parallelBuild)
    bspBuild.SetPreventBuild(preventBuild)
    bspBuild.SetCPU(cpu)
    bspBuild.SetSMP(smp)
    bspCmds = bspBuild.CreateCmd()
    return bspCmds
        
          
def BuildVsbMain():
    basicConfig(level=ERROR)
    parser = argparse.ArgumentParser(description='Build VSB via BSP')
    parser.add_argument('--branch', action='store', dest='branch', help='specify the git branch to build (required)')
    parser.add_argument('--server', action='store', dest='server', help='specify the server to build (required)')
    parser.add_argument('--oldcommit', action='store', dest='oldCommit', help='specify the old commit (required)')
    parser.add_argument('--newcommit', action='store', dest='newCommit', help='specify the new commit (required)')    
    results = parser.parse_args()
    
    if (results.branch is None) or (results.server is None) or (results.oldCommit is None) or (results.newCommit is None):
        parser.print_help()
        exit(1)

    server = results.server
    serverCfg = Vx7Config(server)
    serverCfg.SetupEnv()
    gitDir, buildDir, preventRunDir, preventTmpDir = serverCfg.GetDirs()
    Cleanup(server)
    
    rets = []
    config = ConfigParser(results.branch)
    for bsp in config.GetBsps():
        Report.reports = []
        print '== build bsp %s for branch %s' % (bsp, results.branch)
        buildParameters = config.GetBuildParameters(bsp)
        for p in buildParameters:
            print p
            cmds = CreateBuildCmd(server, buildDir, results.branch, bsp, p['tool'], p['cpu'], p['keywords'], p['parallelBuild'], \
                                  p['preventBuild'], p['smp'], p['layers'], p['components'])
            #for c in cmds: print c
            #sys.exit(0)
            vsbBuild = VsbBuild(results.branch, server, cmds, results.oldCommit, results.newCommit)
            rets.append(vsbBuild.Run())

    for ret in rets:
        if ret != 0:
            sys.exit(ret)
    sys.exit(0)   # mark Jenkins job status

if __name__ == '__main__': BuildVsbMain()
