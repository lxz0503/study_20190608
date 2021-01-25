#!/usr/bin/env python
# python 3.x support only

import sys, argparse, re
from src.rest_client.http_session import *
from src.xml_tools.xml_element import XMLElement

url = 'http://yow-revo-vcd1.wrs.com/api/session'
vdc = 'https://yow-revo-vcd1.wrs.com/api/vdc/9b3200da-cad5-4d5e-816f-8d593aa50763'
vAppKongLab = 'https://yow-revo-vcd1.wrs.com/api/vApp/vapp-d4a742df-e350-457e-90c1-d6fb971fad1f'

user = 'svc-cmnet'
org = 'wco'

def GetPassword():
    encrypted = 'ddafigcu:9;9-'
    uncrypted = ''
    i = 0
    for x in encrypted:
        y = chr(ord(x) ^ i)
        uncrypted += y
        i += 1
    return uncrypted
    
    
def PowerOnKongLab(session):
    vAppKongLabPowerOn = vAppKongLab + '/power/action/powerOn'
    r = session.post(vAppKongLabPowerOn)
    print(r)
    return(r['status_code'])


def UndeployKongLab(session):
    # use undeploy action instead of poweroff to avoid "partially poweroff" state
    vAppKongLabUndeploy = vAppKongLab + '/action/undeploy'
    undeployRequest = """<?xml version="1.0" encoding="UTF-8"?>
<UndeployVAppParams xmlns="http://www.vmware.com/vcloud/v1.5">
    <UndeployPowerAction>powerOff</UndeployPowerAction>
</UndeployVAppParams>"""
    contentType = 'application/vnd.vmware.vcloud.undeployVAppParams+xml'
    r = session.post(vAppKongLabUndeploy, data=undeployRequest, content_type=contentType)
    print(r)
    return(r['status_code'])    


def GetKongLabStatus(session):
    serviceStatus = None
    statusDict = {'8':'poweroff', 
                  '4':'poweron',
                 }
    r = session.get(vAppKongLab)
    if r['body']:
        found = re.search('(?s)<VApp .*?status=\"(.*?)\".*?\">', r['body'])
        if found:
            serviceStatus = statusDict.get(found.groups()[0], None)
    return serviceStatus


def ListKongLab(session):
    r = session.get(vAppKongLab)
    for k in r:
        print(k)
        print(r[k])
        print('='*10)

    """
    elem = XMLElement(r['body']).find('Link')
    print(dir(elem))
    print(elem.tag)
    print(elem.xmlns)
    print(elem.iter_attrib('rel'))
    print(elem.iter_attrib('href'))
    print(s.post(elem.iter_attrib('href')[0]))
    """
    return r['status_code']
    
    
def CheckReturnCode(returnCode):
    if returnCode in [202, 200]:
        return 0
    else:
        return 1
        
    
def main():
    parser = argparse.ArgumentParser(description='Revo VM Lab Manager')
    parser.add_argument('--poweron', dest='poweron', action='store_true', help='power on Revo Kong Lab')
    parser.add_argument('--poweroff', dest='poweroff', action='store_true', help='power off Revo Kong Lab')
    parser.add_argument('--list', dest='list', action='store_true', help='list Revo Kong Lab')
    parser.add_argument('--status', dest='status', action='store_true', help='get status of Revo Kong Lab')
    o = parser.parse_args()

    if (not o.poweron) and (not o.poweroff) and (not o.list) and (not o.status):
        parser.print_help()
        sys.exit(0)

    pwd = GetPassword()
    s = HTTPSession(url)
    s.login(user, org, pwd)
    
    if o.poweron:
        status = GetKongLabStatus(s) 
        if status == 'poweroff':
            exitCode = CheckReturnCode(PowerOnKongLab(s))
        else:
            print('status=%s is not correct when try to poweron' % status)
            exitCode = 2
            
    elif o.poweroff:
        status = GetKongLabStatus(s) 
        if status == 'poweron':
            exitCode = CheckReturnCode(UndeployKongLab(s))
        else:
            print('status=%s is not correct when try to poweroff' % status)
            exitCode = 2
            
    elif o.list:
        exitCode = CheckReturnCode(ListKongLab(s))
        
    elif o.status:
        print('status=%s' % GetKongLabStatus(s))
        exitCode = 0

    #s.logout()  # logout always gets error
    sys.exit(exitCode)
         
if __name__ == '__main__': main()

