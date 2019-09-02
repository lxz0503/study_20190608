""" this is for scp command, if you want to copy file from
one linux server to another linux server """
#!/usr/bin/env python
#encoding=UTF-8

import pexpect,sys

def scp_file(src, dst, passwd):
    s = pexpect.spawn('scp %s %s' % (src,dst))
    #s.logfile = sys.stdout #this is for debug
    try:
        i = s.expect(['password:', 'continue connecting (yes/no)?'], timeout=5)
        if i == 0 :
            s.sendline(passwd)
            s.expect('00:00') #if copy is ok, the ouput end is 00:00
        elif i == 1:
            s.sendline('yes')
            s.expect('password: ')
            s.sendline(passwd)
            s.expect('00:00')
    except pexpect.EOF:
        print "EOF"
        s.close()
    except pexpect.TIMEOUT:
        print "TIMEOUT"
        s.close()
#you need to close this session
    s.close()

def main():
    src = "vxWorks"
    dst = "windriver@128.224.163.8:/home/windriver"
    passwd = "windriver"
    scp_file(src,dst,passwd)

if __name__ == "__main__":
    main()
