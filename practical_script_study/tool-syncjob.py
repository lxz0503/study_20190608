#!/usr/bin/env python
# sync the jobs between Jenkins and KongConfig

import sys
import time
import re

import jenkins
from Jenkins import *
from KongConfig import *
    
def GetTestJob():    
    j = jenkins.Jenkins(kongJenkins, kongUser, kongPassword)
    allProjects = [x['name'] for x in j.get_jobs() if x['name'].startswith('ut-vxsim-')]
    return map(lambda x:x, allProjects)

def main():
    jenkinsJobs = GetTestJob()

    for x in allProjects:
        print x
        
main()    
