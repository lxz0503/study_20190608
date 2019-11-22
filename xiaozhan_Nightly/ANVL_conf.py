#!/usr/bin/env python
# configurations for ANVL automation
import os
import re
import sys

ANVL_targets = {


'Q35' : {

    'ICMPv4'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlicmp',
                      'logfile' : 'ICMPv4.log',
                      'allcase' : '1-5.3 7.1-10',
                      #'allcase' : '1-2',
                      'engine'  : 'icmp',
                  },

    'ICMPv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlicmpv6',
                      'logfile' : 'ICMPv6.log',
                      'allcase' : '1-4.4 4.6 4.7 4.9-5.9 5.11-10',
                      'engine'  : 'icmpv6',
                },

    'IPv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlip',
                      'logfile' : 'IPv4.log',
                      'allcase' : '1-5.5 5.7-5.15 5.20-5.24 5.27-7.5',
                      'engine'  : 'ip',
                  },
    #'NDP'  : {
                    # 'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlndp',
                    # 'logfile' : 'ndp.log',
                    # 'allcase' : ''
                    # 'engine'  : 'ipv6'
              #},


    'IPv6FlowLevelEnable'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlipv6',
                      'logfile' : 'IPv6FlowLevelEnable.log',
                      'allcase' : '1-8.15 8.17-16.1 16.4-16.7',
                      'engine'  : 'ipv6',
                  },

    'IPv6FlowLevelDisable'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlipv6_FlowLevelDisable',
                      'logfile' : 'IPv6FlowLevelDisable.log',
                      'allcase' : '7 11',
                      'engine'  : 'ipv6',
                  },

    'IPGW'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlipgw',
                      'logfile' : 'IPGW.log',
                      'allcase' : '1-2.9 2.11-5',
                      'engine'  : 'ipgw',
                  },

    'IGMPv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvligmp',
                      'logfile' : 'IGMPv2.log',
                      'allcase' : '1-3.9 3.11-6',
                      'engine'  : 'igmp',
                  },

    'IGMPv3'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvligmpv3',
                      'logfile' : 'IGMPv3.log',
                      'allcase' : '1-5.10 5.12-6.9 6.11-7 9-10',
                      'engine'  : 'igmpv3',
                  },

    'Mldv1'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlmld',
                      'logfile' : 'Mldv1.log',
                      'allcase' : '1-8.3 8.5-8.7',
                      'engine'  : 'ipv6-mld',
                  },

    'Mldv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlmldv2',
                      'logfile' : 'Mldv2.log',
                      'allcase' : '1-3.1 3.3-12.2 12.4-12.22 12.25-13.14 13.16-14.13 14.15-14.18',
                      'engine'  : 'ipv6-mldv2',
                  },

    'DHCPC'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvldhcpclient',
                      'logfile' : 'DHCPC.log',
                      'allcase' : '1-6.2 6.4-6.6 6.8-7 8.2-13.6 13.9 14.1 14.3 16.1-16.5 16.7-16.8 16.10',
                      'engine'  : 'dhcp-client',
                  },

    'DHCPS'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvldhcpserver',
                      'logfile' : 'DHCPS.log',
                      'allcase' : '1-2.6 4.1-5.5 6.1 6.3 6.4 7.1-10.1 10.3-10.5 10.7-10.11 10.14-10.18 11.2 12.2-12.5 12.7 12.9 12.11 12.13 13.1-13.4  14.1 15.2 16.1-16.3',
                      'engine'  : 'dhcp-server',
                  },

    'RipPoison'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlrip',
                      'logfile' : 'RipPoison.log',
                      'allcase' : '1-2 3.2 3.4-6.6 7-10.1 10.3-15',#3.1 6.8 10.2 17.1
                      'engine'  : 'rip',
                  },

    'RipCompatibility'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlrip_Compatibility',
                      'logfile' : 'RipCompatibility.log',
                      'allcase' : '16',
                      'engine'  : 'rip',
                  },

    'RipSplitHorizon'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlrip_SplitHorizon',
                      'logfile' : 'RipSplitHorizon.log',
                      'allcase' : '8.17',
                      'engine'  : 'rip',
                  },

    'TcpCore_UrgPtrRFC1122'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvltcp',
                      'logfile' : 'TcpCore_UrgPtrRFC1122.log',
                      'allcase' : '1-11.20 11.22-12.20 12.22-13 15.20-15.29 16-17.18 17.20 18-23',
                      'engine'  : 'tcp-core',
                  },

    'TcpCore_UrgPtrRFC793'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvltcp_UrgPtrRFC793',
                      'logfile' : 'TcpCore_UrgPtrRFC793.log',
                      'allcase' : '19.21-19.23',
                      'engine'  : 'tcp-core',
                  },

    'TcpAdv'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvltcpadv',
                      'logfile' : 'TcpAdv.log',
                      'allcase' : '1-5.19 5.21-7 8.18-8.19 8.23',
                      'engine'  : 'tcp-advanced',
                  },

    'TcpPerf'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvltcpperf',
                      'logfile' : 'TcpPerf.log',
                      'allcase' : '1-2.22 2.24-5.19 6-7.23',
                      'engine'  : 'tcp-highperf',
                  },
   'UDP'  : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvludp',
                      'logfile' : 'UDP.log',
                      'allcase' : '',
                      'engine'  : 'udp',
                  },


    'IPsecAHv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlipsecah',
                      'logfile' : 'IPsecAHv4.log',
                      'allcase' : '1-9.1 9.3-10',
                      'engine'  : 'ipsec-ah',
                  },

    'IPsecAHv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlipsecv6ah',
                      'logfile' : 'IPsecAHv6.log',
                      'allcase' : '1-5.3 5.7-7 9-11 13.1-13.2 14.2-14.3 16-18.1 18.3', #case 17.* is nonexistent
                      'engine'  : 'ipsecv6-ah',
                  },

