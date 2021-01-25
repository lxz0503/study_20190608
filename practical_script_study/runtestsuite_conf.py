#############################################################################
#
# Copyright (c) 2006-2014, 2017-2019 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

#
#modification history
#--------------------
#02aug19,clb remove -DIPCOM_USE_SHELL=IPCOM_SHELL_IPCOM and USE_IPCOM_SHELL
#24may19,mze layer renaming as required for SR0620
#03dec18,rjq Add IPv6 support in RTNET socktest. (F10020)
#13nov18,wfl add telnet client component in IPNET for V7NET-1699 RCA.
#05nov18,ply Add kongtest case for rmd(F11069)
#04sep18,jxy Replace OPENSSL with OPENSSL_CRYPTO due to merge the two layers OPENSSL and HASH
#            into one (V7SEC-682)
#20aug18,lan add test case for ipnet supporting core safety. (F9305)
#15aug18,rjq add new vxparam INET6_DISCARD_UDP_WITH_ZERO_CHECKSUM for IPNET. (V7NET-1721)
#17jul18,ply add test case for V7NET-1609. (F11069)
#11jul18,lan add OPENSSL_FIPS KONG test support. (F10643)
#06jul18,lan support to add files to VIP. (V7NET-1686)
#08mar18,rjq add SNMP KONG test support. (F9305)
#05mar18,clb add to support SNMP
#28dec17,jxy add the layers OPENSSL and SEC_CRYPTO for ipcrytpto-fips-14002 (V7TST-953)
#21dec17,ply add test case for user_management_ldap.(F9804)
#24oct17,clb add rtnet module
#18sep17,ply add test case for user_management.(V7SEC-490)
#05sep17,rjq restore ROHC_UDP test cases. (US102054)
#10aug17,ljl add another uml/generic in SSHCLIENT
#03aug17,ljl add SEC_EVENT_HANDLER in vxprj list of SECEVENT module.(V7SEC-447)
#14jul17,l_y fix lost_delete_notification2 case failed.(V7SEC-316)
#06jul17,rjq Add new test case for IPSNTP server. (US100022)
#06jul17,ply add some vip component for ipsec.(US100135)
#27jun17,ljl add secEvent module. (F9305)
#26may17,ply add ssh client module.(US98163)
#29jul14,h_s Adapt for chap support. (US40661)
#23jul14,chm Move QOS. (US36943)
#10jul14,rjq Move vrrp. (US36942)
#20may14,h_s remove the IPCOM_USE_SHELL related configuration for CRYPTO 
#            test suite due to the removal of ipxinc in vx7.
#            correct SSH configuration error including ipcrypto, enable USER_MANAGEMENT.
#            correct ROHC configuration error, V7NET-343. 
#29apr14,h_s adapt test script for vx7, US35892.
#

# search path is the relative path to vxworks-7/pkgs_v2
testable_packages_search_paths = ['/net/ipnet',
                                  '/security', 
                                  '/net/rtnet',
                                  '/app',
                                 ]

