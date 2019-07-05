#!/usr/bin/env python
# this script is used to analyze test result and generate test_result.log
import os
import resultDir

def analyze(dir):
    os.chdir(dir)
    cmd = """grep -rI ".*: Passed" ./ | awk '{print $2 $3}' | grep -v cmd"""
    process = os.popen(cmd)
    output1 = process.read()
    process.close()

    cmd = """grep -rI "FAILED" ./ | grep "<<" | awk '{print $2 $3}' | grep -v cmd"""
    process = os.popen(cmd)
    output2 = process.read()
    process.close()
    
    cmd = """grep -rI "INCONCLUSIVE" ./ | awk '{print $2 $3}' | grep -v cmd | grep -v '^$'"""
    process = os.popen(cmd)
    output3 = process.read()
    process.close()
    
    with open("test_result.log",'w') as fp:
        fp.write(output1)
        fp.write(output2)
        fp.write(output3)    
        
def main():
    dir = resultDir.enterDir()
    analyze(dir)

if __name__ == '__main__':
    main()
