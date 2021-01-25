#!/usr/bin/env python

testCaseFile = 'ttt'

def readFile(fileName):
    with open(fileName, 'r') as fd:
        content = fd.read()
    return content

def main():
    lines = [x for x in readFile(testCaseFile).split('\n') if x.strip()]
    for line in lines:
        tokens = line.split('ETA')
        testCaseName = tokens[0].replace(' ', '')
        print testCaseName

    print 'total %s test cases' % len(line)
main()
        