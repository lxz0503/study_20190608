#!/usr/bin/env python3
# coding=utf-8

from IPy import IP

# get total IP address in a subnet
ips = IP('192.168.0.32/30')
print('every subnet has {0} IP address'.format(ips.len()))

# show every ip in a subnet
for ip in ips:
    print(ip)
# subnet ip address
net_ip = ips.strNormal(0)
print('subnet ip address is {0}'.format(net_ip))

# show ip range in this subnet
ip_range = ips.strNormal(3)
print('ip address in this subnet is {0}'.format(ip_range))

# whether one ip belongs to a subnet
if '192.168.0.36' in ips:
    print('True')
else:
    print('False')
#
print('the broadcast ip is {0}'.format(ips.broadcast()))  # 192.168.0.35
print('the netmask is {0}'.format(ips.netmask()))      # 255.255.255.252
print('the net ip is {0}'.format(ips.net()))      # 192.168.0.32