testable_packages = {
    # Vx7 applicable below
    'RTNET_RTP' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'extra_build_user_cflags' : ['-DRTNET_SOCKTEST'],
        'extensions'         : [],
        'testengine_name'    : ['rtnet.command_rtp'],
        'vc'                 : ['rtnet'],
        # vsb layers
        'vxconf'             : ['RTNET', 'RTNET_RTP'],
        'vxmake'             : [],
        # vip components
        'vxprj'              : ['ROMFS',  'SHELL',  'SHELL_INTERP_CMD',  'RTP_SHELL_C',  'RTP_SHOW_SHELL_CMD',  'DISK_UTIL_SHELL_CMD',  'ENV_VARS',  'VXBUS_SHOW'],
        'vxprj_remove'       : ['NETWORK'],
        'vxparam'            : [],
        'vxfile'             : [],
        'vx_extra_define'    : [],
        'rtpvxe'             : ['/usr/root/llvm/bin/netshell.vxe', ],
        'jsonfile'           : ['/net/rtnet/test/rtnet/test/28525rtp.json',
                                '/net/rtnet/test/rtnet/test/28526rtp.json',
                                '/net/rtnet/test/rtnet/test/25002rtp.json',
                                '/net/rtnet/test/rtnet/test/25003rtp.json',
                               ]
        
    },
    'RTNET' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : ['-DRTNET_SOCKTEST'],
        'extensions'         : [],
        'testengine_name'    : ['rtnet'],
        'vc'                 : ['rtnet'],
        # vsb layers
        'vxconf'             : ['RTNET', 'UTILS_JANSSON'],
        'vxmake'             : [],
        # vip components
        'vxprj'              : ['ROMFS', 'RTNET', 'RTNET_DEMO', 'RTNET_FIB_SHOW', 'RTNET_IPV6_SUPPORT', 'RTNET_IP_SHOW', 'RTNET_LINK_SHOW', 'RTNET_LINK_SHOW', 'RTNET_MUX', 'RTNET_NEIGH_SHOW', 'RTNET_PING', 'RTNET_SOCK_SHOW', 'SHELL', 'SHELL_INTERP_CMD', 'STANDALONE_DTB'],
        'vxprj_remove'       : ['IPNET'],
        'vxparam'            : [""" RTNET_JSON_FILE='"/romfs/conf.json"'"""],
        'vxfile'             : ['/net/rtnet/test/socktest/tmain.c', '/net/rtnet/test/sock6test/tmain6.c'],
        'vx_extra_define'    : ['-DRTNET_SOCKTEST'],
        'jsonfile'           : ['/net/rtnet/test/rtnet/test/conf.json',
                                '/net/rtnet/test/rtnet/test/22478.json',
                                '/net/rtnet/test/rtnet/test/22479.json',
                                '/net/rtnet/test/rtnet/test/25002.json',
                                '/net/rtnet/test/rtnet/test/25003.json',
                                '/net/rtnet/test/rtnet/test/28525.json',
                                '/net/rtnet/test/rtnet/test/28526.json',
                               ]
        
    },
    'SNMP' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : ['-DIPCOM_ZEROCOPY=1', '-DIPCOM_CMD_SOCKTEST_USE_ZEROCOPY_API'],
        'testengine_name'    : ['snmp'],
        'vc'                 : ['ipnet2', 'snmp', 'ssh', 'ipcrypto'],
        'vxconf'             : ['IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SNMP', 'FEATURE_SNMP_V3', 'SNMP_USE_SEC_KEY_DB', 'SNMP_USE_SSH_TRANSPORT', 'SNMP_USE_TLS_DTLS_TRANSPORT', 'IPNET_SSH', 'USER_MANAGEMENT', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"123456"'""", """ SNMP_TLS_KEY_ID='"snmpserver"'""", """ SNMP_TLS_KEY_FILE='"/ram/snmpserver.pem"'""", """ SNMP_TLS_CERT_FILE='"/ram/snmpserver.pem"'""", """ SNMP_TLS_CA_CERT_FILE='"/ram/root.pem"'""",  """ SNMP_TLS_CERT_SECNAME='"certSecName 10 4D:63:20:91:B2:CD:0A:B1:59:72:1A:F7:C8:56:A3:FC:09:F3:E1:65 --sn client.wrs.com"'"""],
        'vxprj'              : ['SNMP_MANAGER', 'SNMP_PRIVACY', 'WINDMANAGE_SNMP_CORE', 'SNMP_TLS_TRANSPORT', 'SNMP_DTLS_TRANSPORT', 'SNMP_SSH_TRANSPORT', 'IPCRYPTO', 'CCI_IMPORT_BLOWFISH', 'IPFTP_CMD', 'IPFTPS', 'SSH', 'IPCOM_KEY_DB_CMD', 'IPCOM_USE_KEY_DB', 'IPCRYPTO_USE_KEY_DB_EXAMPLE_KEYS', 'SECURITY', 'USER_MGT_SHELL_CMD', 'IPTFTP_CLIENT_CMD']
    },
    'EDOOM': {
        'capable'            : {
           'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'testengine_name'    : ['edoom'],
        'vc'                 : ['ipnet2', 'edoom'],
        'vxconf'             : ['RTP'],
        'vxmake'             : [],
        'vxparam'            : [],
        'vxprj'              : ['RAM_DISK', 'RAM_DISK_FORMAT_ANY'],
        'vxfile'            : ['/net/ipnet/coreip/src/ipnet2/test/edoom/test/rtpMain.c'],        
        'rtpfile'            : ['/net/ipnet/coreip/src/ipnet2/test/edoom/test/rtpMain.c'],
        'rtplib'             : ['-lnet']
    },     
    'CORE_SAFETY': {
        'capable'            : {
           'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'testengine_name'    : ['core_safety'],
        'vc'                 : ['ipnet2', 'core_safety'],
        'vxconf'             : ['CORE_SAFETY', 'RTP'],
        'vxmake'             : [],
        'vxparam'            : [],
        'vxprj'              : ['RTP_PARTITIONS_SHOW', 'TIME_PART_SCHEDULER', 'RESOURCE_ALLOC_CTRL_SHOW', 'RAM_DISK', 'RAM_DISK_FORMAT_ANY'],
        'vxfile'             : ['/net/ipnet/coreip/src/ipnet2/test/core_safety/test/udpClient.c', '/net/ipnet/coreip/src/ipnet2/test/core_safety/test/udpServer.c', '/net/ipnet/coreip/src/ipnet2/test/core_safety/test/rtpStart.c'],
        'rtpfile'            : ['/net/ipnet/coreip/src/ipnet2/test/core_safety/test/udpClient.c', '/net/ipnet/coreip/src/ipnet2/test/core_safety/test/udpServer.c', '/net/ipnet/coreip/src/ipnet2/test/core_safety/test/rtpMain.c'],
        'rtplib'             : ['-lnet']
    },       
    'IPNET' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : ['-DIPCOM_ZEROCOPY=1', '-DIPCOM_CMD_SOCKTEST_USE_ZEROCOPY_API'],
        'testengine_name'    : ['ipnet'],
        'vc'                 : ['ipnet2'],
        'vxconf'             : ['IPNET_QOS','IPNET_DIFFSERV'],
        'vxmake'             : ['VIRTUAL_ROUTER'],
        'vxprj'              : ['IPQOS_CMD','IPQUEUE_CONFIG_CMD','IPPING_CMD','IPPING6_CMD','TELNET_CLIENT', 'IPNETSTAT_CMD'],
        'vxparam'            : [""" INET6_DISCARD_UDP_WITH_ZERO_CHECKSUM='"0"'""", """ SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""]        
    },
    'VRRP' : {
        'capable'            : {
            'vxworks' : {},
        },
        'extra_build_cflags' : [],
        'testengine_name'    : ['vrrp'],
        'vc'                 : ['ipnet2', 'vrrp'],
        'vxconf'             : ['IPNET_VRRP','IPNET_QOS','IPNET_DIFFSERV'],
        'vxmake'             : ['VIRTUAL_ROUTER', 'VRRP'],
        'vxprj'              : ['IPVRRPD', 'IPQOS_CMD','IPQUEUE_CONFIG_CMD']
    },
    'SCTP' : {
        'capable'            : {
            'vxworks' : {},
        },
        'extra_build_cflags' : [],
        'testengine_name'    : ['ipsctp'],
        'vc'                 : ['ipnet2', 'ipsctp'],
        'vxconf'             : ['IPNET_QOS'],
        'vxmake'             : ['IPSCTP'],
        'vxprj'              : ['IPSYSCTL_CMD', 'IPSCTP', 'IPTCP_TEST_CMD', 'IPQUEUE_CONFIG_CMD']
    },
    'MCP' : {
        'capable'            : {
            'vxworks' : {},
        },
        'extra_build_cflags' : [],
        'testengine_name'    : ['ipmcp'],
        'vc'                 : ['ipnet2', 'ipmcp'],
        'vxmake'             : ['VIRTUAL_ROUTER', 'IPMCP'],
        'vxprj'              : ['IPMCAST_PROXY_CMD', 'IPMCP', 'IPMCP_USE_IGMP', 'IPMCP_USE_MLD', ]
    },
    'NAT' : {
        'capable'            : {
            'vxworks' : {},
        },
        'extra_build_cflags' : ['-DIPFTPS_USE_TEST', ],
        'extensions'         : ['uml/generic', 'uml/generic', 'uml/generic'],
        'testengine_name'    : ['ipnat'],
        'vc'                 : ['ipnet2'],
        'vxprj'              : ['IPFTP_CMD', 'IPFTPS', 'IPNAT_CMD', ],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""]
    },
    'FTP' : {
        'capable'            : {
            'vxworks' : {},
        },
        'extra_build_cflags' : ['-DIPFTPS_USE_TEST', ],
        'testengine_name'    : ['ipftp'],
        'vc'                 : ['ipnet2', 'ftp'],
        'vxconf'             : ['USER_MANAGEMENT', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO'],
        'vxprj'              : ['IPFTP_CMD', 'IPFTPS', 'USER_DATABASE', 'SECURITY', 'IPCOM_USE_KEY_DB', 'IPCOM_KEY_DB_CMD','LOGIN_BANNER'],
        'vxparam'            : [""" LOGIN_BANNER_TEXT='"Login Banner #1"'""",""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
    },
    'TFTP' : {
        'capable'            : {
            'vxworks' : {},
        },
        'extensions'         : ['uml/generic'],
        'extra_build_cflags' : [], # replace -DIPCOM_USE_SHELL=IPCOM_SHELL_IPCOM to null
        'testengine_name'    : ['iptftp'],
        'vc'                 : ['ipnet2', 'tftp'],
        'vxprj'              : ['IPTFTP_CLIENT_CMD', 'IPTFTPS', ] # remove USE_IPCOM_SHELL
    },
    'DNSC' : {
        'capable'            : {
            'vxworks' : {},
        },
        'extensions'         : ['uml/generic'],
        'extra_build_cflags' : [],
        'testengine_name'    : ['ipdnsc'],
        'vc'                 : ['ipnet2', 'dnsc'],
        'vxprj'              : ['IPNSLOOKUP_CMD', ]
    },
    'DHCP' : {
        'capable'            : {
            'vxworks' : {},
        },
        'permutations'       : 1, # ???
        'extra_build_cflags' : [],
        'testengine_name'    : ['ipdhcpr', 'ipdhcps'],
        'vc'                 : ['ipnet2', 'dhcpr', 'dhcps'],
        'vxconf'             : ['IPNET_DHCP_RELAY', 'IPNET_DHCP_SERVER'],
        'vxprj'              : ['IPDHCPC', 'IPDHCPR', 'IPDHCPS', ],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""]
    },
    'DHCP6' : {
        'capable'            : {
            'vxworks' : {},
        },
        'extensions'         : ['uml/generic'],
        'extra_build_cflags' : [],
        'permutations'       : 1, # ???
        'testengine_name'    : ['ipdhcp6.assign', 'ipdhcp6.relay', 'ipdhcp6.rtadv', 'ipdhcp6.auth'],
        'vc'                 : ['ipnet2', 'dhcpc6'],
        'vxmake'             : ['VIRTUAL_ROUTER'],
        'vxconf'             : ['IPNET_DHCP_CLIENT6', 'IPNET_DHCP_SERVER6'],
        'vxprj'              : ['IPDHCPC6', 'IPDHCPS6', 'IPDHCPC6_CMD', 'IPDHCPS6_CMD', 'IPNSLOOKUP_CMD']
    },
    'SNTP_CLIENT' : {
        'capable'            : {
            'vxworks' : {},
        },
        'extensions'         : ['uml/generic'],
        'extra_build_cflags' : [],
        'testengine_name'    : ['ipsntp.api.broadcast', 'ipsntp.api.unicast', 'ipsntp.client'],
        'vc'                 : ['ipnet2', 'sntp'],
        'vxprj'              : ['IPSNTP_CMD', 'IPSNTPC', ],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""]
    },
    'SNTP_SERVER' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extensions'         : ['uml/generic'],
        'extra_build_cflags' : ['-DIPSNTP_USE_SERVER', ],
        'testengine_name'    : ['ipsntp.api', 'ipsntp.server'],
        'vc'                 : ['ipnet2', 'sntp', 'ipappl'],
        'vxprj'              : ['IPSNTP_CMD', 'IPSNTPS', 'IPTFTP_CLIENT_CMD', 'IPTFTPS'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'depend'             : ['SNTP_CLIENT']
    },
    'NTP' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extensions'         : ['uml/generic'],
        'extra_build_cflags' : ['-DIPNTP_USE_TEST', ],
        'testengine_name'    : ['ipntp'],
        'vc'                 : ['ipnet2', 'ntp'],
        'vxconf'             : ['IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'IPNTP_USE_SSL', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IPNTP_CMD', 'IPNTP', 'IPTFTP_CLIENT_CMD', 'IPCRYPTO', 'IPCOM_SYSLOGD_CMD', 'IPCOM_SYSVAR_CMD', 'IPNETSTAT_CMD']
    },
    'PPP' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : ['-DIPPPP_TESTENGINE', '-DIPPPP_USE_PPPMP', '-DIPPPP_USE_VJCOMP', ],
        'testengine_name'    : ['ipppp.pppoe', 'ipppp.pppmp'],
        'vc'                 : ['ipnet2', 'ppp'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxconf'             : ['USER_MANAGEMENT', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'IPPPP_MP', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxprj'              : ['IPPPPOE', 'IPPPP_CMD', 'USER_DATABASE', 'SECURITY', 'IPCOM_USE_KEY_DB', 'IPCOM_KEY_DB_CMD']
    },
    'SYSVIEW' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : ['-DIPCOM_WV_INSTRUMENTATION_TEST', '-DIPNET_STATISTICS', '-DIPFTPS_USE_TEST', ],
        'testengine_name'    : ['ipnet.windview'],
        'vc'                 : ['ipnet2'],
        'vxprj'              : ['IPFTPS', 'WINDVIEW', 'WINDVIEW_CLASS', 'WVNETD', 'WVUPLOAD_FILE', 'WVUPLOAD_SOCK', ]
    },

    # The following is for MSP profile.
    'RIP': {
        'capable'            : {
            'vxworks' : {}
        },
        'permutations'       : 1,
        'extra_build_cflags' : [],
        'testengine_name'    : ['iprip'],
        'vc'                 : ['ipnet2', 'rip', 'iptcp'],
        'vxconf'             : ['IPNET_ROUTEPROTO', 'IPNET_RIP'],
        'vxprj'              : ['IPRIP_CTRL_CMD', 'IPRIP_IFCONFIG_1', ]
    },
    'RIPNG': {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : ['-DINCLUDE_RIPNG_CTRL_CMD'],
        'networks'           : 1,
        'permutations'       : 3,
        'testengine_name'    : ['ipripng'],
        'vc'                 : ['ipnet2', 'ripng', 'iptcp'],
        'vxconf'             : ['IPNET_ROUTEPROTO', 'IPNET_RIPNG'],
        'vxprj'              : ['RIPNG_CTRL_CMD', ]
    },
    'CRYPTO' : {
        'capable'            : {
           'vxworks' : {}
        },
        'permutations'       : 1,
        'testengine_name'    : ['ipcrypto'],
        'vc'                 : ['ipcrypto', 'ipnet2', 'iptcp'],
        'vxconf'             : ['IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : ['SHELL_TASK_PRIORITY=60',
                                """ SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IPCRYPTO', 'IPCRYPTO_USE_CMDS', 'SEC_HASH_RMD', 'IPCRYPTO_USE_TEST_CMDS', 'IPFTP_CMD', 'IPFTPS', 'IPCOM_USE_KEY_DB', 'IPCRYPTO_USE_KEY_DB_EXAMPLE_KEYS', 'IPCOM_KEY_DB_CMD'],
    },
    'CRYPTO-FIPS-140-2' : {
        'capable'            : {
           'vxworks' : {}
        },
	'extra_build_cflags' : [],
        'permutations'       : 1,
        'testengine_name'    : ['ipcrypto-fips-140-2'],
        'vc'                 : ['ipcrypto', 'ipnet2'],
        'vxconf'             : ['OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxmake'             : ['IPCRYPTO_USE_FIPS_140_2'],
        'vxparam'            : ['SHELL_TASK_PRIORITY=60',
                                """ SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IPCRYPTO', 'IPCRYPTO_USE_CMDS', 'IPCRYPTO_USE_TEST_CMDS', 'IPFTP_CMD', 'IPFTPS', 'IPCOM_USE_KEY_DB', 'IPCRYPTO_USE_KEY_DB_EXAMPLE_KEYS', 'IPCOM_KEY_DB_CMD', ],
        'extra_build_opt'    : ['IPCRYPTO_USE_FIPS=yes']
    },
    'IKE' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'permutations'       : 1,
        'testengine_name'    : ['ipike.auto'],
        'vc'                 : ['ike', 'ipsec', 'ipnet2'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO','IPNET_QOS', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IPCRYPTO', 'IPFTPS', 'INTERNET_KEY_EXCHANGE', 'IPNAT_CMD', 'IPNET_USE_NAT', 'IPCOM_KEY_DB_CMD', 'IPCOM_USE_KEY_DB', 'IPSECCTRL_CMD', 'KEYADM_CMD', 'IPQOS_CMD','IPQUEUE_CONFIG_CMD'],
    },
    'IKE-ALGORITHMS' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'permutations'       : 2,
        'testengine_name'    : ['ipike.algorithms'],
        'vc'                 : ['ike', 'ipsec', 'ipnet2'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE','IPNET_IKE', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IPCRYPTO', 'IPFTPS', 'INTERNET_KEY_EXCHANGE', 'IPSECCTRL_CMD', 'KEYADM_CMD',]
    },
    'IKE-AUTHENTICATION' : {
        'capable'            : {
            'vxworks' : {}
        },
        #'extra_build_cflags' : [],
        'extensions'         : ['uml/generic'],
        'permutations'       : 2,
        'testengine_name'    : ['ipike.authentication'],
        'vc'                 : ['ike', 'ipsec', 'ipnet2'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IPCRYPTO', 'IPFTPS', 'INTERNET_KEY_EXCHANGE', 'IPSECCTRL_CMD', 'KEYADM_CMD', 'IPCOM_KEY_DB_CMD', 'IPCOM_USE_KEY_DB']
    },
    'IKE-BASIC' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'permutations'       : 2,
        'testengine_name'    : ['ipike.basic'],
        'vc'                 : ['ike', 'ipsec', 'ipnet2'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO', 'IPNET_QOS', 'IPNET_DIFFSERV'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IPCRYPTO', 'IPFTPS', 'INTERNET_KEY_EXCHANGE', 'IPSECCTRL_CMD', 'KEYADM_CMD', 'IPQUEUE_CONFIG_CMD', 'IPQOS_CMD']
    },
    'IKE-ADVANCED' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'permutations'       : 2,
        'testengine_name'    : ['ipike.advanced'],
        'vc'                 : ['ike', 'ipsec', 'ipnet2'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IPCRYPTO', 'IPFTPS', 'INTERNET_KEY_EXCHANGE', 'IPSECCTRL_CMD', 'KEYADM_CMD', 'IPNET_USE_NAT', 'IPNAT_CMD', ]
    },
    'IKE-DAEMON' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : ['-D_WRS_CONFIG_COMPONENT_IPIKE_USE_EVENT_LOG', '-DIPIKE_USE_EVENT_LOG_TEST'],
        'extensions'         : ['uml/generic'],
        'permutations'       : 2,
        'testengine_name'    : ['ipike.daemon'],
        'vc'                 : ['ike', 'ipsec', 'ipnet2'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IPCRYPTO', 'IPFTPS', 'INTERNET_KEY_EXCHANGE', 'IPSSL', 'IPSECCTRL_CMD', 'KEYADM_CMD']
    },
    'IKE-ROHC-IPSEC' : {
        'capable'            : {
            'vxworks' : {}
        },
        'permutations'       : 2,
        'extra_build_cflags' : [],
        'testengine_name'    : ['ipike.rohc_ipsec2'],
        'vc'                 : ['ike', 'ipsec', 'ipnet2'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'IPNET_ROHC', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IPCRYPTO', 'IPFTPS', 'INTERNET_KEY_EXCHANGE', 'IPSECCTRL_CMD', 'KEYADM_CMD','IPROHC', 'IPROHC_CMD', 'IPROHC_PROFILE_UNCOMPRESSED', 'IPROHC_PROFILE_IP','IPROHC_PROFILE_UDP_IP', 'IPROHC_PROFILE_ESP_IP', 'IPROHC_PROFILE_TCP_IP', 'IPCOM_USE_KEY_DB', 'IPCOM_KEY_DB_CMD']
    },
    'IKE-SETTINGS' : {
        'capable'            : {
            'vxworks' : {}
        },
        'permutations'       : 2,
        'extra_build_cflags' : [],
        'testengine_name'    : ['ipike.settings'],
        'vc'                 : ['ike', 'ipsec', 'ipnet2'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],	
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IPCRYPTO', 'IPFTPS', 'INTERNET_KEY_EXCHANGE', 'IPSECCTRL_CMD', 'KEYADM_CMD']
    },
    'IKE-IPEAP' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extensions'         : ['uml/generic'],
        #'extra_build_cflags' : ['-DIPEAP_SIM_ENABLE_TEST', '-DIPEAP_USE_EAP_SIM','-DIPEAP_AKA_ENABLE_TEST','-DIPEAP_USE_EAP_AKA','-DIPEAP_TEST_FOR_PENDING_USER_INPUT'],
        'extra_build_cflags' : ['-DIPEAP_TEST_FOR_PENDING_USER_INPUT'],
        'permutations'       : 2,
        'testengine_name'    : ['ipike.eap'],
        'vc'                 : ['ike', 'ipsec', 'ipnet2'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'IPNET_AAA', 'IPNET_SSL', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'IPNET_EAP', 'IPEAP_USE_EAP_AKA', 'IPEAP_USE_EAP_SIM', 'IPEAP_AKA_ENABLE_TEST', 'IPEAP_SIM_ENABLE_TEST', 'IPEAP_USE_EAP_TLS', 'IPEAP_USE_EAP_PEAP', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['INTERNET_KEY_EXCHANGE', 'IPCRYPTO', 'IPEAP', 'IPEAP_PRIVACY', 'IPEAP_USE_EAP_MD5', 'IPEAP_USE_EAP_SIM', 'IPEAP_USE_EAP_AKA','IPEAP_USE_EAP_TLS', 'IPEAP_USE_EAP_TTLS', 'IPFTPS', 'IPRADIUS', 'IPSSL', 'IPNET_USE_NAT', 'IPNAT_CMD', 'IPCOM_KEY_DB_CMD', 'IPCOM_USE_KEY_DB', 'IPSECCTRL_CMD', 'KEYADM_CMD']
    },
    'IKE-RACOON' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extensions'         : ['uml/generic'],
        'extra_build_cflags' : [],
        'permutations'       : 1,
        'testengine_name'    : ['ipike.racoon'],
        'vc'                 : ['ike', 'ipsec', 'ipnet2'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],	
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['INTERNET_KEY_EXCHANGE', 'IPCRYPTO', 'IPFTPS', 'IPSECCTRL_CMD', 'KEYADM_CMD', 'IPCOM_KEY_DB_CMD', 'IPNET_USE_NAT', 'IPNAT_CMD']
    },
    'IPSEC-IPCRYPTO' : {
        'capable'            : {
            'vxworks' : {}
        },
        #'extra_build_cflags' : [],
        'permutations'       : 1,
        'testengine_name'    : ['ipipsec'],
        'vc'                 : ['ipsec', 'ipnet2'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IPCRYPTO', 'IPSECCTRL_CMD', 'KEYADM_CMD', 'IPCOM_KEY_DB_CMD', 'IPNAT_CMD']
    },
    'IPNET-IPSEC' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'permutations'       : 1,
        'testengine_name'    : ['ipnet.ipsec'],
        'vc'                 : ['ipsec', 'ipnet2'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IP_SECURITY', 'IPSYSCTL_CMD', 'KEYADM_CMD']
    },
    'RADIUS' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'extensions'         : ['uml/generic'],
        'permutations'       : 1,
        'testengine_name'    : ['ipradius'],
        'vc'                 : ['ipnet2', 'radius'],
        'vxconf'             : ['IPNET_AAA'],	
        'vxprj'              : ['IPRADIUS', 'IPRADIUS_CMD', ]
    },
    'ROHC_UNCMP' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'extensions'         : ['uml/generic', 'uml/generic'],
        'loop'               : True,
        'permutations'       : 4,
        'testengine_name'    : ['iprohc_uncmp'],
        'use_extdev'         : True,
        'vc'                 : ['ipnet2', 'rohc', 'ppp'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxconf'             : ['IPNET_ROHC', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],		
        'vxprj'              : ['IPROHC', 'IPROHC_CMD', 'IPTFTPC', 'IPROHC_PROFILE_UNCOMPRESSED', 'IPTFTPS', 'IPTFTP_CLIENT_C', 'IPTFTP_COMMON', 'IPTELNETS', 'IPCOM_SHELL_CMD', 'IPPPPOE','IPPPP_CMD', 'IPCOM_USE_KEY_DB', 'IPCOM_KEY_DB_CMD']
    },
    'ROHC_IP' : {
        'capable'            : {
            'las'     : {},
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'extensions'         : ['uml/generic', 'uml/generic'],
        'loop'               : True,
#        'extra_build_cflags' : ['-DPPPOE_MAX_ETH_SESSIONS="30"','-DINET6_RTHDR0=\\"enable\\"'],
        'permutations'       : 4,
        'testengine_name'    : ['iprohc_ip'],
        'use_extdev'         : True,
        'vc'                 : ['ipnet2', 'rohc', 'ppp'],
        'vxconf'             : ['IPNET_ROHC', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxprj'              : ['IPROHC', 'IPROHC_CMD', 'IPROHC_PROFILE_IP', 'IPROHC_PROFILE_UDP_IP', 'IPTFTPC', 'IPTFTPS', 'IPTFTP_CLIENT_C', 'IPTFTP_COMMON', 'IPTELNETS', 'IPCOM_SHELL_CMD', 'IPPPPOE','IPPPP_CMD', 'IPCOM_USE_KEY_DB', 'IPCOM_KEY_DB_CMD'],
        'vxparam'            : [""" INET6_RTHDR0='"enable"'""", """ SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""]
    },
    'ROHC_UDP' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extensions'         : ['uml/generic', 'uml/generic'],
        'extra_build_cflags' : [],
        'loop'               : True,
        'permutations'       : 4,
        'testengine_name'    : ['iprohc_udp'],
        'use_extdev'         : True,
        'vc'                 : ['ipnet2', 'rohc', 'ppp'],
        'vxconf'             : ['IPNET_ROHC', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],	
        'vxprj'              : ['IPROHC', 'IPROHC_CMD', 'IPROHC_PROFILE_UDP_IP', 'IPROHC_PROFILE_UNCOMPRESSED', 'IPROHC_PROFILE_IP','IPTFTPC', 'IPTFTPS', 'IPTFTP_CLIENT_C', 'IPTFTP_COMMON', 'IPTELNETS', 'IPCOM_SHELL_CMD',  'IPPPPOE','IPPPP_CMD', 'IPCOM_USE_KEY_DB', 'IPCOM_KEY_DB_CMD'],
        'vxparam'            : [""" INET6_RTHDR0='"enable"'"""]
    },
    'ROHC_ESP' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'extensions'         : ['uml/generic', 'uml/generic'],
        'loop'               : True,
        'permutations'       : 4,
        'testengine_name'    : ['iprohc_esp'],
        'use_extdev'         : True,
        'vc'                 : ['ipnet2', 'rohc', 'ppp'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'IPNET_ROHC', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],	
        'vxprj'              : ['IPROHC', 'IPROHC_CMD', 'IPROHC_PROFILE_ESP_IP',  'IPIPSEC', 'IPCRYPTO', 'IPTFTPC', 'IPTFTPS', 'IPTFTP_CLIENT_C', 'IPTFTP_COMMON', 'IPTELNETS', 'IPCOM_SHELL_CMD', 'IPPPPOE','IPPPP_CMD', 'KEYADM_CMD', 'IPCOM_USE_KEY_DB', 'IPCOM_KEY_DB_CMD']
    },
    'ROHC_TCP' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extensions'         : ['uml/generic', 'uml/generic'],
        'loop'               : True,
        'extra_build_cflags' : ['-DIPROHC_USE_TEST', '-DIPROHC_TCP_IP_SIMULATED_IPID'],
        'permutations'       : 4,
        'testengine_name'    : ['iprohc_tcp'],
        'use_extdev'         : True,
        'vc'                 : ['ipnet2', 'rohc', 'ppp'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'IPNET_ROHC', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxprj'              : ['IPROHC', 'IPROHC_CMD', 'IPROHC_PROFILE_TCP_IP', 'IPROHC_PROFILE_UDP_IP',  'IPROHC_PROFILE_IP',  'IPROHC_PROFILE_UNCMP', 'IPTFTP_CLIENT_C', 'IPTFTP_COMMON', 'IPTELNETS', 'IPCOM_SHELL_CMD', 'IPPPPOE', 'IPPPP_CMD', 'IPCOM_USE_KEY_DB', 'IPCOM_KEY_DB_CMD'],
        'vxparam'            : [""" INET6_RTHDR0='"enable"'""", """ SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""]
    },
    'USERDB' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        #'extensions'         : ['uml/generic', 'uml/generic'],
        'loop'               : True,
        'permutations'       : 4,
        'testengine_name'    : ['ipuserdb'],
        'use_extdev'         : True,
        'vc'                 : ['ipnet2', 'ipcom', 'user_management'],
        'vxconf'             : ['USER_MANAGEMENT', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxmake'             : [''],
        'vxprj'              : ['IPCRYPTO', 'USER_CMD', 'IPTELNETS', 'IPCOM_SHELL_CMD', 'IPFTPS', 'IPFTPC', 'IPFTP_CMD', 'IPCOM_KEY_DB_CMD', 'IPCOM_USE_KEY_DB', 'USER_MGT_SHELL_CMD'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'overrided_usrAppInit' : '/security/user_management/test/usrAppInit.c'
    },
    'USERAUTH_LDAP' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'testengine_name'    : ['userauthldap'],
        'vc'                 : ['ipnet2', 'ipcrypto', 'user_management', 'user_management_ldap'],
        'vxconf'             : ['USER_MANAGEMENT' ,'USER_MANAGEMENT_LDAP', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO', 'LDAPC'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['AD_LDAP_AUTH', 'AD_LDAP_AUTH_CMD', 'AUTH_CACHE_USER', 'IPCOM_KEY_DB_CMD', 'IPCOM_USE_KEY_DB', 'IPCRYPTO_USE_KEY_DB_EXAMPLE_KEYS', 'SECURITY', 'IPCRYPTO_USE_TEST_CMDS', 'IPTCP_TEST_CMD', 'STANDALONE_SYM_TBL', 'USER_MGT_SHELL_CMD'],
        'config_file'           : '/security/user_management/user_management_ldap/test/ldap_test.conf'
    },
    'SECEVENT' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'testengine_name'    : ['secEvent'],
        'vc'                 : ['ipnet2', 'ssh', 'ipcrypto', 'security_event'],
        'vxconf'             : ['SECURITY_EVENT', 'IPNET_SSH', 'USER_MANAGEMENT', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['SEC_EVENT_HANDLER', 'CCI_IMPORT_BLOWFISH', 'IPFTP_CMD', 'IPFTPS', 'SSH', 'IPCOM_KEY_DB_CMD', 'IPCOM_USE_KEY_DB', 'IPCRYPTO_USE_KEY_DB_EXAMPLE_KEYS', 'SECURITY', 'IPCRYPTO_USE_TEST_CMDS', 'IPTCP_TEST_CMD', 'IPECHO_SERVER_CMD', 'IPECHO_CLIENT_CMD', 'USER_MGT_SHELL_CMD']
    },
    'SSH' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'testengine_name'    : ['ipssh'],
        'vc'                 : ['ipnet2', 'ssh', 'ipcrypto'],
        'vxconf'             : ['IPNET_SSH', 'USER_MANAGEMENT', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['CCI_IMPORT_BLOWFISH', 'IPFTP_CMD', 'IPFTPS', 'SSH', 'IPCOM_KEY_DB_CMD', 'IPCOM_USE_KEY_DB', 'IPCRYPTO_USE_KEY_DB_EXAMPLE_KEYS', 'SECURITY', 'IPCRYPTO_USE_TEST_CMDS', 'IPTCP_TEST_CMD', 'IPECHO_SERVER_CMD', 'IPECHO_CLIENT_CMD', 'USER_MGT_SHELL_CMD']
    },
    'SSH-FIPS-140-2' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'testengine_name'    : ['ipssh'],
        'vc'                 : ['ipnet2', 'ssh'],
        'vxconf'             : ['IPNET_SSH', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['CCI_IMPORT_BLOWFISH', 'IPFTP_CMD', 'IPFTPS', 'SSH', 'IPCOM_KEY_DB_CMD', 'IPCOM_USE_KEY_DB', 'IPCRYPTO_USE_KEY_DB_EXAMPLE_KEYS','IPCRYPTO_USE_CMDS','SECURITY'],
        'extra_build_opt'    : ['IPCRYPTO_USE_FIPS=yes']
    },
    'OPENSSL_FIPS' : {
        'capable'            : {
           'vxworks' : {}
        },
        'extra_build_cflags' : [],
        'testengine_name'    : ['openssl_fips'],
        'vc'                 : ['ipcrypto', 'ipnet2', 'openssl_fips'],
        'vxconf'             : ['OPENSSL_FIPS', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO', 'RTP'],
        'vxmake'             : [],
        'vxparam'            : [],
        'vxprj'              : ['OPENSSL_FIPS', 'OPENSSL_FIPS_CTRL_CMD', 'RTP'],
        'vxfile'             : ['/security/openssl_fips/test/share/testFipsLib.c'],
        'rtpfile'            : ['/security/openssl_fips/test/share/testFipsLib.c', '/security/openssl_fips/test/rtpMain.c'],
        'rtplib'             : ['-lHASH', '-lOPENSSL', '-lCRYPTO_FIPS']
    },    
    'SSHCLIENT' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extensions'         : ['uml/generic', 'uml/generic'],
        'extra_build_cflags' : [],
        'testengine_name'    : ['sshclient'],
        'vc'                 : ['ipnet2', 'ssh', 'client', 'ipcrypto'],
        'vxconf'             : ['IPNET_SSH', 'USER_MANAGEMENT', 'IPNET_IPCRYPTO', 'OPENSSL_CRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""],
        'vxprj'              : ['IPSSH_CLIENT_CMD', 'CCI_IMPORT_BLOWFISH', 'IPFTP_CMD', 'IPFTPS', 'SSH', 'IPCOM_KEY_DB_CMD', 'IPCOM_USE_KEY_DB', 'IPCRYPTO_USE_KEY_DB_EXAMPLE_KEYS', 'SECURITY', 'IPCRYPTO_USE_TEST_CMDS', 'IPTCP_TEST_CMD', 'IPECHO_SERVER_CMD', 'IPECHO_CLIENT_CMD', 'USER_MGT_SHELL_CMD']
    },
    'SSL' : {
        'capable'            : {
            'vxworks' : {}
        },
        #'extra_build_cflags' : [],
        'permutations'       : 1,
        'testengine_name'    : ['ipssl'],
        'vc'                 : ['ipnet2', 'ssl'],
        'vxconf'             : ['IPNET_SSL', 'OPENSSL_CRYPTO', 'IPNET_IPCRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxprj'              : ['IPCRYPTO', 'IPCRYPTO_USE_CMDS', 'IPCRYPTO_USE_TEST_CMDS', 'IPFTP_CMD', 'IPFTPS', 'IPSSL', 'IPSSL_USE_CMDS', 'IPSSL_USE_TEST_CMDS', 'IPCOM_KEY_DB_CMD', 'IPCOM_USE_KEY_DB'],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""]
    },
    'L2TP' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : ['-DIPPPP_USE_PPPL2TP', '-DIPPPP_USE_PPPL2TP_LNS', ],
        'networks'           : 2,
        'testengine_name'    : ['ipl2tp'],
        'vc'                 : ['l2tp', 'ipnet2'],
        'vxconf'             : ['IPNET_L2TP'],
        'vxprj'              : ['IPL2TP', 'IPPPP', ],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""]
    },
    'FIREWALL' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extensions'         : ['uml/generic', 'uml/generic', 'uml/generic'],
        'extra_build_cflags' : ['-DIPCOM_VXWORKS_PAD_SHORT_ETHERNET_FRAMES', ],
        'permutations'       : 1,
        'testengine_name'    : ['ipfirewall'],
        'vc'                 : ['firewall','ipnet2'],
        'vxconf'             : ['IPNET_IPSECIKE', 'IPNET_IPSECIKE_IKE', 'IPNET_FIREWALL', 'OPENSSL_CRYPTO', 'IPNET_IPCRYPTO', 'SECURITY_MISC_SEC_CRYPTO'],
        'vxprj'              : ['IPFIREWALL_CMD', 'IPFTPS', 'IPNAT_CMD', 'KEYADM_CMD', 'IPCOM_USE_KEY_DB', 'IPCOM_KEY_DB_CMD' ],
        'vxparam'            : [""" SEC_VAULT_KEY_ENCRYPTING_PW='"donald_duck"'"""]
    },
    'NET_VLAN' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : ['-D_WRS_CONFIG_COMPONENT_VIRTUAL_ROUTER'],
        'permutations'       : 2,
        'testengine_name'    : ['ipnet.vlan'],
        'vc'                 : ['ipnet2', 'iptcp'],
        'vxmake'             : [''],
        'vxprj'              : []
    },
    'QOS' : {
        'capable'            : {
            'vxworks' : {}
        },
        'extra_build_cflags' : ['-DIPCOM_ZEROCOPY=1', '-DIPCOM_CMD_SOCKTEST_USE_ZEROCOPY_API'],
        'testengine_name'    : ['qos'],
        'vc'                 : ['ipnet2','qos'],
        'vxmake'             : ['VIRTUAL_ROUTER'],
        'vxconf'             : ['IPNET_QOS','IPNET_DIFFSERV'],
        'vxprj'              : ['IPQOS_CMD','IPQUEUE_CONFIG_CMD']
    }
}
    
mail = {
    'from'     : 'runtestsuite@windriver.com',
    'instance' : 'UNIX',
    'server'   : 'nw-smtp.wineasy.se'
}

tinderbox = {
    'from'     : 'markus.carlstedt@windriver.com',
    'server'   : 'prod-webmail.windriver.com',
    'to'       : 'markus.carlstedt@windriver.com',
}

platform = {
    'all' : {
        'extra_build_cflags' : ['-DIPCOM_RANDOM_LAPS=1', '-DIPNET_MSP_DISTRIBUTION', '-DIPTESTENGINE', '-g'],
        'extra_build_opt'    : ['FEATURE_SET=msp', 'IPGMAKE=yes', 'IPVERBOSE=no']
    },
    'las' : {
        'extra_build_cflags' : ['-DIPCOM_LAS_SYSLOG_FACILITY=LOG_LOCAL7'],
        'extra_build_opt'    : None
    },
    'lkm' : {
        'extra_build_cflags' : None,
        'extra_build_opt'    : None
    },
    'unix' : {
        'extra_build_cflags' : ['-DIPCOM_SMP_READY', '-DIPCOM_SYSLOG_FILE_MAXSIZE=10485760'],
        'extra_build_opt'    : None
    },
    'vxworks' : {
        'extra_build_cflags' : [],
        'extra_build_opt'    : None
    },
    'vxworks/linux' : {
        'extra_build_cflags' : ['-DIPCOM_RAM_DISK_NO_BLOCK=4096', '-DIPCOM_SYSLOG_FILE_MAXSIZE=10485760'],
        'extra_build_opt'    : None
    }
}

vc_cvs_server = {
    'utelnetd'  : {
        'passwd' : '',
        'server' : 'anonymous@arn-cvs1.wrs.com:/home/cvs'
    },
    'vsftpd'    : {
        'passwd' : '',
        'server' : 'anonymous@arn-cvs1.wrs.com:/home/cvs'
    }
}

vc_dependency = {
    #'ipcrypto' : ['ipxinc'],
}

vc_port_dependency = {
    'unix/socktest' : { 'ipcom' : [ 'ipmcrypto' ] }
}

vc_port_substitute = {
    'las'  : None,
    'lkm'  : {
        'ipcrypto' : ['ipmcrypto']
    },
    'unix' : None
}

simicsTargets = {
    'qsp_arm' : {
        'script' : 'kong-qsp-vxworks-7-smp.simics',
        'console-port' : 31602,
    },
    'fsl_t2t4' : {
        'script' : 'kong-t2080qds-vxworks-7.simics',
        'cov-script' : 'kong-code-coverage-t2080qds.simics',
        'console-port' : 31602,
    },
}

# the value for tftp server and path are only for occuping the position
# since the argument tftpserver/tftppath of runtestsuite.py will provide
# the actual values for VLM targets 
tftp_server = 'old_tftp_server'
tftp_path   = 'old_tftp_path'

vlmTargets = {
    'fsl_imx6' :    { 'image' : 'uVxWorks',
                      'dtb'   : 'imx6q-sabrelite.dtb',
                      'dts'   : '/os/board/freescale/fsl_imx6/imx6q-sabrelite.dts',
                    },

    'itl_generic' : { 'image' : 'vxWorks',
                      'dtb'   : None,
                      'dts'   : None,
                    },
}

vlmTargetJsons = { 'vxsim_linux' : ( 'conf.json', ),
                   'fsl_imx6' :    ( '25002.json', '25003.json', ),
                   'itl_generic' : ( '28525.json', '28526.json', ),
                 }

# helix config

helixEnableImageCopy = False

helixBuild = {
                 'itl_generic'        : { 'MIP'   : 'IPNET_DYNAMIC',
                                          'image' : 'vxWorks',
                                          'dtb'   : None,
                                        },
                 'nxp_layerscape_a72' : { 'MIP'   : 'IPNET_D_NXP',
                                          'image' : 'uVxWorks',
                                          'dtb'   : 'ls1046a-rdb-pb.dtb',
                                        }, 
                }

helixHosts = {
    'pek-canoepass' : { 'direct_ethernet' : ( 'enp7s0f1', ),
                        'target' : ( '28567', ),
                        'vm'     : ( '192.168.199.12', ),
                        'tftp_client' : '10.0.0.2',
                        'tftp_server' : '10.0.0.200',
                        'tftp_path'   : '/folk/lchen3/tftpboot/helix/itl_generic/',
                      },
    # setenv bootcmd "tftpboot 0x85000000 nxp/uVxWorks; tftpboot 0x84000000 nxp/ls1046a-rdb-pb.dtb; bootm 0x85000000 - 0x84000000"
    'pek-kong-02' :   { 'direct_ethernet' : ( 'enp1s0', ),
                        'target' : ( '28593', ),
                        'vm'     : ( '192.168.199.12', ),
                        'tftp_client' : '10.0.0.2',
                        'tftp_server' : '10.0.0.200',
                        'tftp_path'   : '/folk/lchen3/tftpboot/helix/nxp/',
                      },             
}

