#!/usr/bin/env python

import sys
import time
import re
import difflib

import jenkins
from Jenkins import *
from KongConfig import *

newParameterSection = """
      <parameterDefinitions>
        <hudson.model.StringParameterDefinition>
          <name>BRANCH</name>
          <description>The Git branch you want to test on</description>
          <defaultValue>vx7-release</defaultValue>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>NEWCOMMIT</name>
          <description></description>
          <defaultValue>none</defaultValue>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>BSP</name>
          <description></description>
          <defaultValue>vxsim_linux</defaultValue>
        </hudson.model.StringParameterDefinition>
      </parameterDefinitions>
"""

def UpdateKongProjectSection():
    def __extractValue(keyExpression, content):
        found = re.search('(?s)' + keyExpression, content)
        if found is not None:
            return found.groups()[0]
        else:
            return ''
        
    jenkinsWeb = 'http://pek-testharness-s1.wrs.com:8080'
    #j = jenkins.Jenkins(jenkinsWeb, username='svc-qctool', password='ohm.ahda')
    j = jenkins.Jenkins(jenkinsWeb, username='svc-cmnet', password='december2012!')
    allProjects = [x['name'] for x in j.get_jobs()]

    for project in allProjects:
        if project.startswith('ut-vxsim-'):
        #if project == 'ut-vxsim-RTNET':
            print '== updating project %s' % project
            configXml = j.get_job_config(project)
            
            ptnStringSection = '(?s)<hudson.model.ParametersDefinitionProperty>(.*?)</hudson.model.ParametersDefinitionProperty>'
            found = __extractValue(ptnStringSection, configXml)
            #print found
            
            oldSection = '<hudson.model.ParametersDefinitionProperty>' + found + '</hudson.model.ParametersDefinitionProperty>'
            newSection = '<hudson.model.ParametersDefinitionProperty>' + newParameterSection + '</hudson.model.ParametersDefinitionProperty>'
            configXml = configXml.replace(oldSection, newSection)
            
            #print configXml
            j.reconfig_job(project, configXml)
            #break
    
    
def ModifyEmailUser(emailUser):
    jenkinsWeb = 'http://128.224.159.246:8080'
    j = jenkins.Jenkins(jenkinsWeb, username='svc-qctool', password='ohm.ahda')
    allProjects = [x['name'] for x in j.get_jobs()]

    for project in allProjects:
        if not project.startswith('vxworks-vx7-'):
            continue
        print
        configXml = j.get_job_config(project)
        ptn = '<recipients>(.*?)</recipients>'
        r = re.search(ptn, configXml)
        if r is not None:
            email = r.groups()[0]
            print 'project : %s' % project
            print '\told email: %s' % email
            print '\tnew email: %s' % emailUser
            configXml = configXml.replace(email, emailUser)
            j.reconfig_job(project, configXml)

def _ExtractCmd(configXml):
    found = re.search('(?s)<command>(.*?)</command>', configXml)
    if found is not None:
        return found.groups()[0]
    else:
        raise 'cannot find the shell commands in this config xml'
    
def _ExtractValue(cmd, keyExpression):
    found = re.search('(?s)' + keyExpression, cmd)
    if found is not None:
        return found.groups()[0]
    else:
        raise 'cannot find %s' % keyExpression

# API
def GetModTCBspFromLog(jenkinsWeb, job, build):
    try:
        content = GetBuildConsole(kongJenkins, job, build, kongUser, kongPassword)
        mod = ParseModule(content)
        tc  = _ExtractValue(content, '(?s)TESTCASE=(.*?)\n')
        bsp = ParseBsp(content)
        return mod, tc, bsp
    except:
        return '', '', ''


# API
def ParseModule(content):
    return _ExtractValue(content, '(?s)MODULE=(.*?)\n')


# API
def ParseBsp(content):
    # runtestsuite.py --uml="..." --vxworks=board=vxsim_linux,target=simlinux,version=7,wrenv=7,path=
    try:
        bsp = _ExtractValue(content, '(?s)vxworks=board=(.*?),')
    except:
        bsp = _ExtractValue(content, '(?s)BSP=(.*?)\n')
    return bsp


