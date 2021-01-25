#!/usr/bin/env python

from sys import exit
from logging import *

# package jenkinsapi
import jenkinsapi
from jenkinsapi.jenkins import Jenkins
from jenkinsapi import api

# package python jenkins
import jenkins
import json, sys, urllib2, os, re
import requests


class myconfig:
    user = 'svc-qctool'
    password = 'ohm.ahda'

def PrettyPrintJson(jsonData):
    print 'ret json:', json.dumps(jsonData, sort_keys=True, indent=4, separators=(',', ': '))
    
    
def __GetOneBuildStatus(jenkinsWeb, job, build, content, user=None, password=None):
    """ this function has the limit and it does not work for the job without build records """
    try:
        if build == 'lastBuild':
            url = jenkinsWeb + '/job/' + job + '/' + build + content
        else:
            url = jenkinsWeb + '/job/' + job + '/' + str(build) + content
        if user is None:
            r = requests.get(url)    # requests support the build name with space while urlopen does not
        else:
            r = requests.get(url, auth=(user, password))
    except requests.exceptions.RequestException, e:
        print "Request Error: " + str(e.code) 
        print "      (job name [" + job + "] probably wrong)"
        return ''
        exit(2)
    return r
    
    
def GetBuildStatus(jenkinsUrl, jobName, buildId, user=None, password=None):
    """ return the status of a build of a Jenkins job
        status: SUCCESS, FAILURE, INPROGRESS (None) and latest job number
    """
    if buildId is None:
        return ''
    
    retJson = __GetOneBuildStatus(jenkinsUrl, jobName, buildId, '/api/json', user, password).json()

    if retJson.has_key('result') and retJson.has_key('number'):
        status = retJson['result']
        if status is None:
            status = 'INPROGRESS'
        return status
    else:
        print '%s has no keys for either result or number' % jobName
        return ''
    

def GetBuildStatusAndFullName(jenkinsUrl, jobName, buildId, user=None, password=None):
    """ return the status of a build of a Jenkins job
        status: SUCCESS, FAILURE, INPROGRESS (None) and latest job number
    """
    if buildId is None:
        return '', None
    
    retJson = __GetOneBuildStatus(jenkinsUrl, jobName, buildId, '/api/json', user, password).json()

    if retJson.has_key('result') and retJson.has_key('number'):
        status = retJson['result']
        if status is None:
            status = 'INPROGRESS'
        return status, retJson['fullDisplayName']
    else:
        print '%s has no keys for either result or number' % jobName
        return '', retJson['fullDisplayName']
    
    
def GetLatestJobStatus(jenkinsUrl, jobName, user=None, password=None):
    """ return the latest status of a Jenkins job
        status: SUCCESS, FAILURE, INPROGRESS (None) and latest job number
    """
    rJson = __GetOneBuildStatus(jenkinsUrl, jobName, 'lastBuild', '/api/json', user, password).json()    # return value is json, so change to python dict

    if rJson.has_key('result') and rJson.has_key('number'):
        status = rJson['result']
        if status is None:
            status = 'INPROGRESS'
        return status, rJson['number']
    else:
        print '%s has no result key' % jobName
        return ('', 0)


def GetJobBuildTimeStamp(jenkinsUrl, jobName, buildId, user, password, duration=False):
    """ use python jenkins here since jenkinsapi does not work for unknown reason """
    try:
        server = jenkins.Jenkins(jenkinsUrl, username=user, password=password)
        if duration:
            return (server.get_build_info(jobName, buildId)['timestamp'] + server.get_build_info(jobName, buildId)['duration'])/1000.0
        else:
            return server.get_build_info(jobName, buildId)['timestamp']/1000.0
    except:
        return None
    

def GetJobLastBuildNumber(jenkinsUrl, jobName, user, password):
    """ use python jenkins here since jenkinsapi does not work for unknown reason """
    try:
        server = jenkins.Jenkins(jenkinsUrl, username=user, password=password)
        return server.get_job_info(jobName)['lastCompletedBuild']['number']
    except:
        return None
    
    """
    # do not why the following implementation based on jenkinsapi does not work
    j = Jenkins(jenkinsUrl, 'svc-cmnet', 'december2012!')

    try:
        job = j[jobName]
    except KeyError:
        print 'job name %s is not valid' % jobName
        return None
    return job.get_last_buildnumber()
    """

def GetBuildConsole(jenkinsUrl, jobName, buildId, user=None, password=None):
    """ return the console content of a job build
    """
    r = __GetOneBuildStatus(jenkinsUrl, jobName, buildId, '/consoleFull', user, password)
    return r.text
    