#    'IPsecAHv6Transport'  : {        
#                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlipsecv6ah_transport128',
#                      'logfile' : 'IPsecAHv6_transport128.log',
#                      'allcase' : '5.6',  #12.1 are pass, but ANVL cannot recognize the authenticated NeigbourAdvertise and hang.
#                      'engine'  : 'ipsecv6-ah',
#                  },

    'IPsecESPv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlipsecesp',
                      'logfile' : 'IPsecESPv4.log', # 11.7 25.1 25.2 will hang. 11.2 11.4 11.6 11.7 11.9 11.10 cannot support by WIND00423259. 7.5<-vxWorks doesn't support "-auth none" or missing "-auth" option. So vxWorks doesn't support NULL Authentication algorithm?
                      'allcase' : '1-7.4 8-10.1 10.3-11.1 11.3 11.5 11.8 24 25.3-25.4 26.2-26.4 27-29.3 31-34',  
                      #'allcase' : '27.1',
                      'engine'  : 'ipsec-esp',
                 },

    'IPsecESPv4-noencry'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlipsecesp-noencry',
                      'logfile' : 'IPsecESPv4-noencry.log',
                      'allcase' : '8.4 8.6 22-23 26.7',
                      'engine'  : 'ipsec-esp',
                 },

    'IPsecESPv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlipsecv6esp',
                      'logfile' : 'IPsecESPv6.log',
                      'allcase' : '1.1-1.3 2.1-13 14.3  15.2-15.4 16.2-19.3 20.2-25.1 25.3',#14.1 14.2 will hang
                      'engine'  : 'ipsecv6-esp',
                  },

    'IPsecESPv6-des'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlipsecv6esp-des',
                      'logfile' : 'IPsecESPv6-des.log',
                      'allcase' : '5 7.5 7.7 9',
                      'engine'  : 'ipsecv6-esp',
                  },

    'IKEMain'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlike',
                      'logfile' : 'IKEMain.log',
                      'allcase' : '1-3.12 3.15 3.17 3.19 3.21-4.15 4.17-4.27 4.29 5.1-5.2 6.1-6.5 6.7-7.10 7.12-7.16 7.18 7.20 7.22-7.23 7.25 7.27-8.1 8.3-8.7 9.1-9.8 9.11-9.13 9.15-10 11.2 11.4-11.15 12.1-12.3 12.5 12.7-12.14 12.17-12.27 12.29 12.31 13 19-23',#4.16(WIND00359787), 9.14(WIND00409415) don't support on vxWorks.
                      #'allcase' : '1.1',
                      'engine'  : 'ike',
                  },

    'IKEAggressive'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlike_aggressive_resp',
                      'logfile' : 'IKEAggressive.log',
                      'allcase' : '14.1-14.16 14.18-17.5 17.7-18.5 18.7-18.14 18.16-18.27',#14.17 skipped for enhancement WIND00409237
                      'engine'  : 'ike',                      
                  },

    'IKECombinedSA'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlike_combined_sa',
                      'logfile' : 'IKECombinedSA.log',
                      'allcase' : '9.9, 9.10, 11.1, 11.3, 11.18',
                      'engine'  : 'ike',  
                  },

    'IKEDH1md5'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlike_dh1_md5',
                      'logfile' : 'IKEDH1md5.log',
                      'allcase' : '2.19, 4.9, 7.7, 14.5, 16.9, 18.11',
                      'engine'  : 'ike',  
                  },

    'IKEDH1sha'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlike_dh1_sha',
                      'logfile' : 'IKEDH1sha.log',
                      'allcase' : '2.20, 4.10, 14.6, 16.10',
                      'engine'  : 'ike',  
                  },

    'IKEv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlikev2',
                      'logfile' : 'IKEv2.log',
                      'allcase' : '1-4.3 5-6.5 6.7-9.1 9.3-12 14-15.1 15.3-17 21-22 24-30.1 30.3-33.1 33.5-33.7 33.9-36.2 38.1-38.2 38.8-38.9 38.13', # 6.3 14.9 19 20.2 is dieded
                      'engine'  : 'ikev2',  
                  },

    'IKEIPv6Main'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlikev6',
                      'logfile' : 'IKEIPv6Main.log',
                      'allcase' : '1-3.12 3.15 3.17 3.19 3.21-4.15 4.17-4.27 4.29 5.1-5.2 6.1-6.5 6.7-7.5 7.7-7.16 7.18 7.20 7.22-7.23 7.25 7.27-8.1 8.3-8.6 8.9-9.8 9.11-9.13 9.15-10 11.2 11.4-11.15 12.1-12.3 12.5 12.7-12.14 12.17-12.27 12.29 12.31 13 19-23', #3.14(WIND00409237), 4.16(WIND00359787), 9.14(WIND00409415) don't support on vxWorks.
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6CombinedSA'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlikev6_combined_sa',
                      'logfile' : 'IKEIPv6CombinedSA.log',
                      'allcase' : '2.20 9.9, 9.10, 11.1, 11.3, 11.18 14.6',
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6Aggressive'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlikev6_aggressive',
                      'logfile' : 'IKEIPv6Aggressive.log',
                      'allcase' : '14.1-14.16 14.18-15.13 15.15-17.5 17.7-18.5 18.7-18.9 18.11-18.17 18.20-18.26', #14.17,15.14 skipped for enhancement WIND00409237. 18.18 18.19 18.27 ANVL case bug.
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6md5'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL880/ANVL-SRC/DocUserQ35/anvlikev6_dh1_md5',
                      'logfile' : 'IKEIPv6md5.log',
                      'allcase' : '2.19 4.9 4.10 7.7 16.9 16.10 14.5 18.11',
                      'engine'  : 'ike-ipv6',
                  },
},






'pcPentium4' : {

    'ICMPv4'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlicmp',
                      'logfile' : 'ICMPv4.log',
                      'allcase' : '',
                      'engine'  : 'icmp',
                  },

    'ICMPv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlicmpv6',
                      'logfile' : 'ICMPv6.log',
                      'allcase' : '1-4.4 4.6 4.7 4.9-5.9 5.11-10',
                      'engine'  : 'icmpv6',
                },

    'IPv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlip',
                      'logfile' : 'IPv4.log',
                      'allcase' : '',
                      'engine'  : 'ip',
                  },

    'IPv6FlowLevelEnable'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlipv6',
                      'logfile' : 'IPv6FlowLevelEnable.log',
                      'allcase' : '',
                      'engine'  : 'ipv6',
                  },

    'IPv6FlowLevelDisable'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlipv6_FlowLevelDisable',
                      'logfile' : 'IPv6FlowLevelDisable.log',
                      'allcase' : '7 11',
                      'engine'  : 'ipv6',
                  },

    'IPGW'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlipgw',
                      'logfile' : 'IPGW.log',
                      'allcase' : '',
                      'engine'  : 'ipgw',
                  },

    'IGMPv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvligmp',
                      'logfile' : 'IGMPv2.log',
                      'allcase' : '',
                      'engine'  : 'igmp',
                  },

