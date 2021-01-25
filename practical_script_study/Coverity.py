#!/usr/bin/env python

import os, sys, re
from logging import *
from operator import itemgetter
from commands import getoutput
from lxml import html

def ParsePreventIndexTxt(fileName):
    """ return a list of defects getting from prevent-index.txt 
        each list member is (checker, num)
            where num is int
    """
    if not os.path.exists(fileName):
        error('cannot find prevent-index.txt file')
        exit(1)
    with open(fileName, 'r') as fd:
        fc = fd.read()
    found = re.search('(?s)Defect occurrences found :(.*?)Processed', fc)
    if found is None:
        return []
    foundStr = found.groups()[0]
    lines = foundStr.split('\n')
    defects = []
    for e in lines:
        if e.strip() != '':
            defects.append(e.strip())
        else:
            break
    if defects == ['0']:
        return [('Total', 0)]
    FoundList = map(__HandleCheckerResult, defects)
    retList = sorted(FoundList[1:], key=itemgetter(0))
    retList = [FoundList[0]] + retList
    return retList
    

def __HandleCheckerResult(x):
    x = x.strip()
    num, checker = x.split()
    return (checker, int(num))


def ParseIndexXML(fileName):
    pass
 

def ReportCoverity(preventHtmlFile):
    """ return: coverity num, report list """
    covNum = 0
    reportList = []
    
    defectList = ParsePreventIndexTxt(preventHtmlFile.replace('html', 'txt'))
    covHeader = 'COVERITY-REPORT:'
    print '%s total %s prevent defects' % (covHeader, defectList[0][1])
    covNum = defectList[0][1]
    reportList.append( '%s total %s prevent defects' % (covHeader, defectList[0][1]) )
    defects = sorted(defectList[1:], key=itemgetter(1), reverse=True)
    print '%s refer to %s for details' % (covHeader, CreateHtmlPath(preventHtmlFile))
    reportList.append( '%s refer to %s for details' % (covHeader, CreateHtmlPath(preventHtmlFile)) )
    for e in defects:
        print '%s\t%s  %s' % (covHeader, e[0], e[1])
        reportList.append( '%s\t%s  %s' % (covHeader, e[0], e[1]) )
    return covNum, reportList


def ReportComponentCoverity(preventHtmlFile, newPreventHtmlFile, keyword):
    """ return: coverity num, report list """
    covNum = 0
    covHeader = 'COVERITY-REPORT:'
    reportList = []
    
    CreateCompIndexHtml(preventHtmlFile, newPreventHtmlFile, keyword)    
    rets = SummarizeIndexHtml(newPreventHtmlFile)

    for e in rets:
        covNum = covNum + rets[e]
        reportList.append( '%s\t%s  %s' % (covHeader, e, rets[e]) )
    reportList.append(' ')
    
    reportList.insert(0, '%s refer to %s for details' % (covHeader, CreateHtmlPath(newPreventHtmlFile)) )
    reportList.insert(0, '%s total %s prevent defects for component %s' % (covHeader, covNum, keyword) )

    for e in reportList: print e
    return covNum, reportList
            

def CreateHtmlPath(preventHtmlFile):
    htmlFile = RefinePath(preventHtmlFile)
    hostName = getoutput('hostname').split('.')[0]
    netAccessHeader = 'http://' + hostName + '/vx7/CoverityRuns/'
    covRecordPath = os.environ['PREVENT_RUN_DIR'] + '/CoverityRuns'
    if htmlFile.find(covRecordPath) == -1:
        print 'error to replace the path of prevent-index.html'
        exit(1)
    return htmlFile.replace(covRecordPath, netAccessHeader)


def RefinePath(pathStr):
    outStr = '/'.join( filter(lambda x: x != '', pathStr.split('/')) )
    if pathStr[0] == '/':
        outStr = '/' + outStr
    return outStr


def FindWarningFile(preventHtmlFile):
    warnFile = 'compiler_warnings.txt'
    htmlFile = RefinePath(preventHtmlFile)
    return os.path.dirname(preventHtmlFile) + '/' + warnFile


def FindBuildLogFile(preventHtmlFile):
    warnFile = 'build-log.txt'
    htmlFile = RefinePath(preventHtmlFile)
    return os.path.dirname(preventHtmlFile) + '/' + warnFile
        

def IsBuildPassed(preventWarningFile):
    fc = ''
    with open(preventWarningFile, 'r') as fd:
        fc = fd.read()
    if fc.find('make: *** [BUILD] Error') != -1:
        return False
    else:
        return True
    
    
def CreateCompIndexHtml(indexHtmlFile, newIndexHtmlFile, keyword):
    root = html.parse(indexHtmlFile)
    for elem in root.iter('tr'):
        children = elem.getchildren()
        if children[2].text is None: # <tr><a href=...>
            sourceFile = children[2].getchildren()[0].text # source file name
            if sourceFile == 'File':
                continue
            if sourceFile.find(keyword) != -1:
                pass
                #print sourceFile
            else:
                elem.getparent().remove(elem)

    root.write(newIndexHtmlFile)
    

def SummarizeIndexHtml(indexHtmlFile):
    rets = {}
    root = html.parse(indexHtmlFile)
    for elem in root.getiterator():
        if elem.tag == 'tr':
            children = elem.getchildren()
            if children[2].text is None:
                checker = children[1].text # Prevent CHECKER
                if checker in rets:
                    rets[checker] = rets[checker] + 1
                else:
                    rets[checker] = 1
    return rets
    

def ExtractPreventSummary(consoleOutput):        
    ptn = '(?s)(Analysis summary report:.*?)Total execution time'
    found = re.search(ptn, consoleOutput)
    if found is not None:
        return found.groups()[0]
    else:
        return ''
            