def GetDownStreamJob(jenkinsUrl, project, build, user=None, password=None):
    """ return project, build """
    if user is None:
        j = Jenkins(jenkinsUrl)
    else:
        j = Jenkins(jenkinsUrl, username=user, password=password)
    job = j[project]
    dsProjectNames = job.get_downstream_job_names()
    if dsProjectNames == []:
        return None, None
    else:
        dsProject = dsProjectNames[0]
    dsBuild = GetDownStreamBuildId(jenkinsUrl, project, build, dsProject, user, password)
    return dsProject, dsBuild
    
            
def GetDownStreamBuildId(jenkinsUrl, jobName, buildId, downStreamJob, user=None, password=None):
    _, dsMaxId = GetLatestJobStatus(jenkinsUrl, downStreamJob, user, password)
    if dsMaxId == 0:
        return 0

    j = Jenkins(jenkinsUrl, username=user, password=password)
    dsJob = j[downStreamJob]
    dsBuildIds = dsJob.get_build_ids()
    for dsBuildId in dsBuildIds:
        usBuildId = GetUpStreamBuildId(jenkinsUrl, downStreamJob, dsBuildId, jobName, user, password)
        if usBuildId == buildId:
            return dsBuildId
    return 0                
        

def GetUpStreamBuildId(jenkinsUrl, jobName, buildId, upStreamJob, user=None, password=None):
    try:
        rJson = __GetOneBuildStatus(jenkinsUrl, jobName, buildId, '/api/json', user, password).json()
    except urllib2.HTTPError, e:
        print "URL Error: " + str(e.code) 
        print "      (job name [" + jobName + "] probably wrong)"
        return 2

    if rJson.has_key('actions'):
        for d in rJson['actions']:
            if d.has_key('causes'):
                for d1 in d['causes']:
                    if d1.has_key('upstreamProject'):
                        if d1['upstreamProject'] == upStreamJob:
                            return d1['upstreamBuild']
        return 0                    
    else:
        return 0
        

def GetBuildServer(jenkinsUrl, jobName, buildId, user=None, password=None):
    retJson = __GetOneBuildStatus(jenkinsUrl, jobName, buildId, '/api/json', user, password).json()
    #PrettyPrintJson(retJson)
    if retJson.has_key('builtOn'):
        return retJson['builtOn']
    else:
        print '%s has no result key' % jobName
        return ''


def GetQueuedJobs(queue):
    assert isinstance(queue, jenkinsapi.queue.Queue)
    rets = []
    for item in queue._data['items']:
        queueId = item['id']
        userId = item['actions'][1]['causes'][0]['userId']
        taskName = item['task']['name']
        inQueueSince = item['inQueueSince']
        rets.append( (queueId, userId, taskName, inQueueSince) )
    return rets


class QueryBuildRunning_Static:
    first = {'ci-rerun-test' : True, 
             'ci-rerun-test-rm' : True,
             'ci-build-slave' : True,
            }
    buildIds = {} # {job: buildIds, ...}

    
def QueryBuildRunning(jenkinsUrl, jobName, user=None, password=None, optimized=True):
    """ return: a list, each member is (server, buildId), e.g. (u'kong-rvm-102', 19769) """
    rets = []
    buildIds = GetJobBuildIds(jenkinsUrl, jobName, user, password)

    if optimized:
        if QueryBuildRunning_Static.first[jobName]:
            QueryBuildRunning_Static.buildIds[jobName] = buildIds
    else:
        QueryBuildRunning_Static.buildIds[jobName] = buildIds
    
    for buildId in QueryBuildRunning_Static.buildIds[jobName]:
        status = GetBuildStatus(jenkinsUrl, jobName, buildId, user, password)
        if status == 'INPROGRESS':
            server = GetBuildServer(jenkinsUrl, jobName, buildId, user, password)
            rets.append((server, buildId))

    if optimized:
        QueryBuildRunning_Static.buildIds[jobName] = map(lambda x: x[1], rets)
        QueryBuildRunning_Static.first[jobName] = False
        
    return rets
       

def GetJobBuildIds(jenkinsUrl, jobName, user=None, password=None): 
    rets = []
    j = jenkins.Jenkins(jenkinsUrl, username=user, password=password)
    jobInfo = j.get_job_info(jobName)
    return map(lambda x: x['number'], jobInfo['builds'])