#  cguo: vxWorks only supplies API Socket Options for IGMP/MLD Joining and Leaving Groups.
#  For details, see 12.4.1 in "wr_net_stack_programmers_guide_vol1". The host side 
#  whole functions, which are tested by these ANVL IGMP/MLD host side cases, depends 
#  on user's own application. So the cases PASS or FAIL results depend on user's own
#  application, but not related with vxWorks APIs. So I cancel these ANVL IGMP/MLD host
#  side cases to save effort. If you have interest to develop IGMP host side applications,
#  see my developed "Igmp-Join-Leave.c" as a demo.  

#    'IGMPv2-host'  : {        
#		              'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvligmp-host',
#					  'logfile' : 'IGMPv2-host.log',
#		              'allcase' : '1-4.3 4.5-6',    #4.4 case has bug and will hang
#	                  'engine'  : 'igmp',
#	               },
	
	
    'IGMPv3'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvligmpv3',
                      'logfile' : 'IGMPv3.log',
                      'allcase' : '',
                      'engine'  : 'igmpv3',
                  },

#    'IGMPv3-host'  : {        
#                     'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvligmpv3-host',
#                     'logfile' : 'IGMPv3-host.log',
#                     'allcase' : '',    
#                     'engine'  : 'igmpv3',
#                  },
	
	'Mldv1'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlmld',
                      'logfile' : 'Mldv1.log',
                      'allcase' : '',
                      'engine'  : 'ipv6-mld',
                  },

    'Mldv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlmldv2',
                      'logfile' : 'Mldv2.log',
                      'allcase' : '',
                      'engine'  : 'ipv6-mldv2',
                  },

    'DHCPC'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvldhcpclient',
                      'logfile' : 'DHCPC.log',
                      'allcase' : '',
                      'engine'  : 'dhcp-client',
                  },

    'DHCPS'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvldhcpserver',
                      'logfile' : 'DHCPS.log',
                      'allcase' : '',
                      'engine'  : 'dhcp-server',
                  },

    'RipPoison'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlrip',
                      'logfile' : 'RipPoison.log',
                      'allcase' : '1-15 17',
                      'engine'  : 'rip',
                  },

    'RipCompatibility'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlrip_Compatibility',
                      'logfile' : 'RipCompatibility.log',
                      'allcase' : '16',
                      'engine'  : 'rip',
                  },

    'RipSplitHorizon'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlrip_SplitHorizon',
                      'logfile' : 'RipSplitHorizon.log',
                      'allcase' : '8.17',
                      'engine'  : 'rip',
                  },

    'TcpCore_UrgPtrRFC1122'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvltcp',
                      'logfile' : 'TcpCore_UrgPtrRFC1122.log',
                      'allcase' : '',
                      'engine'  : 'tcp-core',
                  },

    'TcpCore_UrgPtrRFC793'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvltcp_UrgPtrRFC793',
                      'logfile' : 'TcpCore_UrgPtrRFC793.log',
                      'allcase' : '19.21-19.23',
                      'engine'  : 'tcp-core',
                  },

    'TcpAdv'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvltcpadv',
                      'logfile' : 'TcpAdv.log',
                      'allcase' : '1-8',
                      'engine'  : 'tcp-advanced',
                  },

    'TcpPerf'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvltcpperf',
                      'logfile' : 'TcpPerf.log',
                      'allcase' : '',
                      'engine'  : 'tcp-highperf',
                  },

    'IPsecAHv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlipsecah',
                      'logfile' : 'IPsecAHv4.log',
                      'allcase' : '',
                      'engine'  : 'ipsec-ah',
                  },

    'IPsecAHv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlipsecv6ah',
                      'logfile' : 'IPsecAHv6.log',
                      'allcase' : '1-5.3 5.7-11 12.2-18', # 12.1 is pass, but ANVL cannot recognize the authenticated NeigbourAdvertise and hang. #case 17.* is nonexistent
                      'engine'  : 'ipsecv6-ah',
                  },