# API
def GetModTCBspFromConfig(jenkinsWeb, job):
    j = jenkins.Jenkins(jenkinsWeb, username='svc-cmnet', password='december2012!')
    configXml = j.get_job_config(job)
    cmd = _ExtractCmd(configXml)
    mod = _ExtractValue(cmd, '(?s)MODULE=(.*?)\n')
    tc = _ExtractValue(cmd, '(?s)TESTCASE=(.*?)\n')
    bsp = _ExtractValue(cmd, '(?s)BSP=(.*?)\n')
    return mod, tc, bsp


def GetKongModTC():
    jenkinsWeb = 'http://pek-testharness-s1.wrs.com:8080'
    #job = 'ut-vxsim-IKE-ALGORITHMS-1'
    j = jenkins.Jenkins(jenkinsWeb, username='svc-cmnet', password='december2012!')
    utJobs = sorted( [ x['name'] for x in j.get_jobs() if x['name'].startswith('ut-vxsim-')] )
    jobs = []
    for job in utJobs:
        if not ElemBeginWith(utJobs, job):
            jobs.append(job)
    
    rets = []        
    for job in jobs:
        mod, tc, bsp = GetModTCBspFromConfig(jenkinsWeb, job)
        rets.append( (mod, tc, bsp))
        print 'Job=', job
        print '\tMODULE=', mod
        print '\tTESTCASE=', tc
        print '\tBSP=', bsp
        print
    return rets


def ElemBeginWith(theList, theElem):
    for elem in theList:
        if (elem != theElem) and elem.startswith(theElem):
            return True
    return False

    
def UpdateKongProjectCommand():
    jenkinsWeb = 'http://pek-testharness-s1.wrs.com:8080'
    j = jenkins.Jenkins(jenkinsWeb, username='svc-cmnet', password='december2012!')
    allProjects = [x['name'] for x in j.get_jobs()]

    for project in allProjects:
        if project.startswith('ut-vxsim-'):
            configXml = j.get_job_config(project)
            cmd = _ExtractCmd(configXml)
            if (cmd.find('BSP=vxsim_linux') == -1):
                print '\n\n== updating %s ==' % project
                oldCmd = '<command>' + cmd + '</command>'
                newCmd = oldCmd.replace('/net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/try/workspace/PdvTool/vx7tool/new/RunTest.sh', 
                                        'BSP=vxsim_linux\n/net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/try/workspace/PdvTool/vx7tool/new/RunTest.sh')
                newConfigXml = configXml.replace(oldCmd, newCmd)

                #print newConfigXml
                #print
                j.reconfig_job(project, newConfigXml)
                #break
                           
                
def UpdateKongProjectCommand1():
    #with open('JobCmd.txt', 'r') as fd:
    #    newCmdSample = fd.read()
        
    jenkinsWeb = 'http://pek-testharness-s1.wrs.com:8080'
    j = jenkins.Jenkins(jenkinsWeb, username='svc-cmnet', password='december2012!')
    allProjects = [x['name'] for x in j.get_jobs()]

    for project in allProjects:
        if project.startswith('ut-vxsim-'):
            print project
            sys.exit(0)
            configXml = j.get_job_config(project)
            cmd = _ExtractCmd(configXml)
            if (cmd.find('TESTCASE=ALL') != -1) or (cmd.find('TESTCASE=ALL') == -1):
                print '\n\n== %s ==' % project
                #print '%s\n' % configXml
                #print '='*20
                
                oldCmd = '<command>' + cmd + '</command>'
                #print configXml.find(oldCmd)
                #print '='*20

                oldTestCase = _ExtractValue(cmd, 'TESTCASE=(.*?)\n')
                print 'old test case:%s' % oldTestCase
                #newConfigXml = newConfigXml.replace('TESTCASE=ALL', 'TESTCASE=%s' % oldTestCase)
                
                oldMod = _ExtractValue(cmd, 'MODULE=(.*?)\n')
                print 'old module:%s' % oldMod
                #newConfigXml = newConfigXml.replace('MODULE=FTP', 'MODULE=%s' % oldMod)

                newCmd = '<command>' + """date
hostname
id
echo $BRANCH
echo $NEWCOMMIT
""" + ('MODULE=%s' % oldMod) + '\n' + ('TESTCASE=%s' % oldTestCase) + '\n' + '/net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/try/workspace/PdvTool/vx7tool/new/RunTest.sh $BRANCH $NEWCOMMIT $MODULE $TESTCASE' + '\n'+ '</command>'
                newConfigXml = configXml.replace(oldCmd, newCmd)

                print '='*10
                print newConfigXml
                print
                #break
                j.reconfig_job(project, newConfigXml)