def IsAnyProjectRunning(jenkinsWeb, user=None, password=None):
    j = jenkins.Jenkins(jenkinsWeb, user, password)
    allProjects = [x['name'] for x in j.get_jobs()]

    for project in allProjects:
        status, _ = GetLatestJobStatus(jenkinsWeb, project, user, password)
        if status == 'INPROGRESS':
            return True
    return False

# the functions above have been tested

def StopBuild(jobName, buildId, jenkinsUrl):
    try:
        url = jenkinsUrl + '/job/' + jobName + '/' + str(buildId) + '/stop'
        data = {}
        ret   = urllib2.Request(url, data)
    except urllib2.HTTPError, e:
        print "URL Error: " + str(e.code) 
        print "      (job name [" + jobName + "] probably wrong)"
        sys.exit(2)
    print ret
    

def __GetJobJson(jenkinsWeb, job, user=None, password=None):
    try:
        url = jenkinsWeb + '/job/' + job + '/api/json' 
        if user is None:
            r = requests.get(url)    # requests support the build name with space while urlopen does not
        else:
            r = requests.get(url, auth=(user, password))
    except requests.exceptions.RequestException, e:
        print "Request Error: " + str(e.code) 
        print "      (url [" + url + "] probably wrong)"
        exit(2)
    return r.json()


def GetSubJobsFromMultiJob(jenkinsWeb, multiJobName, user=None, password=None):
    rJson = __GetJobJson(jenkinsWeb, multiJobName, user, password)
    #PrettyPrintJson(rJson)
    rets = []
    for x in rJson['downstreamProjects']:
        rets.append(x['name'])
    return rets


def GetJobBuildsFromMultiJob(jenkinsWeb, jobName, buildId, user=None, password=None):
    rJson = __GetJobJson(jenkinsWeb, jobName, user, password)

    rets = []
    for x in rJson['builds']:
        if x['number'] == buildId:
            for y in x['subBuilds']:
                rets.append( (y['jobName'], y['buildNumber']) )
            break
    return rets
    

def GetParentBuildIdFromMultiJob(jenkinsWeb, multiJob, jobName, jobBuildId, user=None, password=None):
    rJson = __GetJobJson(jenkinsWeb, multiJob, user, password)
    parentBuildId = 0
    for x in rJson['builds']:
        for y in x['subBuilds']:
            if y['jobName'] == jobName and y['buildNumber'] == jobBuildId:
                parentBuildId = y['parentBuildNumber']
                break
    return parentBuildId


def TryJenkins():
    print GetLatestJobStatus('http://128.224.159.246:8080', 'kong-dev-test')
    exit(0)
    print IsAnyProjectRunning('http://128.224.159.246:8080', 'svc-cmnet', 'december2012!')

    print '==== using jenkinsapi package ===='
    jenkinsWeb = 'http://128.224.159.246:8080'
    j = Jenkins(jenkinsWeb, username='svc-qctool', password='ohm.ahda')
    print '== all projects:\n%s\n' % j.keys()
    
    #job = j['v7-multi-build']
    #project = 'vx7-dev-branch-truely-build'

    project = 'vxworks-vx7-vxsim-CRYPTO'
    buildId = 171
    project = 'vxworks-vx7-vxsim-VRRP' # last project
    buildId = 92
        
    job = j[project]
    #exit(0)
    print '== project all member functions:\n'
    for op in dir(job):
        print op
    print
    
    print '== api member functions:%s\n' % dir(api)
    #print GetBuildConsole(jenkinsWeb, project, buildId)

    #print '== project config:\n%s\n' % job.get_config()  # get a job config xml file
    print '== project %s build %s status:%s\n' % (project, buildId, GetBuildStatus(jenkinsWeb, project, buildId))
    print '== project last build number:%s\n' % job.get_last_buildnumber()
    print '== project last completed build number:%s\n' % job.get_last_completed_buildnumber()
    print '== project last good build number:%s\n' % job.get_last_good_buildnumber()
    print '== project is running?:%s\n' % job.is_running()
    dsProject, dsBuildId = GetDownStreamJob(jenkinsWeb, project, buildId)
    print '== project %s build %s downstream is project %s build %s' % (project, buildId, dsProject, dsBuildId)
    
    print '== project all build ids:'
    for i in job.get_build_ids(): print i,
    print 

    print '\n==== using jenkins package ===='
    jenkinsWeb = 'http://128.224.159.246:8080'
    j = jenkins.Jenkins(jenkinsWeb, username='svc-qctool', password='ohm.ahda')
    print dir(j)
    #newEmail = 'libo.chen@windriver.com huabing.chu@windriver.com'
    #ModifyEmailUser(newEmail)
    
    exit(0)  

    print job.print_data()
    print job.baseurl
    print job.jenkins
    
    #basicConfig(level=INFO)
    #print j['make-rpm'].invoke()    # trigger to build a job
    print j['make-rpm'].is_running()
    
    print job.python_api_url(job.baseurl) # not often used
    
    n = job.get_last_build()
    #print n, n.get_number(), type(n), dir(n)
    print n.get_result_url()
    print api.get_build('http://localhost:8080', 'build-vip', n.get_number())
    print api.get_latest_test_results('http://localhost:8080', 'build-vip')
    
    