#    'IPsecAHv6_transport128'  : {        
#                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlipsecv6ah_transport128',
#                      'logfile' : 'IPsecAHv6_transport128.log',
#                      'allcase' : '5.6 12.1',  # 5.6, 12.1 are pass, but ANVL cannot recognize the authenticated NeigbourAdvertise and hang.
#                      'engine'  : 'ipsecv6-ah',
#                  },

    'IPsecESPv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlipsecesp',
                      'logfile' : 'IPsecESPv4.log', # 11.7 25.1 25.2 will hang. 11.2 11.4 11.6 11.7 11.9 11.10 cannot support by WIND00423259. 7.5<-vxWorks doesn't support "-auth none" or missing "-auth" option. So vxWorks doesn't support NULL Authentication algorithm?
                      'allcase' : '1-7.4 8-11.1 11.3 11.5 11.8 24 25.3-26.4 27-34',  
                      'engine'  : 'ipsec-esp',
                 },

    'IPsecESPv4-noencry'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlipsecesp-noencry',
                      'logfile' : 'IPsecESPv4-noencry.log',
                      'allcase' : '8.4 8.6 22-23 26.7',
                      'engine'  : 'ipsec-esp',
                 },

    'IPsecESPv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlipsecv6esp',
                      'logfile' : 'IPsecESPv6.log',
                      'allcase' : '1-13 14.3 15-25',#14.1 14.2 will hang
                      'engine'  : 'ipsecv6-esp',
                  },

    'IPsecESPv6-des'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlipsecv6esp-des',
                      'logfile' : 'IPsecESPv6-des.log',
                      'allcase' : '5 7.5 7.7 9',
                      'engine'  : 'ipsecv6-esp',
                  },

    'IKEMain'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlike',
                      'logfile' : 'IKEMain.log',
                      'allcase' : '1-4.15 4.17-5.3 6-9.8 9.11-9.13 9.15-10 11.2 11.4-11.17 11.19 12-13 19-23',#4.16(WIND00359787), 9.14(WIND00409415) don't support on vxWorks.
                      'engine'  : 'ike',
                  },

    'IKEAggressive'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlike_aggressive_resp',
                      'logfile' : 'IKEAggressive.log',
                      'allcase' : '14.1-14.16 14.18-18.5 18.7-18.28',#14.17 skipped for enhancement WIND00409237
                      'engine'  : 'ike',                      
                  },

    'IKECombinedSA'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlike_combined_sa',
                      'logfile' : 'IKECombinedSA.log',
                      'allcase' : '9.9, 9.10, 11.1, 11.3, 11.18',
                      'engine'  : 'ike',  
                  },

    'IKEDH1md5'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlike_dh1_md5',
                      'logfile' : 'IKEDH1md5.log',
                      'allcase' : '2.19, 4.9, 7.7, 14.5, 16.9, 18.11',
                      'engine'  : 'ike',  
                  },

    'IKEDH1sha'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlike_dh1_sha',
                      'logfile' : 'IKEDH1sha.log',
                      'allcase' : '2.20, 4.10, 14.6, 16.10',
                      'engine'  : 'ike',  
                  },

    'IKEv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlikev2',
                      'logfile' : 'IKEv2.log',
                      'allcase' : '1-6.2 6.4-14.8 14.10-18 20.1 21-22 24-38', # 6.3 14.9 19 20.2 is dieded
                      'engine'  : 'ikev2',  
                  },

    'IKEIPv6Main'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlikev6',
                      'logfile' : 'IKEIPv6Main.log',
                      'allcase' : '1-3.13 3.15-4.15 4.17-5.3 6-8.6 8.8-9.8 9.11-9.13 9.15-10 11.2 11.4-11.17 11.19-13 19-23', #3.14(WIND00409237), 4.16(WIND00359787), 9.14(WIND00409415) don't support on vxWorks.
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6CombinedSA'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlikev6_combined_sa',
                      'logfile' : 'IKEIPv6CombinedSA.log',
                      'allcase' : '2.20 9.9, 9.10, 11.1, 11.3, 11.18 14.6',
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6Aggressive'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlikev6_aggressive',
                      'logfile' : 'IKEIPv6Aggressive.log',
                      'allcase' : '14.1-14.16 14.18-15.13 15.15-18.17 18.20-18.26 18.28', #14.17,15.14 skipped for enhancement WIND00409237. 18.18 18.19 18.27 ANVL case bug.
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6md5'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUser/anvlikev6_dh1_md5',
                      'logfile' : 'IKEIPv6md5.log',
                      'allcase' : '2.19 4.9 4.10 7.7 16.9 16.10 14.5 18.11',
                      'engine'  : 'ike-ipv6',
                  },
},


'SMPQ35' : {

    'ICMPv4'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlicmp',
                      'logfile' : 'ICMPv4.log',
                      'allcase' : '',
                      'engine'  : 'icmp',
                  },

    'ICMPv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlicmpv6',
                      'logfile' : 'ICMPv6.log',
                      'allcase' : '1-4.4 4.6 4.7 4.9-5.9 5.11-10',
                      'engine'  : 'icmpv6',
                },

    'IPv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlip',
                      'logfile' : 'IPv4.log',
                      'allcase' : '',
                      'engine'  : 'ip',
                  },

    'IPv6FlowLevelEnable'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlipv6',
                      'logfile' : 'IPv6FlowLevelEnable.log',
                      'allcase' : '',
                      'engine'  : 'ipv6',
                  },

    'IPv6FlowLevelDisable'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlipv6_FlowLevelDisable',
                      'logfile' : 'IPv6FlowLevelDisable.log',
                      'allcase' : '7 11',
                      'engine'  : 'ipv6',
                  },

    'IPGW'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlipgw',
                      'logfile' : 'IPGW.log',
                      'allcase' : '',
                      'engine'  : 'ipgw',
                  },

    'IGMPv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvligmp',
                      'logfile' : 'IGMPv2.log',
                      'allcase' : '',
                      'engine'  : 'igmp',
                  },

    'IGMPv3'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvligmpv3',
                      'logfile' : 'IGMPv3.log',
                      'allcase' : '',
                      'engine'  : 'igmpv3',
                  },

    'Mldv1'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlmld',
                      'logfile' : 'Mldv1.log',
                      'allcase' : '',
                      'engine'  : 'ipv6-mld',
                  },

    'Mldv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlmldv2',
                      'logfile' : 'Mldv2.log',
                      'allcase' : '',
                      'engine'  : 'ipv6-mldv2',
                  },

    'DHCPC'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvldhcpclient',
                      'logfile' : 'DHCPC.log',
                      'allcase' : '',
                      'engine'  : 'dhcp-client',
                  },

    'DHCPS'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvldhcpserver',
                      'logfile' : 'DHCPS.log',
                      'allcase' : '',
                      'engine'  : 'dhcp-server',
                  },

    'RipPoison'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlrip',
                      'logfile' : 'RipPoison.log',
                      'allcase' : '1-15 17',
                      'engine'  : 'rip',
                  },

    'RipCompatibility'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlrip_Compatibility',
                      'logfile' : 'RipCompatibility.log',
                      'allcase' : '16',
                      'engine'  : 'rip',
                  },

    'RipSplitHorizon'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlrip_SplitHorizon',
                      'logfile' : 'RipSplitHorizon.log',
                      'allcase' : '8.17',
                      'engine'  : 'rip',
                  },

    'TcpCore_UrgPtrRFC1122'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvltcp',
                      'logfile' : 'TcpCore_UrgPtrRFC1122.log',
                      'allcase' : '',
                      'engine'  : 'tcp-core',
                  },

    'TcpCore_UrgPtrRFC793'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvltcp_UrgPtrRFC793',
                      'logfile' : 'TcpCore_UrgPtrRFC793.log',
                      'allcase' : '19.21-19.23',
                      'engine'  : 'tcp-core',
                  },

    'TcpAdv'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvltcpadv',
                      'logfile' : 'TcpAdv.log',
                      'allcase' : '1-8',
                      'engine'  : 'tcp-advanced',
                  },

    'TcpPerf'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvltcpperf',
                      'logfile' : 'TcpPerf.log',
                      'allcase' : '',
                      'engine'  : 'tcp-highperf',
                  },

    'IPsecAHv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlipsecah',
                      'logfile' : 'IPsecAHv4.log',
                      'allcase' : '',
                      'engine'  : 'ipsec-ah',
                  },

    'IPsecAHv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlipsecv6ah',
                      'logfile' : 'IPsecAHv6.log',
                      'allcase' : '1-5.3 5.7-11 12.2-18', # 12.1 is pass, but ANVL cannot recognize the authenticated NeigbourAdvertise and hang. #case 17.* is nonexistent
                      'engine'  : 'ipsecv6-ah',
                  },

