#!/usr/bin/env python

# ssh to VMs and run commands
#     include both local and remote VMs

import os
import re
import sys
import pxssh
import socket
from multiprocessing import Pool

vmConfig = {
            'revo vms':[
                        '128.224.8.213', #kong-rvm-101
                        '128.224.8.168', #kong-rvm-102
                        '128.224.8.211', #kong-rvm-103
                        '128.224.8.212', #kong-rvm-104
                        '128.224.8.215', #kong-rvm-105
                        '128.224.8.216', #kong-rvm-106
                        '128.224.8.217', #kong-rvm-107
                        '128.224.8.218', #kong-rvm-108
                        '128.224.8.219', #kong-rvm-109
                        '128.224.8.220', #kong-rvm-110
                        '128.224.8.221', #kong-rvm-111
                        '128.224.8.222', #kong-rvm-112
                        ],
                        
            #'pek-cc-pb02l-old.wrs.com':[
            #                            'kong-vm-11',
            #                            'kong-vm-12', # rerun server
            #                           ],

            #'pek-cc-pb01l.wrs.com':[
            #                        'kong-vm-01', # rerun server
            #                        'kong-vm-03',
            #                        'kong-vm-04',
            #                       ],
            
            #'pek-cc-pb02l.wrs.com':[
            #                        'kong-vm-05',
            #                        'kong-vm-06', # rerun server
            #                        'kong-vm-07',
            #                        'kong-vm-08', # rerun server
            #                        'kong-vm-09',
            #                        'kong-vm-10',
            #                       ],
                 
            #'pek-cc-pb05l.wrs.com':[
            #                        'kong-vm-02', # rerun server
            #                      ],
            }

def Log(outputStr):
    print '=== (%s) ' % os.getpid() + outputStr

def SendCmd(node, login, password, cmds):
    """ node as string, app as string, arg as strings """
    try:
        s = pxssh.pxssh()
        #s.force_password = True
        Log('node:%s' % node)
        s.login(node, login, password) # modify pxssh.py and add 2 lines
        for cmd in cmds:
            #Log('cmd:%s' % cmd)
            app = cmd.split(' ')[0]
            arg = ' '.join( cmd.split(' ')[1:] )
            s.sendline('%s %s' % (app, arg))
            s.prompt(timeout=60*30)
            Log(s.before)
        s.logout()
    except pxssh.ExceptionPxssh, e:
        Log('pxssh failed to login %s' % node)
        Log(str(e))
        
def ProcessCmd(cmds):
    login = 'svc-cmnet'
    password = 'december2012!'

    Log('handling vm %s' % cmds[0])
    SendCmd(cmds[0], login, password, cmds[1:])
    Log('\n')
    return '%s done' % os.getpid()

def main():
    workCmds = []

    for server in vmConfig:
        for vm in vmConfig[server]:
            cmds = []
            if server == 'revo vms':
                vmName = vm
            if server.startswith('pek-cc-'):
                vmName = vm + '.corp.ad.wrs.com'
                
            cmds.append(vmName)
            #cmds.append('cd /home/svc-cmnet')
            #cmds.append('sudo rm -fr /home/svc-cmnet/vxworks') # has to use sudo
            #cmds.append('git clone http://svc-cmnet@stash.wrs.com/scm/vx7/vxworks vxworks')
            
            #cmds.append('cd /home/svc-cmnet/vxworks')
            #cmds.append('git checkout vx7-net')
            #cmds.append('git pull')            
            #cmds.append('./setup-tools -clean')
            #cmds.append('./setup-tools')
            
            cmds.append('sudo apt-get install putty-tools')
                        
            workCmds.append(cmds)

    workers = Pool(processes=1)

    results = workers.map(ProcessCmd, workCmds)

if __name__ == '__main__':
    main()
    
