#!/usr/bin/env python3
import os
import re

def set_git_commit(dir,good_commit,bad_commit):
   os.chdir(dir)
   os.system('git bisect start')
   cmd = "git bisect good" + " " + good_commit 
   os.system(cmd)
   cmd = "git bisect bad" + " " + bad_commit
   os.system(cmd)
 
# after test,pass the test result to str
def set_git_sign(dir,str):
    if str == 'pass':
        os.chdir(dir)
        r = os.popen('git bisect good').read()    # if test result is pass,run git bisect good, then it will try another commit
        m = re.match(r"(\w+) is the first bad commit", r)
        if m is not None:
            os.system("git bisect reset")
            print("the bad commit is %s" % (m.group(1)))
            return m.group(1)

    else:
        os.chdir(dir)
        r = os.popen('git bisect bad').read()  # if test result is fail,run git bisect bad, then it will try another commit
        m = re.match(r"(\w+) is the first bad commit", r)
        if m is not None:
            os.system("git bisect reset")
            print("the bad commit is %s" % (m.group(1)))
            return m.group(1)
 
if __name__ == '__main__':
    set_git_commit("/home/windriver/Integration/vxworks","7f0a795f241d31a8aad4d1eead3bf12954ea9214","8c6da7358ad1d0651581b94b94c0527578df5bbc")
    while True:
        if set_git_sign("/home/windriver/Integration/vxworks", "fail") is not None:
            break