#    'IPsecAHv6_transport128'  : {        
#                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlipsecv6ah_transport128',
#                      'logfile' : 'IPsecAHv6_transport128.log',
#                      'allcase' : '5.6 12.1',  # 5.6, 12.1 are pass, but ANVL cannot recognize the authenticated NeigbourAdvertise and hang.
#                      'engine'  : 'ipsecv6-ah',
#                  },

    'IPsecESPv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlipsecesp',
                      'logfile' : 'IPsecESPv4.log', # 11.7 25.1 25.2 will hang. 11.2 11.4 11.6 11.7 11.9 11.10 cannot support by WIND00423259. 7.5<-vxWorks doesn't support "-auth none" or missing "-auth" option. So vxWorks doesn't support NULL Authentication algorithm?
                      'allcase' : '1-7.4 8-11.1 11.3 11.5 11.8 24 25.3-26.4 27-34',  
                      'engine'  : 'ipsec-esp',
                 },

    'IPsecESPv4-noencry'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlipsecesp-noencry',
                      'logfile' : 'IPsecESPv4-noencry.log',
                      'allcase' : '8.4 8.6 22-23 26.7',
                      'engine'  : 'ipsec-esp',
                 },

    'IPsecESPv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlipsecv6esp',
                      'logfile' : 'IPsecESPv6.log',
                      'allcase' : '1-13 14.3 15-25',#14.1 14.2 will hang
                      'engine'  : 'ipsecv6-esp',
                  },

    'IPsecESPv6-des'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlipsecv6esp-des',
                      'logfile' : 'IPsecESPv6-des.log',
                      'allcase' : '5 7.5 7.7 9',
                      'engine'  : 'ipsecv6-esp',
                  },

    'IKEMain'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlike',
                      'logfile' : 'IKEMain.log',
                      'allcase' : '1-4.15 4.17-5.3 6-9.8 9.11-9.13 9.15-10 11.2 11.4-11.17 11.19 12-13 19-23',#4.16(WIND00359787), 9.14(WIND00409415) don't support on vxWorks.
                      'engine'  : 'ike',
                  },

    'IKEAggressive'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlike_aggressive_resp',
                      'logfile' : 'IKEAggressive.log',
                      'allcase' : '14.1-14.16 14.18-18',#14.17 skipped for enhancement WIND00409237
                      'engine'  : 'ike',                      
                  },

    'IKECombinedSA'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlike_combined_sa',
                      'logfile' : 'IKECombinedSA.log',
                      'allcase' : '9.9, 9.10, 11.1, 11.3, 11.18',
                      'engine'  : 'ike',  
                  },

    'IKEDH1md5'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlike_dh1_md5',
                      'logfile' : 'IKEDH1md5.log',
                      'allcase' : '2.19, 4.9, 7.7, 14.5, 16.9, 18.11',
                      'engine'  : 'ike',  
                  },

    'IKEDH1sha'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlike_dh1_sha',
                      'logfile' : 'IKEDH1sha.log',
                      'allcase' : '2.20, 4.10, 14.6, 16.10',
                      'engine'  : 'ike',  
                  },

    'IKEv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlikev2',
                      'logfile' : 'IKEv2.log',
                      'allcase' : '1-4.3 5-6.2 6.4-14.8 14.10-18 20.1 21-22 24-38', # 6.3 14.9 19 20.2 is dieded
                      'engine'  : 'ikev2',  
                  },

    'IKEIPv6Main'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlikev6',
                      'logfile' : 'IKEIPv6Main.log',
                      'allcase' : '1-3.13 3.15-4.15 4.17-5.3 6-8.6 8.8-9.8 9.11-9.13 9.15-10 11.2 11.4-11.17 11.19-13 19-23', #3.14(WIND00409237), 4.16(WIND00359787), 9.14(WIND00409415) don't support on vxWorks.
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6CombinedSA'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlikev6_combined_sa',
                      'logfile' : 'IKEIPv6CombinedSA.log',
                      'allcase' : '2.20 9.9, 9.10, 11.1, 11.3, 11.18 14.6',
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6Aggressive'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlikev6_aggressive',
                      'logfile' : 'IKEIPv6Aggressive.log',
                      'allcase' : '14.1-14.16 14.18-15.13 15.15-18.17 18.20-18.26 18.28', #14.17,15.14 skipped for enhancement WIND00409237. 18.18 18.19 18.27 ANVL case bug.
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6md5'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL860/ANVL-SRC/DocUserSMPQ35/anvlikev6_dh1_md5',
                      'logfile' : 'IKEIPv6md5.log',
                      'allcase' : '2.19 4.9 4.10 7.7 16.9 16.10 14.5 18.11',
                      'engine'  : 'ike-ipv6',
                  },
},







