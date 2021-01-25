import os
import re
import sys
from operator import itemgetter

from Jenkins import GetBuildConsole, GetJobBuildsFromMultiJob, GetLatestJobStatus
from KongConfig import kongJenkins, kongUser, kongPassword
from Mail import SendEmail

def saveFile():
    job = 'ci-build-slave'
    build = 100049
    console = GetBuildConsole(kongJenkins, job, build, user=kongUser, password=kongPassword)
    print(console)
    with open('%s_%s' % (job, build), 'w') as fd:
        fd.write(console.encode('ascii', 'ignore'))

def extractWarnings(fileName):
    warningPtn = '(?s)\n(\w+\.\w+:\d+:\d+: warning: .*?\^)'
    with open(fileName, 'rt') as fd:
        content = fd.read()
        founds = findAllItems(warningPtn, content, multiline=False)
    return founds        
        
def findAllItems(rePattern, content, raiseException=False, multiline=True):
    if multiline:
        found = re.findall(rePattern, content, re.MULTILINE)
    else:
        found = re.findall(rePattern, content)
    if found is not None:
        return found
    else:
        if raiseException:
            raise BaseException('not found %s' % rePattern)
        else:
            return []

    
def test_extractWarnings():
    fileName = 'ci-build-slave_100049'
    warnings = extractWarnings(fileName)
    i = 0
    for w in warnings:
        print(len(w))
        print('-'*22)
        #if i >= 3:
        #    break
        i += 1

def main1():
    multiJob = 'ci-manager'
    multiJobBuild = 2850
    jobBuilds = GetJobBuildsFromMultiJob(kongJenkins, multiJob, multiJobBuild, kongUser, kongPassword)
    print(jobBuilds)

class WarningParser():
    def __init__(self):
        pass
    
    def extractWarnings(self, content):
        warningPtn = '(?s)\n(\w+\.\w+:\d+:\d+: warning: .*?\^)'
        founds = findAllItems(warningPtn, content, multiline=False)
        return founds
    
    def getFileName(self, warning):
        # format : iptftpc.c:489:23: warning: ...^
        return warning.split(':')[0]

class KongTestJenkins():
    def __init__(self, kongJenkins, kongUser, kongPassword):
        self.kongJenkins = kongJenkins
        self.kongUser = kongUser
        self.kongPassword = kongPassword
    
    def getLatestBuild(self):
        job = 'ci-manager'
        status, build = GetLatestJobStatus(self.kongJenkins, job, user=self.kongUser, password=self.kongPassword)
        if status == 'INPROGRESS':
            raise Exception('%s is in progress and this tool should not be running' % job)
        return build
    
    def getBuildSlaves(self, build):
        # return [ (module, job, build), ... ]
        multiPhaseJob = 'ci-manager'
        buildManagerJob = 'ci-build-manager'
        jobBuilds = GetJobBuildsFromMultiJob(self.kongJenkins, multiPhaseJob, build, self.kongUser, self.kongPassword)
        buildManagerJobBuilds = [x for x in jobBuilds if x[0] == buildManagerJob]
        if not buildManagerJobBuilds:
            raise Exception('%s with build id not found' % buildManagerJob)
        moduleJobBuilds = self.__extractBuildSlaves(buildManagerJobBuilds[0][0], buildManagerJobBuilds[0][1])
        return moduleJobBuilds
    
    def __extractBuildSlaves(self, buildManagerJob, build):
        content = self.getConsole(buildManagerJob, build)
        buildSlavePtn = '(?s)\njava -jar .*? -p MODULE=(.*?) -p BSP=(.*?) .*?Started ci-build-slave #(.*?)\n'
        founds = findAllItems(buildSlavePtn, content, multiline=False)
        moduleJobBuilds = [('%s@%s' % (x[0], x[1]), 'ci-build-slave', int(x[2])) for x in founds]
        return moduleJobBuilds
            
    def getConsole(self, job, build):
        return GetBuildConsole(self.kongJenkins, job, build, user=self.kongUser, password=self.kongPassword)
    
    def jobBuildUrl(self, job, build):
        return '%s/view/KONG-CI/job/%s/%s/console' % (self.kongJenkins, job, build)
                
