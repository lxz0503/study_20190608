#!/usr/bin/env python

import os
import re
import sys
import pxssh
import socket


vmConfig = { 
            'pek-cc-pb02l-old.wrs.com':[
                                        'kong-vm-11',
                                        'kong-vm-12', # rerun server
                                       ],

            #'pek-cc-pb01l.wrs.com':[
            #                       'kong-vm-01', # rerun server
            #                        'kong-vm-03',
            #                        'kong-vm-04',
            #                       ],
            
            'pek-cc-pb02l.wrs.com':[
                                    'kong-vm-05',
                                    'kong-vm-06', # rerun server
                                    'kong-vm-07',
                                    'kong-vm-08', # rerun server
                                    'kong-vm-09',
                                    'kong-vm-10',
                                   ],
                 
            'pek-cc-pb05l.wrs.com':[
                                    'kong-vm-02', # rerun server
                                   ],
            }

def SendCmd(node, login, password, cmds):
    """ node as string, app as string, arg as strings """
    try:
        s = pxssh.pxssh()
        s.force_password = True
        s.login(node, login, password) # modify pxssh.py and add 2 lines
        for cmd in cmds:
            app = cmd.split(' ')[0]
            arg = ' '.join( cmd.split(' ')[1:] )
            s.sendline('%s %s' % (app, arg))
            s.prompt()
            print s.before
        s.logout()
    except pxssh.ExceptionPxssh, e:
        warning('pxssh failed to login %s' % node)
        warning(str(e))
        


def CheckServer(node, port):
    """ return (boolean, msg) 
            (True, msg) if both node and port are available for using later
            (False, msg) if either one is not available
    """
    sshPort = 22
    msg = ''
    try:
        s = socket.socket()
        s.connect((node, sshPort))
        try:
            s = socket.socket()
            s.connect((node, port))
            msg = 'port is not available'
            return (False, msg)
        except Exception:
            msg = 'node and port are available'
            return (True, msg) 
    except Exception:
        msg = 'node is not available'
        return (False, msg)
    

def CheckFile(fileName):
    fullName = os.path.dirname(os.path.realpath(__file__)) + '/' + fileName
    if not os.path.exists(fullName):
        error('file %s not existed' % fileName)
        exit(1)    
        
def main():
    login = 'svc-cmnet1'
    password = 'december2012!'

    for server in vmConfig:
        vms = vmConfig[server]
        for vm in vms:
            cmds = []
            cmds.append('vboxmanage controlvm %s poweroff' % vm)
            #cmds.append('sleep 3')
            #cmds.append('vboxmanage startvm %s --type headless' % vm)
            print server, cmds
            SendCmd(server, login, password, cmds)
            print
                    
if __name__ == '__main__':
    main()
    
