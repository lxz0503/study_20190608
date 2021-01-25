#!/usr/bin/ env python3
# coding:utf-8
# install python-jenkins
import jenkins

# server = jenkins.Jenkins('http://pek-testharness-s1.wrs.com:8080/view/KONG-CI/', username='xli3', password='3333xli3')
# build_id = server.get_job_info('ci-manager')['lastCompletedBuild']['number']
# print(build_id)      # this is current 2850
# build_info = server.get_build_info('ci-manager', build_id)
# # print(build_info)
# build_job = 'ci-build-manager'
# slave_build_id = server.get_job_info(build_job)['lastCompletedBuild']['number']
# print(slave_build_id)     # get real build ID
# get every module and build ID

# =====================================
import requests
def GetJobJson(jenkinsWeb, job, user=None, password=None):     #ci-manager     'http://pek-testharness-s1.wrs.com:8080'
    try:
        url = jenkinsWeb + '/job/' + job + '/api/json'
        if user is None:
            r = requests.get(url)  # requests support the build name with space while urlopen does not
        else:
            r = requests.get(url, auth=(user, password))
    except requests.exceptions.RequestException as e:
        print("Request Error: " + str(e))
        print("      (url [" + url + "] probably wrong)")
        exit(2)
    return r.json()          # return a dict


def GetJobBuildsFromMultiJob(jenkinsWeb, jobName, buildId, user=None, password=None):      # ci-manager   2850
    r = GetJobJson(jenkinsWeb, jobName, user, password)
    # rets = []
    # for x in r['builds']:
    #     if x['number'] == buildId:
    #         for y in x['subBuilds']:
    #             rets.append((y['jobName'], y['buildNumber']))
    #         break
    # return rets
    return r['builds']


if __name__ == '__main__':
    # r = GetJobJson('http://pek-testharness-s1.wrs.com:8080', 'ci-manager', 'xli3', '3333xli3')
    # # print(r['builds'])
    r = GetJobBuildsFromMultiJob('http://pek-testharness-s1.wrs.com:8080', 'ci-manager', '2850', 'xli3', '3333xli3')
    print(r)

# one module warning as below
#  http://pek-testharness-s1.wrs.com:8080/view/KONG-CI/job/ci-build-slave/100080/consoleFull
# http://pek-testharness-s1.wrs.com:8080/view/KONG-CI/job/ci-build-manager/2814/console

# from above website, you can get below information such as module name and build ID,
# then you can compose a url: http://pek-testharness-s1.wrs.com:8080/view/KONG-CI/job/ci-build-slave/100030/console
# to get the console log, and then parser

# java -jar /net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/package/jenkins-cli.jar -s http://pek-testharness-s1.wrs.com:8080 build ci-build-slave           -p BRANCH=SPIN:/buildarea1/svc-cmnet/SPIN/vx20210120163205_vx_2103 -p NEWCOMMIT=SPIN -p MODULE=CRYPTO -p BSP=vxsim_linux -v -w --username svc-cmnet --password december2012!
# WARNING: An illegal reflective access operation has occurred
# WARNING: Illegal reflective access by hudson.remoting.RemoteClassLoader (file:/net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/package/jenkins-cli.jar) to method java.lang.ClassLoader.getClassLoadingLock(java.lang.String)
# WARNING: Please consider reporting this to the maintainers of hudson.remoting.RemoteClassLoader
# WARNING: Use --illegal-access=warn to enable warnings of further illegal reflective access operations
# WARNING: All illegal access operations will be denied in a future release
# Failed to authenticate with your SSH keys.
# Started ci-build-slave #100030