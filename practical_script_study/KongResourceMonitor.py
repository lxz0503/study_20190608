#!/usr/bin/env python
import os
import re
import sys
import time

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
from paramiko import SSHClient

from Mail import SendEmail

from jenkins import Jenkins
from KongConfig import kongJenkins, kongUser, kongPassword

fromEmail = 'kong_resource_monitor@windriver.com'
admins = 'libo.chen@windriver.com;xiaozhan.li@windriver.com;peng.bi@windriver.com;dapeng.zhang@windriver.com;yanyan.liu@windriver.com'

checkSequence = ('Jenkins-master', 'northAmericaVM', 'NAT-server', 'beijingVM', 'build-server',)

resourceToMonitor = { 
                     'beijingVM' : {
                        'kong-vm-tis-100-1'  : '192.168.112.51',
                        'kong-vm-tis-100-2'  : '192.168.112.48',
                        'kong-vm-tis-100-3'  : '192.168.112.49',
                        'kong-vm-tis-100-4'  : '192.168.112.50',
                        'kong-vm-tis-100-5'  : '192.168.112.44',
                        'kong-vm-tis-100-6'  : '192.168.112.15',
                        'kong-vm-tis-100-7'  : '192.168.112.16',
                        'kong-vm-tis-100-8'  : '192.168.112.53',
                        'kong-vm-tis-100-9'  : '192.168.112.18',
                        'kong-vm-tis-100-10' : '192.168.112.19',
                        'kong-vm-tis-100-11' : '192.168.112.45',
                        'kong-vm-tis-100-12' : '192.168.112.46',
                     },
                     
                     'northAmericaVM' : {
                        'kong-rvm-101' : '128.224.186.74',
                        'kong-rvm-102' : '128.224.186.24',
                        'kong-rvm-103' : '128.224.186.155',
                        'kong-rvm-104' : '128.224.186.118',
                        'kong-rvm-105' : '128.224.186.236',
                        'kong-rvm-106' : '128.224.186.156',
                        'kong-rvm-107' : '128.224.186.234',
                        'kong-rvm-108' : '128.224.186.32',
                        'kong-rvm-109' : '128.224.186.240',
                        'kong-rvm-110' : '128.224.186.214',
                        'kong-rvm-111' : '128.224.186.241',
                        'kong-rvm-112' : '128.224.186.249',
                     },
                     
                     'Jenkins-master' : {
                        'Jenkins-master' : '128.224.162.99',
                     },
                     
                     'NAT-server' : {
                        'NAT-server' : '128.224.179.25',
                     },
                     
                     'build-server' : {
                        'pek-vx-nwk1' : '128.224.153.34',
                     },
                     
                     'helix-node' : {
                        'pek-kong-02'   : '128.224.166.245',
                        'pek-kong-03'   : '128.224.166.106',
                        'pek-canoepass' : '128.224.166.229',
                     },
                     }

debugFlag = False # boolean to turn on/off debug log
shcmdIndicator = '===='

def shCmd(cmd, sudo=False):
    if sudo:
        cmd = 'sudo ' + cmd
    if debugFlag:
        print('%s %s' % (shcmdIndicator, cmd))
    return os.popen(cmd).readlines()

def pingOne(target_address, retries=3):
    for _ in range(1, retries):
        if ':' in target_address:
            lines = shCmd('ping6 -c 1 ' + target_address)
        else:
            lines = shCmd('ping -c 1 ' + target_address)
        for line in lines:
            if (('64 bytes from %s:' % target_address) in line or
                ('%s bytes=64' % target_address) in line):
                return True
        time.sleep(0.5)
    return False


def pingOneFromNAT(natNode, target_address, retries=3):
    username = 'root'
    password = 'kernel'
    for _ in range(0, retries):
        try:
            client = SSHClient()
            client.load_system_host_keys()
            client.connect(natNode, username=username, password=password)
            if ':' in target_address:
                _, stdout, stderr = client.exec_command('ping6 -c 1 %s' % target_address)
                lines = stdout.read().decode('utf-8').split('\n')
            else:
                _, stdout, stderr = client.exec_command('ping -c 1 %s' % target_address)
                lines = stdout.read().decode('utf-8').split('\n')
            for line in lines:
                if (('64 bytes from %s:' % target_address) in line or
                    ('%s bytes=64' % target_address) in line):
                    return True
            time.sleep(0.5)
        finally:
            client.close()
    return False 


def isNodeAlive(ipAddr, natNode=''):
    if natNode:
        return pingOneFromNAT(natNode, ipAddr)
    else:
        return pingOne(ipAddr)


def printNode(nodes, message='', output2String=False):
    retStr = ''
    if nodes:
        if message:
            if output2String:
                retStr += '== %s ==\n' % message
            else:
                print('\n== %s ==' % message)
        for node in nodes:
            if output2String:
                retStr += '%s %s\n' % node
            else:
                print('%s %s' % node)
    return retStr


def test_pingOneFromNAT():
    print(pingOneFromNAT('128.224.179.25', '192.168.112.48'))

          
def main_old():
    natServer = '128.224.179.25'
    notAliveNodes = []
    
    for category in checkSequence:
        nodes = resourceToMonitor[category]
        for node in sorted(nodes):
            ipAddr = resourceToMonitor[category][node]
            if category == 'beijingVM':
                natNode = natServer
            else:
                natNode = ''
            pingResult = isNodeAlive(ipAddr, natNode=natNode)
            print('check %s %s : %s' % (node, ipAddr, pingResult))
            if not pingResult:
                notAliveNodes.append( (node, ipAddr) )

    printNode(notAliveNodes, message='Not available nodes')
    
    if notAliveNodes:
        print('\nsend email to Kong admins')
        content = printNode(notAliveNodes, message='Not available nodes', output2String=True)
        SendEmail(fromEmail, admins, 'Found unavailable nodes in Kong infrastructure', content)


def getNodeState(s):
    nodeStates = {}
    nodes = s.get_nodes()
    for x in nodes: 
        nodeStates[x['name']] = x['offline']
    return nodeStates


def getNodeOffline(s, node):
    nodeInfo = s.get_node_info(node)
    return nodeInfo['offline']


def getNodeIp(node):
    for c in resourceToMonitor:
        for n in resourceToMonitor[c]:
            if node == n:
                return resourceToMonitor[c][n]
    raise Exception('ip address of %s not found' % node)
    
def main():
    monitoredNodes = []
    for category in resourceToMonitor:
        monitoredNodes += resourceToMonitor[category]

    s = Jenkins(kongJenkins, kongUser, kongPassword)
    nodeStates = getNodeState(s)
    offlineNodes = [x for x in nodeStates if nodeStates[x]]
    
    offlineMonitoredNodes = sorted(list(set(monitoredNodes).intersection( set(offlineNodes) )))
    offlineMonitoredNodes = [(x, getNodeIp(x)) for x in offlineMonitoredNodes]
    printNode(offlineMonitoredNodes, message='Not available nodes')
    
    if offlineMonitoredNodes:
        print('\nsend email to Kong admins')
        content = printNode(offlineMonitoredNodes, message='Not available nodes', output2String=True)
        SendEmail(fromEmail, admins, 'Found unavailable nodes in Kong infrastructure', content)
    
    
if __name__ == '__main__':
    main()
    #test_pingOneFromNAT()
    