def BackupJenkinsProject(jenkinsWeb='http://pek-testharness-s1.wrs.com:8080'):
    j = jenkins.Jenkins(jenkinsWeb, username='svc-cmnet', password='december2012!')
    allProjects = [x['name'] for x in j.get_jobs()]

    for project in allProjects:
        configXml = j.get_job_config(project)
        configFile = project + '.xml'
        #if project != 'vxworks-vx7-vxsim-CRYPTO':
        #    continue
        print 'backup ', configFile
        with open(configFile, 'w') as fd:
            fd.write(configXml)
                

def EnableJenkinsProject(jenkinsWeb=kongJenkins, turnOnFlag=True):
    j = jenkins.Jenkins(jenkinsWeb, username='svc-cmnet', password='december2012!')
    allProjects = [x['name'] for x in j.get_jobs() if x['name'].startswith('ut-vxsim-')]
    allProjects += ['ci-summary', 
                    'ci-wassp-report', 
                    'ci-rerun-after-ltaf-report',
                    'ft-virtio-network-driver',
                   ]
    
    filterOutProjects = ['abc']
    for project in allProjects:
        if turnOnFlag:
            if project not in filterOutProjects:
                print 'enabling %s' % project
                j.enable_job(project)
        else:
            if project not in filterOutProjects:
                print 'disabling %s' % project
                j.disable_job(project)
            
            
def StopAllProjectRunning(jenkinsWeb='http://128.224.159.246:8080'):
    """ not worked for both stop_build() and send POST approaches """
    j = jenkins.Jenkins(jenkinsWeb)
    allProjects = [x['name'] for x in j.get_jobs()]

    for i in range(0, 100):
        for project in allProjects:
            status, build = GetLatestJobStatus(jenkinsWeb, project)
            if status == 'INPROGRESS':
                print 'stopping job %s #%s' % (project, build)
                #print StopBuild(project, build, jenkinsWeb)
                j.stop_build(project, build)
        time.sleep(20)


def UpdateKongProject0():
    branchStrParameter = """</org.jvnet.jenkins.plugins.nodelabelparameter.NodeParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>BRANCH</name>
          <description></description>
          <defaultValue>vx7-release</defaultValue>
        </hudson.model.StringParameterDefinition>"""

    ptnBuildTriggerToRemove = '(?s)<hudson.tasks.BuildTrigger>(.*?)</hudson.tasks.BuildTrigger>'
      
    buildTrigger = """</hudson.tasks.BuildTrigger>
    <hudson.plugins.parameterizedtrigger.BuildTrigger plugin="parameterized-trigger@2.25">
      <configs>
        <hudson.plugins.parameterizedtrigger.BuildTriggerConfig>
          <configs>
            <hudson.plugins.parameterizedtrigger.PredefinedBuildParameters>
              <properties>BRANCH=$BRANCH</properties>
            </hudson.plugins.parameterizedtrigger.PredefinedBuildParameters>
          </configs>
          <projects>vxworks-vx7-vxsim-DHCP</projects>
          <condition>ALWAYS</condition>
          <triggerWithNoParameters>false</triggerWithNoParameters>
        </hudson.plugins.parameterizedtrigger.BuildTriggerConfig>
      </configs>
    </hudson.plugins.parameterizedtrigger.BuildTrigger>"""
    
    buildNaming = """<buildWrappers>
    <org.jenkinsci.plugins.buildnamesetter.BuildNameSetter plugin="build-name-setter@1.3">
      <template>#${BUILD_NUMBER}-${ENV,var=&quot;BRANCH&quot;}</template>
    </org.jenkinsci.plugins.buildnamesetter.BuildNameSetter>
  </buildWrappers>"""
    
    jenkinsWeb = 'http://128.224.159.246:8080'
    j = jenkins.Jenkins(jenkinsWeb, username='svc-qctool', password='ohm.ahda')
    allProjects = [x['name'] for x in j.get_jobs()]

    for project in allProjects:
        fc = ''
        if project.startswith('vxworks-vx7-vxsim-'):
            if project == 'vxworks-vx7-vxsim-VRRP':
                break
            with open('./kong/'+project+'.xml', 'r') as fd:
                fc = fd.read()
                ptn = '<childProjects>(.*?)</childProjects>'
                r = re.search(ptn, fc)
                if r is not None:
                    downstreamProject = r.groups()[0]
                else:
                    print 'error to find downstream project'
                    exit(1)
                newProjectTag = '<projects>' + downstreamProject +'</projects>'
                print 'project:', project
                print '\tnew project tag:', newProjectTag
                currentBuildTrigger = buildTrigger.replace('<projects>vxworks-vx7-vxsim-DHCP</projects>', newProjectTag)
                
                r1 = re.search(ptnBuildTriggerToRemove, fc)
                if r1 is not None:
                    r1content = r1.groups()[0]
                else:
                    print 'error to find build trigger to remove'
                    exit(2)
                buildTriggerToRemove = '<hudson.tasks.BuildTrigger>' + r1content + '</hudson.tasks.BuildTrigger>'
                
                fc = fc.replace('<name/>', '<name></name>')
                fc = fc.replace('<description/>', '<description></description>')
                fc = fc.replace('</org.jvnet.jenkins.plugins.nodelabelparameter.NodeParameterDefinition>', branchStrParameter)
                fc = fc.replace('</hudson.tasks.BuildTrigger>', currentBuildTrigger)
                fc = fc.replace('<buildWrappers/>', buildNaming)
                fc = fc.replace(buildTriggerToRemove, '')
                j.reconfig_job(project, fc)
            #with open(project+'-new.xml', 'w') as fd:
            #    fd.write(fc)