def try1():
    #jenkinsUrl = "http://pek-dfe-server:8080"
    jenkinsUrl = "http://vxjenkins.wrs.com:8080"
    if len( sys.argv ) > 1 :
        jobName = sys.argv[1]
    else :
        print 'usage: %s job_name' % os.path.basename(sys.argv[0])
        sys.exit(1)
        
    status = GetLatestJobStatus(jenkinsUrl, jobName)
    print '%s status is %s' % (jobName, status) 
    

def GetJobStatus(jobBuildName):
    """ input: jobBuildName, e.g. http://pek-mcbuild2.wrs.com:8070/job/03.2-Vx7-Branch-Build/VSB_BUILD_MATRIX=vsb_bsp6x_fsl_imx6_sabrelite_6_9_0_0_diab_smp_vsbCfg-Def/94
        return the status of a Jenkins job
        status: SUCCESS, UNSTABLE, NONE (building)
    """
    try:
        jenkinsStream   = urllib2.urlopen( jobBuildName + "/api/json" )
    except urllib2.HTTPError, e:
        print "URL Error: " + str(e.code) 
        print "      (job name [" + jobBuildName + "] probably wrong)"
        sys.exit(2)
    
    try:
        buildStatusJson = json.load( jenkinsStream )
        #print buildStatusJson
    except:
        print "Failed to parse json"
        sys.exit(3)
    
    if buildStatusJson.has_key( "result" ):
        return buildStatusJson["result"]
    else:
        print '%s has no result key' % jobBuildName
        sys.exit(4)
        
            
def GetMulticonfigJob(jenkinsUrl, jobName, buildId=None):
    """ return a list of jobs under a multiconfig job
    """
    if buildId is None:
        url = jenkinsUrl + '/job/' + jobName + "/lastBuild/api/json"
    else:
        url = jenkinsUrl + '/job/' + jobName + '/' + buildId + '/api/json'
    #print url
    try:
        jenkinsStream   = urllib2.urlopen( url )
    except urllib2.HTTPError, e:
        print "URL Error: " + str(e.code) 
        print "      (job name [" + jobName + "] probably wrong)"
        sys.exit(2)
    
    try:
        buildStatusJson = json.load( jenkinsStream )
        #print buildStatusJson
    except:
        print "Failed to parse json"
        sys.exit(3)
    
    if buildStatusJson.has_key( "runs" ):
        return buildStatusJson["runs"]
    else:
        print '%s has no result key' % jobName
        sys.exit(4)


def showMulticonfigJobStatus(jenkinsUrl, jobName, buildId):
    i = 0    
    subJobDicts = GetMulticonfigJob(jenkinsUrl, jobName, buildId)
    print '========'
    print 'sub jobs status:'
    for x in subJobDicts: 
        y = x['url']
        jobBuildName = y[:-1]
        #print jobBuildName
        status = GetJobStatus(jobBuildName)
        subJobName = jobBuildName.split('=')[1]
        subJobBuildId = subJobName.split('/')[1]
        if subJobBuildId == buildId:
            print '\t%s status is %s' % (subJobName, status)
            i += 1
    print 'total %s sub jobs' % i


def main():
    jenkinsUrl = "http://pek-mcbuild2.wrs.com:8070"
    print QueryBuildRunning(jenkinsUrl, 'vx7-dev-branch-truely-build')
    sys.exit(0)
    
    if len( sys.argv ) == 3 :
        jobName = sys.argv[1]
        buildId = sys.argv[2]
        
        print '==GetDownStreamBuildId'
        print GetDownStreamBuildId(jenkinsUrl, 'vx7-dev-branch-build', 19, jobName)
        
    else :
        print 'usage: %s job_name build_id' % os.path.basename(sys.argv[0])
        sys.exit(1)
            
    
if __name__ == '__main__': 
    #try1()
    TryJenkins()
    #BackupJenkinsProject()
    #main()
