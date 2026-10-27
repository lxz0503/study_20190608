#############################################################################
#
# Copyright (c) 2006-2018, 2021, 2023 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

#


#This is where logfiles will be stored
logpath = 'log'

#The top path from where the productpaths begin. This is where you have products dirs like "ipnet2-any-r6_0_0"
#This is relative from where you run the script, i.e. <iptestengine>/src/
#You can to change this run-time with  --productroot
productroot = '../..'

#Names of products and where they are relative to the product root.
productpath = {
    'ipepoll': 'epoll', 
    'rtnet': 'rtnet',
    'ipnet': 'ipnet2',
    'ipnat': 'ipnet2/test/nat',
    'ipsvlan': 'ipnet2/test/svlan',
    'ipmpls': 'ipmpls',
    'ipdhcp6': 'dhcpc6',
    'ipmcp': 'ipmcp',
    'ipike': 'ike',
    'ipmip': 'ipmipmn',
    'ipmip6mn': 'ipmip6mn',
    'ipmip6': 'ipmip6',
    'iprohc_uncmp':'rohc/test/uncmp',
    'iprohc_ip':'rohc/test/ip',
    'iprohc_udp': 'rohc/test/udp',
    'iprohc_esp': 'rohc/test/esp',
    'iprohc_tcp': 'rohc/test/tcp',
    'ipuserdb': 'user_management',
    'userauthldap': 'user_management_ldap',
    'ipl2tp': 'l2tp',
    'ipipsec': 'ipsec',
    'ipppp': 'ppp',
    'iptestengine': 'iptestengine',
    'ipdhcps': 'dhcps',
    'ipdhcpr': 'dhcpr',
    'ipradius': 'radius',
    'ipsntp': 'sntp_client',
    'ipntp': 'ntp',
    'ipfirewall': 'firewall',
    'ipappl' : 'ipappl',
    'ipssh' : 'ssh',
    'sshclient' : 'client',
    'ipradius': 'radius',
    'iprip': 'rip',
    'ipripng': 'ripng',
    'ipmcrypto': 'ipmcrypto',
    'ipfreescale': 'ipfreescale',
    'crypto': 'crypto',
    'crypto-fips-140-2': 'crypto',
    'ipccci': 'crypto/test/cci',
    'ipssl': 'ssl',
    'secEvent': 'security_event',
    'send': 'ipnet2/test/send',
    'sanity': 'ipnet2/test/sanity',
    'ipcavium': 'ipcavium',
    'ipsctp': 'ipsctp',
    'vxbridge': 'vxbridge',
    'ipdiameter': 'ipdiameter',
    'ipmacsec': 'ipmacsec',
    'ipftp': 'ftp',
    'iptftp': 'tftp',
    'ipdnsc': 'dnsc',
    'vrrp': 'vrrp',
    'qos': 'qos',
    'snmp': 'snmp',
    'openssl_fips': 'openssl_fips',
    'core_safety': 'core_safety',
    'edoom': 'edoom',
    'supplicant': 'supplicant',
    'socktest': 'socktest',
    'vsomeip': 'vsomeip'
}

misc = {'tftp_root': 'hello',
        }

################################################################################
#                       End of file
################################################################################
