#!/usr/bin/env python

import os, sys, argparse, re
from logging import *

def SearchInfo(content, pattern, after=0, before=0,lineSeparator='\n'):
    """ search several lines in content by using pattern """
    lines = content.split(lineSeparator)
    found = None
    for line in lines:
        if re.search(pattern, line):
            found = line
            break # find the 1st matched
    if found is None:
        return ''
    else:
        i = lines.index(found)
        lineFrom = i - before
        if lineFrom < 0:
            error('range minimum error')
            exit(1)
        lineTo = i + after + 1
        if lineTo > len(lines):
            error('range maximum error')
            exit(1)
        lineRange = range(lineFrom, lineTo)
        matchedLines = filter(lambda x:lines.index(x) in lineRange, lines)
        retStr = ''
        for line in matchedLines:
            retStr += line + lineSeparator
        return retStr


class TestResult():
    def __init__(self, total=0, passed=0, failed=0, error=0, skip=0):
        debug('entering class TestResult::__init__')
        self.total = total
        self.passed = passed
        self.failed = failed
        self.error = error
        self.skip = skip
        self.results = [] # each element is (testCaseName, status, errorInfo, testClassName)

    # public
    def AddPassed(self, testCase, info='', testClassName='default'):
        self.AddResult(testCase, 'passed', info=info, testClassName=testClassName)

    def AddFailed(self, testCase, failedInfo, testClassName='default'):
        self.AddResult(testCase, 'failed', info=failedInfo, testClassName=testClassName)

    def AddError(self, testCase, errorInfo, testClassName='default'):
        self.AddResult(testCase, 'error', info=errorInfo, testClassName=testClassName)
       
    def AddSkip(self, testCase, skipInfo, testClassName='default'):
        self.AddResult(testCase, 'skip', info=skipInfo, testClassName=testClassName)
    
    def AddResult(self, testCase, status, info='', testClassName='default'):
        assert status in ('passed', 'failed', 'error', 'skip')
        if status == 'passed':
            self.results.append((testCase, 'passed', info, testClassName))
            self.passed += 1
            self.total += 1
        elif status == 'failed':
            self.results.append((testCase, 'failed', info, testClassName))
            self.failed += 1
            self.total += 1
        elif status == 'error':
            self.results.append((testCase, 'error', info, testClassName))
            self.error += 1
            self.total += 1
        elif status == 'skip':
            self.results.append((testCase, 'skip', info, testClassName))
            self.skip += 1
            self.total += 1
        else:
            error('invalid status - should be one of passed, failed, error or skip')
        self.__ValidData()
            
    
    def GetAll(self):
        """ return a list of all test results """
        return self.results
        
    def GetPassed(self):
        """ return a list of passed test results """
        return self.__GetResults('passed')

    def GetFailed(self):
        """ return a list of failed test results """
        return self.__GetResults('failed')

    def GetError(self):
        """ return a list of error test results """
        return self.__GetResults('error')

    def GetSkip(self):
        """ return a list of skip test results """
        return self.__GetResults('skip')
    
    # private        
    def __GetResults(self, status):
        """ return a list of failed test results """
        assert status in ('passed', 'failed', 'error', 'skip')
        return filter(lambda x: x[1] == status, self.results)
            
    def __ValidData(self):
        assert self.total == self.passed + self.failed + self.error + self.skip, \
                                'internal data inconsistent'

    # public
    def CreateXMLReport(self, fileName):
        """Writes an Xunit-formatted XML file
            support: classname, failure message
            not support: testsuite name, failure type, test case time field
        """
        all = len(self.GetAll())
        #passedNum = len(self.GetPassed())
        failedNum = len(self.GetFailed())
        errorNum = len(self.GetError())
        skipNum = len(self.GetSkip())
        stream = open(fileName, 'w')
        stream.write(
            u'<?xml version="1.0" encoding="UTF-8"?>\n'
            u'<testsuite name="default-test-suite" tests="%s" '
            u'failure="%s" errors="%s" '
            u'skips="%s">\n' % (all, failedNum, errorNum, skipNum))
        
        for eachResult in self.results:
            status = eachResult[1]
            stream.write('\t<testcase classname="%s" name="%s">\n' % (eachResult[3], eachResult[0]))
            if status == 'failed':
                stream.write('\t\t<failure type="unknown" message="%s"></failure>\n' % eachResult[2])
            elif status == 'error':
                stream.write('\t\t<error type="unknown" message="%s"></error>\n' % eachResult[2])
            elif status == 'skip':
                stream.write('\t\t<skipped type="unknown" message="%s"></skipped>\n' % eachResult[2])
            elif status == 'passed':
                pass
            else:
                raise
            stream.write('\t</testcase>\n')

        stream.write('</testsuite>\n')
        stream.close()

# end of class TestResult        
          
def main():
    pass

if __name__ == '__main__': main()
