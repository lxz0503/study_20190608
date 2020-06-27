""" this is for ftp test, if you want to put or get file from
one linux server to another linux server,this can be run on 168 server """
#!/usr/bin/env python
#encoding=UTF-8

import pexpect,sys

def ftp_file(server, userName, passwd, cmd):
    s = pexpect.spawn('ftp %s' % server)
    #s.logfile = sys.stdout #this is for debug
    s.expect('(?i)Name .*:', timeout=5) #ignore N or n
    s.sendline(userName)
    s.expect('(?i)Password:') #ignore P or p
    s.sendline(passwd)
    s.expect('ftp>')
    s.sendline('pwd')
    s.expect('ftp>')
    s.sendline('ls')
    s.expect('ftp>')
    #s.sendline('delete ntp.conf')
    #s.expect('ftp>')

    s.sendline(cmd)
    s.expect('ftp>')
    #s.interact() #after this, the ftp operation is left to your hand
    s.sendline('quit')
    s.expect('Goodbye')

    s.close()

def main():
    server = "128.224.166.211"
    userName = "windriver"
    passwd = "windriver"
    cmd = "put ntp.conf"
    ftp_file(server,userName,passwd,cmd)

if __name__ == "__main__":
    main()