def outputResult(jkn, latestBuild, moduleUrlWarnings):
    url = jkn.jobBuildUrl('ci-manager', latestBuild)
    print('Build warnings for ci-manager build %s (%s)\n' % (latestBuild, url))
    totalWarnings = []
    for module, url, warnings in sorted(moduleUrlWarnings, key=itemgetter(0)):
        print('\n=== MODULE=%s, URL=%s, warnings=%s ===\n' % (module, url, len(warnings)))
        for w in warnings:
            print('%s' % w)
        totalWarnings += warnings
    total = len( list(set(totalWarnings)) )
    print('\nTotal warnings=%s' % total)
    
    fileWarnings = sortWarningByFile(moduleUrlWarnings)
    for f in sorted(fileWarnings.keys()):
        warnings = fileWarnings[f]
        print('\n=== FILE=%s ==' % f)
        for w in warnings:
            print('%s' % w)
    
    print('\nsummary:')
    print('\ttotal warnings=%s, total files=%s, total modules=%s\n' % (total, len(fileWarnings.keys()), len(moduleUrlWarnings)))

def sortWarningByFile(moduleUrlWarnings):
    fileWarnings = {}
    
    allWarnings = []
    for _, _, warnings in moduleUrlWarnings:
        allWarnings += warnings
    allWarnings = list(set(allWarnings))
    
    wp = WarningParser()
    for warning in allWarnings:
        fname = wp.getFileName(warning)
        if fname in fileWarnings:
            fileWarnings[fname].append(warning)
        else:
            fileWarnings[fname] = [warning]
    return fileWarnings


def notify(jkn, buildId, moduleUrlWarnings):
    sender = 'kong@windriver.com'
    tos = ['kun.duan@windriver.com',
           'dapeng.zhang@windriver.com',
           'yanyan.liu@windriver.com',
           'xiaozhan.li@windriver.com',
           'dong.liu@windriver.com',
           'yabing.liu@windriver.com',
           'libo.chen@windriver.com',
          ]
    to = ';'.join(tos)
    # debug
    #to = 'libo.chen@windriver.com'
    subject = 'kong build warnings for ci-manager %s' % buildId
    
    ciManagerUrl = jkn.jobBuildUrl('ci-manager', buildId)
    ciKongWarningBuild = int(os.getenv('BUILD_NUMBER', '0'))
    url = jkn.jobBuildUrl('ci-kong-warning', os.getenv('BUILD_NUMBER', ''))
    body = 'ci-manager build %s (%s) has:\n' % (buildId, ciManagerUrl) + \
           '   total %s build warnings\n' % getNum(moduleUrlWarnings) + \
           '   see ci-kong-warning #%s (%s) in details' % (ciKongWarningBuild, url)
    print(SendEmail(sender, to, subject, body))


def getNum(moduleUrlWarnings):
    allWarnings = []
    for _, _, warnings in moduleUrlWarnings:
        allWarnings += warnings
    allWarnings = list(set(allWarnings))    
    return len(allWarnings)


def main():
    moduleUrlWarnings = []
    allWarnings = []

    parser = WarningParser()
    jkn = KongTestJenkins(kongJenkins, kongUser, kongPassword)
    latestBuild = jkn.getLatestBuild()
    moduleJobBuilds = jkn.getBuildSlaves(latestBuild)

    for module, job, build in moduleJobBuilds:
        content = jkn.getConsole(job, build)
        warnings = parser.extractWarnings(content)
        allWarnings += warnings
        url = jkn.jobBuildUrl(job, build)
        moduleUrlWarnings.append( (module, url, warnings) )
    
    outputResult(jkn, latestBuild, moduleUrlWarnings)
    notify(jkn, latestBuild, moduleUrlWarnings)
        
if __name__ == '__main__':
    main()
    