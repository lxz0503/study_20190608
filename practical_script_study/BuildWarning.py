#!/usr/bin/env python

import os, sys, argparse, re
from logging import *
from operator import itemgetter


"""
diab:
"acos.c", line 95: warning (etoa:1025): division by zero
"acosh.c", line 57: warning (etoa:1025): division by zero

ccpentium:
afcjk.c:706: warning: conversion to 'FT_Byte' from 'int' may alter its value
ccarm:
etoa_decode.c:1298: warning: passing argument 2 of 'is_operator_function_name' from incompatible pointer type

icc:
cplusLib.c(126): warning #1418: external function definition with no prior declaration
"""

diabWarning = 'warning \(etoa:'
gccWarning = ': warning:'
iccWarning = ': warning #'

compilerWarnings = {'diab':diabWarning, 'gnu':gccWarning, 'icc':iccWarning}

def FindWarning(content, pattern):
    """ find a list of all the warnings in a content (str) """
    warnings = []
    lines = content.split('\n')
    for line in lines:
        if re.search(pattern, line):
            warnings.append(line)
    uniqueWarnings = sorted(list(set(warnings)))
    return uniqueWarnings

    
def CountWarning(warnings, warningType):
    """ input: a list of warining and warningType
        output: a list of (file, # of warnings) in reverse order
    """
    assert warningType in ('diab', 'gnu', 'icc')
    if warningType == 'diab':
        filePattern = '\"(.*?)\"'
    elif warningType == 'gnu':
        filePattern = '(.*?):'
    else: # icc
        filePattern = '(.*?)\('
    summary = {}
    for w in warnings:
        #print '====%s' % w
        fileName = re.match(filePattern, w)
        if fileName:
            fname = fileName.groups()[0]
            #print fname
            if fname in summary:
                summary[fname] += 1
            else:
                summary[fname] = 1
        else:
            error('error to find file name')
            exit(1)
    return sorted(summary.items(), key=itemgetter(1), reverse=True)
    

def SummaryWarning(content):
    print '='*60
    warningHeader = 'WARNING-REPORT:'
    for compiler in compilerWarnings.keys():
        warnings = FindWarning(content, compilerWarnings[compiler])
        print '\n%s %s WARNINGS TOTAL=%s' % (warningHeader, compiler.upper(), len(warnings))
        files = CountWarning(warnings, compiler)
        for e in files:
            print '%s     %s has %s warning(%s)' % (warningHeader, e[0], e[1], compiler)
        for w in warnings: print '\t%s' % w
    print '='*60
    return 0


def ReportWarning(buildLog):
    """ warning #, report list """
    print '\nAnalyzing the build log: %s\n' % buildLog
    warningNum = 0
    reportList = []

    with open(buildLog, 'r') as fd:
        content = fd.read()
    
    print '='*60
    reportList.append( '='*60 )
    warningHeader = 'WARNING-REPORT:'
    for compiler in compilerWarnings.keys():
        warnings = FindWarning(content, compilerWarnings[compiler])
        if len(warnings) > warningNum:
            warningNum = len(warnings)
        print '\n%s %s WARNINGS TOTAL=%s' % (warningHeader, compiler.upper(), len(warnings))
        reportList.append( '\n%s %s WARNINGS TOTAL=%s' % (warningHeader, compiler.upper(), len(warnings)) )
        files = CountWarning(warnings, compiler)
        for e in files:
            print '%s     %s has %s warning(%s)' % (warningHeader, e[0], e[1], compiler)
            reportList.append( '%s     %s has %s warning(%s)' % (warningHeader, e[0], e[1], compiler) )
        for w in warnings: 
            print '\t%s' % w
            reportList.append( '\t%s' % w )
    print '='*60
    reportList.append( ' ' )
    reportList.append( '='*60 )
    return warningNum, reportList
    
    
def main():
    with open('./test/nightlyBuild-diab-gnu.log', 'r') as fd:
        fc = fd.read()
    SummaryWarning(fc)

    
def AnalyzeBuildMain():
    basicConfig(level=INFO)
    parser = argparse.ArgumentParser(description='Analyze Build Log')
    parser.add_argument('--log', action='store', dest='logFile', help='specify build log file to analyze (required)')
    results = parser.parse_args()
    logFile = results.logFile
    
    if logFile is None:
        parser.print_help()
        exit(1)
    if not os.path.exists(logFile):
        error('cannot find log file')
        exit(1)
        
    with open(logFile, 'r') as fd:
        fc = fd.read()
    ret = SummaryWarning(fc)
    print '%s retcode=%s' % (os.path.basename(sys.argv[0]), ret)
    sys.exit(ret) # use sys.exit() for the exit code of a Python script


if __name__ == '__main__': AnalyzeBuildMain()    