'bsp6x_itl_x86_2_1_2_1' : {

    'ICMPv4'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlicmp',
                      'logfile' : 'ICMPv4.log',
                      'allcase' : '',
                      'engine'  : 'icmp',
                  },

    'ICMPv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlicmpv6',
                      'logfile' : 'ICMPv6.log',
                      'allcase' : '1-4.4 4.6 4.7 4.9-5.9 5.11-10',
                      'engine'  : 'icmpv6',
                },

    'IPv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlip',
                      'logfile' : 'IPv4.log',
                      'allcase' : '',
                      'engine'  : 'ip',
                  },

    'IPv6FlowLevelEnable'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlipv6',
                      'logfile' : 'IPv6FlowLevelEnable.log',
                      'allcase' : '',
                      'engine'  : 'ipv6',
                  },

    'IPv6FlowLevelDisable'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlipv6_FlowLevelDisable',
                      'logfile' : 'IPv6FlowLevelDisable.log',
                      'allcase' : '7 11',
                      'engine'  : 'ipv6',
                  },

    'IPGW'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlipgw',
                      'logfile' : 'IPGW.log',
                      'allcase' : '',
                      'engine'  : 'ipgw',
                  },

    'IGMPv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvligmp',
                      'logfile' : 'IGMPv2.log',
                      'allcase' : '',
                      'engine'  : 'igmp',
                  },

    'IGMPv3'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvligmpv3',
                      'logfile' : 'IGMPv3.log',
                      'allcase' : '',
                      'engine'  : 'igmpv3',
                  },

    'Mldv1'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlmld',
                      'logfile' : 'Mldv1.log',
                      'allcase' : '',
                      'engine'  : 'ipv6-mld',
                  },

    'Mldv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlmldv2',
                      'logfile' : 'Mldv2.log',
                      'allcase' : '',
                      'engine'  : 'ipv6-mldv2',
                  },

    'DHCPC'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvldhcpclient',
                      'logfile' : 'DHCPC.log',
                      'allcase' : '',
                      'engine'  : 'dhcp-client',
                  },

    'DHCPS'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvldhcpserver',
                      'logfile' : 'DHCPS.log',
                      'allcase' : '',
                      'engine'  : 'dhcp-server',
                  },

    'RipPoison'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlrip',
                      'logfile' : 'RipPoison.log',
                      'allcase' : '1-15 17',
                      'engine'  : 'rip',
                  },

    'RipCompatibility'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlrip_Compatibility',
                      'logfile' : 'RipCompatibility.log',
                      'allcase' : '16',
                      'engine'  : 'rip',
                  },

    'RipSplitHorizon'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlrip_SplitHorizon',
                      'logfile' : 'RipSplitHorizon.log',
                      'allcase' : '8.17',
                      'engine'  : 'rip',
                  },

    'TcpCore_UrgPtrRFC1122'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvltcp',
                      'logfile' : 'TcpCore_UrgPtrRFC1122.log',
                      'allcase' : '',
                      'engine'  : 'tcp-core',
                  },

    'TcpCore_UrgPtrRFC793'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvltcp_UrgPtrRFC793',
                      'logfile' : 'TcpCore_UrgPtrRFC793.log',
                      'allcase' : '19.21-19.23',
                      'engine'  : 'tcp-core',
                  },

    'TcpAdv'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvltcpadv',
                      'logfile' : 'TcpAdv.log',
                      'allcase' : '1-8',
                      'engine'  : 'tcp-advanced',
                  },

    'TcpPerf'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvltcpperf',
                      'logfile' : 'TcpPerf.log',
                      'allcase' : '',
                      'engine'  : 'tcp-highperf',
                  },

    'IPsecAHv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlipsecah',
                      'logfile' : 'IPsecAHv4.log',
                      'allcase' : '',
                      'engine'  : 'ipsec-ah',
                  },

    'IPsecAHv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlipsecv6ah',
                      'logfile' : 'IPsecAHv6.log',
                      'allcase' : '1-5.3 5.7-11 12.2-18', # 12.1 is pass, but ANVL cannot recognize the authenticated NeigbourAdvertise and hang. #case 17.* is nonexistent
                      'engine'  : 'ipsecv6-ah',
                  },

#    'IPsecAHv6_transport128'  : {        
#                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSMPQ35/anvlipsecv6ah_transport128',
#                      'logfile' : 'IPsecAHv6_transport128.log',
#                      'allcase' : '5.6 12.1',  # 5.6, 12.1 are pass, but ANVL cannot recognize the authenticated NeigbourAdvertise and hang.
#                      'engine'  : 'ipsecv6-ah',
#                  },

    'IPsecESPv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlipsecesp',
                      'logfile' : 'IPsecESPv4.log', # 11.7 25.1 25.2 will hang. 11.2 11.4 11.6 11.7 11.9 11.10 cannot support by WIND00423259. 7.5<-vxWorks doesn't support "-auth none" or missing "-auth" option. So vxWorks doesn't support NULL Authentication algorithm?
                      'allcase' : '1-7.4 8-11.1 11.3 11.5 11.8 24 25.3-26.4 27-34',  
                      'engine'  : 'ipsec-esp',
                 },

    'IPsecESPv4-noencry'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlipsecesp-noencry',
                      'logfile' : 'IPsecESPv4-noencry.log',
                      'allcase' : '8.4 8.6 22-23 26.7',
                      'engine'  : 'ipsec-esp',
                 },

    'IPsecESPv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlipsecv6esp',
                      'logfile' : 'IPsecESPv6.log',
                      'allcase' : '1-13 14.3 15-25',#14.1 14.2 will hang
                      'engine'  : 'ipsecv6-esp',
                  },

    'IPsecESPv6-des'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlipsecv6esp-des',
                      'logfile' : 'IPsecESPv6-des.log',
                      'allcase' : '5 7.5 7.7 9',
                      'engine'  : 'ipsecv6-esp',
                  },

    'IKEMain'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlike',
                      'logfile' : 'IKEMain.log',
                      'allcase' : '1-4.15 4.17-5.3 6-9.8 9.11-9.13 9.15-10 11.2 11.4-11.17 11.19 12-13 19-23',#4.16(WIND00359787), 9.14(WIND00409415) don't support on vxWorks.
                      'engine'  : 'ike',
                  },

    'IKEAggressive'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlike_aggressive_resp',
                      'logfile' : 'IKEAggressive.log',
                      'allcase' : '14.1-14.16 14.18-18',#14.17 skipped for enhancement WIND00409237
                      'engine'  : 'ike',                      
                  },

    'IKECombinedSA'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlike_combined_sa',
                      'logfile' : 'IKECombinedSA.log',
                      'allcase' : '9.9, 9.10, 11.1, 11.3, 11.18',
                      'engine'  : 'ike',  
                  },

    'IKEDH1md5'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlike_dh1_md5',
                      'logfile' : 'IKEDH1md5.log',
                      'allcase' : '2.19, 4.9, 7.7, 14.5, 16.9, 18.11',
                      'engine'  : 'ike',  
                  },

    'IKEDH1sha'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlike_dh1_sha',
                      'logfile' : 'IKEDH1sha.log',
                      'allcase' : '2.20, 4.10, 14.6, 16.10',
                      'engine'  : 'ike',  
                  },

    'IKEv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlikev2',
                      'logfile' : 'IKEv2.log',
                      'allcase' : '1-4.3 5-6.2 6.4-14.8 14.10-18 20.1 21-22 24-38', # 6.3 14.9 19 20.2 is dieded
                      'engine'  : 'ikev2',  
                  },

    'IKEIPv6Main'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlikev6',
                      'logfile' : 'IKEIPv6Main.log',
                      'allcase' : '1-3.13 3.15-4.15 4.17-5.3 6-8.6 8.8-9.8 9.11-9.13 9.15-10 11.2 11.4-11.17 11.19-13 19-23', #3.14(WIND00409237), 4.16(WIND00359787), 9.14(WIND00409415) don't support on vxWorks.
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6CombinedSA'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlikev6_combined_sa',
                      'logfile' : 'IKEIPv6CombinedSA.log',
                      'allcase' : '2.20 9.9, 9.10, 11.1, 11.3, 11.18 14.6',
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6Aggressive'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlikev6_aggressive',
                      'logfile' : 'IKEIPv6Aggressive.log',
                      'allcase' : '14.1-14.16 14.18-15.13 15.15-18.17 18.20-18.26 18.28', #14.17,15.14 skipped for enhancement WIND00409237. 18.18 18.19 18.27 ANVL case bug.
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6md5'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserAllagash/anvlikev6_dh1_md5',
                      'logfile' : 'IKEIPv6md5.log',
                      'allcase' : '2.19 4.9 4.10 7.7 16.9 16.10 14.5 18.11',
                      'engine'  : 'ike-ipv6',
                  },
},

