#!/usr/bin/env python

import os

def enterDir():
    result_dir = "/home/windriver/ANVL/ANVL_Result"
    dir_list = sorted(os.listdir(result_dir))
    dir_list = sorted(dir_list,  key=lambda x: os.path.getmtime(os.path.join(result_dir, x)))
    print dir_list[-1]
    dir = "/home/windriver/ANVL/ANVL_Result" + "/" + dir_list[-1]
    #print dir
    return dir
	
	
def main():
    enterDir()
	
	
if __name__ == '__main__':
    main()


