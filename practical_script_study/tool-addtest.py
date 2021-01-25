#!/usr/bin/env python

testCaseFile = 'tt'
reportFile = 'KongTestPlanToReport.py'

testCasesAtReportFile = []
testCases = []

reportStr = ''

def readFile(fileName):
    with open(fileName, 'r') as fd:
        content = fd.read()
    return content

def printTestCase(name, testCases):
    print '== test cases existed in %s' % name
    for x in testCases: print x
    print 'total: %s\n' % len(testCases)


def removeETA(version):
    return version.split('ETA')[0]


def main():        
    reportFileContent = readFile(reportFile)
    
    reportStr = ''
    with open(testCaseFile, 'r') as fd:
        lines = fd.readlines()
        for line in lines:
            line = line.strip().replace(' ', '')
            if line:
                # use the separator "-IP" instead of "-" since some test cases 
                # have "-" for their test case name
                testName, version = line.split('-IP') 
                version = 'IP' + version
                newTestName = testName + ' - ' + removeETA(version)
                
                if reportFileContent.find(newTestName) != -1:
                    testCasesAtReportFile.append(newTestName)
                else:
                    reportStr += '\'%s\' : \'Blocked\',' % newTestName + '\n'
            else:
                mapStr += '\n'
                reportStr += '\n'
    
    print mapStr
    print '='*22
    print reportStr
    
    printTestCase(reportFile, testCasesAtReportFile)

main()
