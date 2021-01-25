#!/usr/bin/env python

# features:
#    - create rerunNighlyTest.sh to re-run all failed and blocked tests
#    - create an email report template

import os
import argparse
import sys

from KongNightlyRerun import ReadNightlyTest

def parseArgument():
    parser = argparse.ArgumentParser(description='create nightly rerun test')
    parser.add_argument('--git', action='store', dest='git', help='git path (required)')
    parser.add_argument('--release', action='store', dest='release', help='LTAF release (required)')
    parser.add_argument('--component', action='store', dest='component', help='LTAF component (required)')
    parser.add_argument('--tag', action='store', dest='tag', help='LTAF tags (required)')
    parser.add_argument('--date', action='store', dest='date', help='LTAF date (required)')
    args = parser.parse_args()

    if (args.release is None) or (args.component is None) or (args.tag is None) or (args.date is None):
        parser.print_help()
        exit(1)
    return args

def createRerunScript(scriptName, nightlyRecords, gitPath):
    needLockMods = ('EDOOM', 'CORE_SAFETY', 'OPENSSL_FIPS',)
    modTests = createModTestMap(nightlyRecords)

    with open(scriptName, 'w') as fd:
        for mod in modTests:
            if mod in needLockMods:
                fd.write('sudo rm -f /tmp/wrtool_lock' + os.linesep)
            cmd = './runKong.sh buildTest -g %s -m %s -c %s 2>&1 | tee %s.log' % (gitPath, mod, ','.join(modTests[mod]), mod)
            fd.write(cmd + os.linesep)
            if mod in needLockMods:
                fd.write('sudo rm -f /tmp/wrtool_lock' + os.linesep*2)
    os.system('chmod 755 %s' % scriptName)
    print('%s created' % scriptName)

def createModTestMap(nightlyRecords, withIPVersion=False): 
    modTests = {}
    for record in nightlyRecords:
        if record.testSuite not in modTests:
            modTests[record.testSuite] = []
        if withIPVersion:
            modTests[record.testSuite].append( record.testName )
        else:
            modTests[record.testSuite].append( removeIPVersion(record.testName) )
    return modTests

def removeIPVersion(testName):
    return testName.split('-IPv')[0].strip()

def createReportEmail(nightlyRecords):
    print('\n')
    numFailed  = len(filter(lambda x:x.status == 'Fail', nightlyRecords))
    numBlocked = len(filter(lambda x:x.status == 'Blocked', nightlyRecords))
    report = 'Network Kong has '
    if numFailed > 0:
        report += '%s failed tests' % numFailed
    if numBlocked > 0:
        if numFailed > 0:
            report += ' and '
        report += '%s blocked tests' % numBlocked
    report += '\n'

    modTests = createModTestMap(nightlyRecords, withIPVersion=True)
    for mod in modTests:
        report += '\t%s\n' % mod
        for test in modTests[mod]:
            report += '\t\t%s : passed after being rerun\n' % test
    print(report)
    
def main():
    scriptName = 'rerunNighlyTest.sh'
    args = parseArgument()
    nightlyRecords = ReadNightlyTest(args.release, args.component, args.tag, args.date)
    notPassedNightlyRecords = filter(lambda x:x.status != 'Pass', nightlyRecords)
    
    createRerunScript(scriptName, notPassedNightlyRecords, args.git)
    
    createReportEmail(notPassedNightlyRecords)
    
if __name__ == '__main__':
    main()
    