'fsl_p2020_rdb' : {

    'ICMPv4'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlicmp',
                      'logfile' : 'ICMPv4.log',
                      'allcase' : '',
                      'engine'  : 'icmp',
                  },

    'ICMPv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlicmpv6',
                      'logfile' : 'ICMPv6.log',
                      'allcase' : '1-4.4 4.6 4.7 4.9-5.9 5.11-10',
                      'engine'  : 'icmpv6',
                },

    'IPv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlip',
                      'logfile' : 'IPv4.log',
                      'allcase' : '',
                      'engine'  : 'ip',
                  },

    'IPv6FlowLevelEnable'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlipv6',
                      'logfile' : 'IPv6FlowLevelEnable.log',
                      'allcase' : '',
                      'engine'  : 'ipv6',
                  },

    'IPv6FlowLevelDisable'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlipv6_FlowLevelDisable',
                      'logfile' : 'IPv6FlowLevelDisable.log',
                      'allcase' : '7 11',
                      'engine'  : 'ipv6',
                  },

    'IPGW'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlipgw',
                      'logfile' : 'IPGW.log',
                      'allcase' : '1-2.8 3-5',  #2.9, 2.10 died on simics
                      'engine'  : 'ipgw',
                  },

    'IGMPv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvligmp',
                      'logfile' : 'IGMPv2.log',
                      'allcase' : '',
                      'engine'  : 'igmp'
                  },

    'IGMPv3'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvligmpv3',
                      'logfile' : 'IGMPv3.log',
                      'allcase' : '',
                      'engine'  : 'igmpv3',
                  },

    'Mldv1'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlmld',
                      'logfile' : 'Mldv1.log',
                      'allcase' : '',
                      'engine'  : 'ipv6-mld',
                  },

    'Mldv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlmldv2',
                      'logfile' : 'Mldv2.log',
                      'allcase' : '',
                      'engine'  : 'ipv6-mldv2',
                  },

    'DHCPC'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvldhcpclient',
                      'logfile' : 'DHCPC.log',
                      'allcase' : '',
                      'engine'  : 'dhcp-client',
                  },

    'DHCPS'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvldhcpserver',
                      'logfile' : 'DHCPS.log',
                      'allcase' : '',
                      'engine'  : 'dhcp-server',
                  },

    'RipPoison'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlrip',
                      'logfile' : 'RipPoison.log',
                      'allcase' : '1-15 17',
                      'engine'  : 'rip',
                  },

    'RipCompatibility'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlrip_Compatibility',
                      'logfile' : 'RipCompatibility.log',
                      'allcase' : '16',
                      'engine'  : 'rip',
                  },

    'RipSplitHorizon'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlrip_SplitHorizon',
                      'logfile' : 'RipSplitHorizon.log',
                      'allcase' : '8.17',
                      'engine'  : 'rip',
                  },

    'IPsecAHv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlipsecah',
                      'logfile' : 'IPsecAHv4.log',
                      'allcase' : '',
                      'engine'  : 'ipsec-ah',
                  },

    'IPsecAHv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlipsecv6ah',
                      'logfile' : 'IPsecAHv6.log',
                      'allcase' : '1-5.3 5.7-11 12.2-18', # 12.1 is pass, but ANVL cannot recognize the authenticated NeigbourAdvertise and hang. #case 17.* is nonexistent
                      'engine'  : 'ipsecv6-ah',
                  },

