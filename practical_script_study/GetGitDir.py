#!/usr/bin/env python

import sys
from Config import Vx7Config

def main():
    if len(sys.argv) != 2:
        print 'usage: %s server_name' % os.path.basename(sys.argv[0])
        exit(1)
    serverCfg = Vx7Config(sys.argv[1])
    serverCfg.SetupEnv()
    gitDir, buildDir, preventRunDir, preventTmpDir = serverCfg.GetDirs()
    print gitDir
        
if __name__ == '__main__': main()
