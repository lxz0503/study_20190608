#!/usr/bin/env python

import os, time, shutil

from Config import *

def Cleanup(server):
    # get server directories to clean up
    # get cleanup policy
    # clean up 
    config = Vx7Config(server)
    covDir = config.GetPreventRunDir() + '/CoverityRuns'
    for eachDir in os.listdir(covDir):
        fullPath = covDir + '/' + eachDir
        if CoverityRecordExpired(fullPath):
            print 'remove %s' % fullPath
            shutil.rmtree(fullPath)
    

def CoverityRecordExpired(coverityDirName):
    now = time.time()
    if (now - GetCoverityDateTime(coverityDirName)) > (4 * 24 * 3600.00):
        return True
    else:
        return False
        
        
def GetCoverityDateTime(fullCoverityDirName):  
    """ prevent-21Aug-22:54:32 """
    assert os.path.basename(fullCoverityDirName).startswith('prevent-')
    return os.path.getmtime(fullCoverityDirName)
	   
   
def main():
    Cleanup('pek-cc-pb05l')
    
if __name__ == '__main__':
    main()
    
