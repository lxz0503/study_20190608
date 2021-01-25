#!/usr/bin/env python

import sys
from datetime import date
from KongNightlyRerun import ReadNightlyTest, WriteNightlyTest
from LTAFInterface import ReleaseReportWriter

failedTests = [
               #'ipnet.icmp.addr_mask-IPv4',
              ]

def main_nightly_to_nightly():
    # need to change
    fromDate = '2018-04-11'
    toDate = '2018-04-10'
    
    # fixed parameters
    releaseFrom = 'vx653-integration'
    componentFrom = 'networking'
    
    releaseTo = 'vx653-integration'
    componentTo = 'networking'
    
    tags = 'KONG-nightly'
    
    nightlyRecords = ReadNightlyTest(releaseFrom, componentFrom, tags, fromDate)
    newNightlyRecords = []
    for x in nightlyRecords: 
        print x.testName
        """
        if x.testName in failedTests: 
            # handle failed test cases
            x.status = 'Fail'
            x.runDate = toDate
            x.funcPass = 0
            x.funcFail = 1
        else:
            # handle passed test cases
            x.status = 'Pass'
            x.runDate = toDate
            x.funcPass = 1
            x.funcFail = 0
        """
        x.runDate = toDate
        newNightlyRecords.append(x)            
   
    print '='*22
    for x in newNightlyRecords:
        print x
    print 'total %s old test runs' % len(nightlyRecords)
    print 'total %s new test runs' % len(newNightlyRecords)
    
    WriteNightlyTest(releaseTo, newNightlyRecords)


def main_nightly_to_release():
    # need to change
    fromDate = '2018-06-03'
    toDate = '2018-06-03'
    
    # fixed parameters
    releaseFrom = 'vx7-SR0540-features'
    componentFrom = 'networking'
    
    releaseTo = 'vx7-SR0540-features'
    componentTo = 'networking'
    
    tags = 'KONG-nightly'
    plannedSprint = 'releaseTestSprint'  # need to change per release
    plannedWeek = '2018-05-11'           # need to change per release
    requirement = 'US113581'             # need to change per release
    log = 'http://pek-cc-pb08l.wrs.com/net/pek-cc-pb08l/vxtest/vxtest1/LOG_VX7/Vx-7_Networking-Kong/vx7-SR0540-features/vx20180602090303_SR0540'                 # need to change per release
    
    nightlyRecords = ReadNightlyTest(releaseFrom, componentFrom, tags, fromDate)
    newNightlyRecords = []
    for x in nightlyRecords: 
        #print x.testName
        x.runDate = toDate
        x.log = log
        x.requirement = requirement
        newNightlyRecords.append(x)
   
    print '='*22
    for x in newNightlyRecords:
        print '%s\n' % x
    print 'total %s old test runs' % len(nightlyRecords)
    print 'total %s new test runs' % len(newNightlyRecords)
    
    writer = ReleaseReportWriter(releaseTo, plannedSprint, plannedWeek, trDomain='networking')
    for x in newNightlyRecords:
        writer.AddTestResult(x)
    writer.Store()
    
    
    
if __name__ == '__main__':    
    #main_nightly_to_nightly()
    main_nightly_to_release()
    