#    'IPsecAHv6_transport128'  : {        
#                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlipsecv6ah_transport128',
#                      'logfile' : 'IPsecAHv6_transport128.log',
#                      'allcase' : '5.6 12.1',  # 5.6, 12.1 are pass, but ANVL cannot recognize the authenticated NeigbourAdvertise and hang.
#                      'engine'  : 'ipsecv6-ah',
#                  },

    'IPsecESPv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlipsecesp',
                      'logfile' : 'IPsecESPv4.log', # 11.7 25.1 25.2 will hang. 11.2 11.4 11.6 11.7 11.9 11.10 cannot support by WIND00423259
                      'allcase' : '1-7.2 7.4 8 10 11.1 11.3 11.5 11.8 22-24 25.3-34',  # 7.3 cannot run on Simics',
                      'engine'  : 'ipsec-esp',
                 },

    'IPsecESPv4-noencry'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlipsecesp-noencry',
                      'logfile' : 'IPsecESPv4-noencry.log',
                      'allcase' : '8.4 8.6 22-23 26.7',
                      'engine'  : 'ipsec-esp',
                 },

    'IPsecESPv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlipsecv6esp',
                      'logfile' : 'IPsecESPv6.log',
                      'allcase' : '1-13 14.3 15-25',
                      'engine'  : 'ipsecv6-esp',
                  },

    'IPsecESPv6-des'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlipsecv6esp-des',
                      'logfile' : 'IPsecESPv6-des.log',
                      'allcase' : '5 7.5 7.7 9',
                      'engine'  : 'ipsecv6-esp',
                  },

    'IKEMain'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlike',
                      'logfile' : 'IKEMain.log',
                      'allcase' : '1-4 5.1-5.3 6-9.8',#simcis died in 9.11  and after 9.12-9.13 9.16-10 11.2 11.4-11.15 12-13 19-23
                      'engine'  : 'ike',
                  },

    'IKEAggressive'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlike_aggressive_resp',
                      'logfile' : 'IKEAggressive.log',
                      'allcase' : '14.1-14.16 14.18-18',#14.17 skipped for enhancement WIND00409237
                      'engine'  : 'ike',                      
                  },

    'IKECombinedSA'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlike_combined_sa',
                      'logfile' : 'IKECombinedSA.log',
                      'allcase' : '9.9, 9.10, 11.1, 11.3, 11.18',
                      'engine'  : 'ike',  
                  },

    'IKEDH1md5'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlike_dh1_md5',
                      'logfile' : 'IKEDH1md5.log',
                      'allcase' : '2.19, 4.9, 7.7, 14.5, 16.9, 18.11',
                      'engine'  : 'ike',  
                  },

    'IKEDH1sha'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlike_dh1_sha',
                      'logfile' : 'IKEDH1sha.log',
                      'allcase' : '2.20, 4.10, 14.6, 16.10',
                      'engine'  : 'ike',  
                  },

    'IKEv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlikev2',
                      'logfile' : 'IKEv2.log',
                      'allcase' : '1-6.2 6.4-14.8 14.10-18 20.1 21-22 24-38', # 6.3 14.9 19 20.2 is dieded
                      'engine'  : 'ikev2',  
                  },

    'IKEIPv6Main'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlikev6',
                      'logfile' : 'IKEIPv6Main.log',
                      'allcase' : '1-4.23 4.25-5.3 6-7.27 7.29-8.6 8.8-9.8 ', #4.24 7.28 9.11 and after 9.12-10 11.2 11.4-11.17 11.19-12.22 13 19-23 #12.23 died
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6CombinedSA'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlikev6_combined_sa',
                      'logfile' : 'IKEIPv6CombinedSA.log',
                      'allcase' : '2.20 9.9, 9.10, 11.1, 11.3, 11.18 14.6',
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6Aggressive'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlikev6_aggressive',
                      'logfile' : 'IKEIPv6Aggressive.log',
                      'allcase' : '14.1-14.16 14.18-15.13 15.15-18.17 18.20-18.26 18.28', #14.17,15.14 skipped for enhancement WIND00409237. 18.18 18.19 18.27 ANVL case bug. 
                      'engine'  : 'ike-ipv6', 
                  },

    'IKEIPv6md5'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlikev6_dh1_md5',
                      'logfile' : 'IKEIPv6md5.log',
                      'allcase' : '2.19 4.9 4.10 7.7 16.9 16.10 14.5 18.11',
                      'engine'  : 'ike-ipv6',
                  },                           
},


'bsp6x_fsl_p2020_rdb_6_9_0_0' : {

    'ICMPv4'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlicmp',
                      'logfile' : 'ICMPv4.log',
                      'allcase' : '',
                      'engine'  : 'icmp',
                  },

    'ICMPv6'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlicmpv6',
                      'logfile' : 'ICMPv6.log',
                      'allcase' : '1-4.4 4.6 4.7 4.9-5.9 5.11-10',
                      'engine'  : 'icmpv6',
                },

    'IPv4'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlip',
                      'logfile' : 'IPv4.log',
                      'allcase' : '',
                      'engine'  : 'ip',
                  },

    'IPv6FlowLevelEnable'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlipv6',
                      'logfile' : 'IPv6FlowLevelEnable.log',
                      'allcase' : '',
                      'engine'  : 'ipv6',
                  },

    'IPv6FlowLevelDisable'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlipv6_FlowLevelDisable',
                      'logfile' : 'IPv6FlowLevelDisable.log',
                      'allcase' : '7 11',
                      'engine'  : 'ipv6',
                  },

    'IPGW'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlipgw',
                      'logfile' : 'IPGW.log',
                      'allcase' : '1-2.8 3-5',  #2.9, 2.10 died on simics
                      'engine'  : 'ipgw',
                  },

    'IGMPv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvligmp',
                      'logfile' : 'IGMPv2.log',
                      'allcase' : '',
                      'engine'  : 'igmp',
                  },

    'IGMPv3'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvligmpv3',
                      'logfile' : 'IGMPv3.log',
                      'allcase' : '',
                      'engine'  : 'igmpv3',
                  },

    'Mldv1'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlmld',
                      'logfile' : 'Mldv1.log',
                      'allcase' : '',
                      'engine'  : 'ipv6-mld',
                  },

    'Mldv2'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlmldv2',
                      'logfile' : 'Mldv2.log',
                      'allcase' : '',
                      'engine'  : 'ipv6-mldv2',
                  },

    'DHCPC'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvldhcpclient',
                      'logfile' : 'DHCPC.log',
                      'allcase' : '',
                      'engine'  : 'dhcp-client',
                  },

    'DHCPS'  : {        
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvldhcpserver',
                      'logfile' : 'DHCPS.log',
                      'allcase' : '',
                      'engine'  : 'dhcp-server',
                  },

    'RipPoison'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlrip',
                      'logfile' : 'RipPoison.log',
                      'allcase' : '1-15 17',
                      'engine'  : 'rip',
                  },

    'RipCompatibility'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlrip_Compatibility',
                      'logfile' : 'RipCompatibility.log',
                      'allcase' : '16',
                      'engine'  : 'rip',
                  },

    'RipSplitHorizon'    : {
                      'cfg_prm_path' : '/opt/Ixia/IxANVL850update/ANVL-SRC/DocUserSIMICS/anvlrip_SplitHorizon',
                      'logfile' : 'RipSplitHorizon.log',
                      'allcase' : '8.17',
                      'engine'  : 'rip',
                  },

},

}
