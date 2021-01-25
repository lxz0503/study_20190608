vmConfig = { 
            'tis-vm':{
                        'kong-vm-tis-100-1' : '11247',
                        'kong-vm-tis-100-2' : '11248',
                        'kong-vm-tis-100-3' : '11249',
                        'kong-vm-tis-100-4' : '11250',
                        'kong-vm-tis-100-5' : '11244',
                        'kong-vm-tis-100-6' : '11215', # once down
                        'kong-vm-tis-100-7' : '11216', # once down
                        'kong-vm-tis-100-8' : '11253', # once down
                        'kong-vm-tis-100-9' : '11218', # once down
                        'kong-vm-tis-100-10' : '11219', # once down
                        'kong-vm-tis-100-11' : '11245',
                        'kong-vm-tis-100-12' : '11246',
                     },
                 
            'revo-vm':{
                        'kong-rvm-101' : '128.224.8.213',
                        'kong-rvm-102' : '128.224.8.168',
                        'kong-rvm-103' : '128.224.8.211',
                        'kong-rvm-104' : '128.224.8.212',
                        'kong-rvm-105' : '128.224.8.215',
                        'kong-rvm-106' : '128.224.8.216',
                        'kong-rvm-107' : '128.224.8.217',
                        'kong-rvm-108' : '128.224.8.218',
                        'kong-rvm-109' : '128.224.8.219',
                        'kong-rvm-110' : '128.224.8.220',
                        'kong-rvm-111' : '128.224.8.221',
                        'kong-rvm-112' : '128.224.8.222',
                      },
            }

bootCmdTpl="""
nova boot \
  --flavor df5b5725-2749-444d-9738-e2465fc928c3 \
  --image 679eeb8a-25df-46cb-8d83-69f8b0da4a2e \
  --nic net-id=0ff4041d-c4c1-4261-8f96-462334de0a34,v4-fixed-ip={ipAddr1} \
  --nic net-id=103321db-c55c-4d04-a616-ac53077ec079,v4-fixed-ip={ipAddr2} \
  --user-data postCreation.sh \
  {vmName}
"""

def port2ip(port):
    return '192.168.' + str(int(port/100)) + '.' + str(port - int(port/100)*100)

def port2internalIp(port):
    return '10.10.0.' + str(port - int(port/100)*100)

for host in sorted(vmConfig['tis-vm']):
    if host not in ('kong-vm-tis-100-4'):
        print 'nova delete %s' % host
        
for host in sorted(vmConfig['tis-vm']):
    if host not in ('kong-vm-tis-100-4'):
        ip1 = port2ip(int(vmConfig['tis-vm'][host]))
        ip2 = port2internalIp(int(vmConfig['tis-vm'][host]))
        print bootCmdTpl.format(vmName=host, ipAddr1=ip1, ipAddr2=ip2)
        