def CreateJenkinsProject(jenkinsWeb='http://128.224.159.246:8080'):
    j = jenkins.Jenkins(jenkinsWeb, username='svc-cmnet', password='december2012!')
    allProjects = [x['name'] for x in j.get_jobs()]

    oldJobs = []
    for oldProject in allProjects:
        if oldProject.startswith('vxworks-vx7-vxsim-'):
            module = oldProject.replace('vxworks-vx7-vxsim-', '')
            module = module.replace('.xml', '')
            print oldProject, module
            configXml = j.get_job_config(oldProject)
            r = re.search('(?s).*--speed -c (.*?)</command>', configXml)
            if r is not None:
                mod = r.groups()[0]
                print mod
                oldJobs.append(mod)
    
    print oldJobs
    print len(oldJobs)
    
    newXmlSample = 'ut-vxsim-FTP.xml'
    newJobPrefix = 'ut-vxsim-'
    existedJobs = ['FTP', 'TFTP']
    strangeJobs = ['ut-vxsim-IKE-ALGORITHMS ', 
                   'ut-vxsim-IKE-RACOON ',
                   'ut-vxsim-IKE-ROHC-IPSEC ',
                  ]

    for job in oldJobs:
        with open(newXmlSample, 'r') as fd:
            fc = fd.read()
        if job not in existedJobs:
            newJob = newJobPrefix + job
            if (newJob not in allProjects) and (newJob not in strangeJobs):
                newModule = '\nMODULE=%s\n' % job
                fc = fc.replace('\nMODULE=FTP\n', newModule)
                print '='*10
                print 'creating %s...' % newJob
                #print fc
                r = re.search('(?s)\nMODULE=(.*?)\n', fc)
                if r is not None:
                    print r.groups()[0]
                else:
                    print '---'
                j.create_job(newJob, fc)
                time.sleep(10)


def CheckUTJobsConfig():
    jenkinsWeb='http://pek-testharness-s1.wrs.com:8080'
    j = jenkins.Jenkins(jenkinsWeb, username='svc-cmnet', password='december2012!')
    allJobs = [x['name'] for x in j.get_jobs()]
    print j.get_job_config('ci-manager')
    sys.exit(0)

    utJobs = [x for x in allJobs if x.startswith('ut-vxsim-')]
    
    for job in utJobs:
        configXml = j.get_job_config(job)
        print '\n', job
        print configXml
        """
        r = re.search('(?s)\nMODULE=(.*?)\n', configXml)
        if r is not None:
            print job, r.groups()[0]
        else:
            print '---'
        """
        break
        
def main():
    #print IsAnyProjectRunning('http://128.224.159.246:8080', 'svc-cmnet', 'december2012!')
    #BackupJenkinsProject()
    #UpdateKongProjectSection()
    #UpdateKongProjectCommand()
    EnableJenkinsProject(turnOnFlag=False)
    #StopAllProjectRunning()
    
    #CreateJenkinsProject()
    #CheckUTJobsConfig()
    
if __name__ == '__main__':
    main()
    