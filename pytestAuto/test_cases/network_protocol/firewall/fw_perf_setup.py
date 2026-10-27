#!/usr/bin/env python
#############################################################################
#
# Copyright (c) 2006-2013 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################


import pexpect
import sys

# INSTRUCTIONS FOR FIREWALL PERFORMANCE MEASUREMENTS
# =================================================
#
#
#               NETWORK SETUP
#
#   smartbits                                smartbits
#   port1                                     port2
#   -----                                     -----
#   |   |_                                   _|   |
#   |   | |                                 | |   |
#   ----- |                                 | -----
#         |                                 |
#         |              target             |
#         | secondary_if ----- primary_if   |
#         |______________|   |______________|
#         |              |   |              |
#         |              -----              |
#   linux |                                 | linux
#   host1 |                                 | host2
#   ----- |                                 | -----
#   |   |_|                                 |_|   |
#   |   |                                     |   |
#   -----                                     -----
#     |                                         |
#     |            linux                        |
#     |            host3                        |
#     |            -----                        |
#     |            |   |                        |
#     |            |   |                        |
#     |            -----                        |
#     |              |                          |
#     |______________|__________________________|
#             CORPORATE LAN
#
#
#      Run the script from linux host 3
#      Use linux host 1 or 2 as a gateway to reach target
#
#
# 1. Rebuild libraries. Set everything to false in config.mk except:
#    COMPONENT_IPNET = true
#    COMPONENT_IPFIREWALL = true
#
#    Build command: make CPU=PPC32 TOOL=sfdiab FEATURE_SET=pne TARGET=rclean
#                   make CPU=PPC32 TOOL=sfdiab FEATURE_SET=pne
#
#    Modify the following files before build:
#    - components/ip_net2-6.5/ipcom/port/vxworks/config/ipcom_pconfig.h:
#      Disable WV_INSTRUMENTATION: /* #define IPCOM_WV_INSTRUMENTATION */
#
#    - components/ip_net2-6.5/ipnet2/config/ipnet_config.h:
#      Disable NAT: /* #define IPNET_USE_NAT */
#      Increase forwarding cache size: #define IPNET_IPV4_FORWARD_CACHE_ORDER 15
#                                      #define IPNET_IPV6_FORWARD_CACHE_ORDER 15
#
#    - components/ip_net2-6.5/ipfirewall/config/ipfirewall_config.h:
#      Disable MAC_FILTER: /* #define IPFIREWALL_USE_MAC_FILTER */
#
# 2. Create a VxWorks image project and build an image.
#    Use the default kernel config but enable:
#    - telnet server
#    - ifconfig cmd
#
# 3. Reboot targets with the newly built image run this setup script from linux host 3.
#
# 4. Run the Spirent SmartApplications program. Use the firewall.sig config file
#    and execute the throughput test.
#
# 5. Await the results and paste into the spreadsheet (firewall_perf.xls)
#
# 6. Re-run this script with a new setting of "number of rules",
#    and repeat from step 4.
#

netmask         = '255.255.255.0'
primary_ip      = '192.168.2.90'
primary_if      = 'mottsec1'
secondary_ip    = '192.168.1.90'
secondary_if    = 'mottsec0'

telnet_port     = 23
cprompt         = '-> '
cmdprompt       = '\[vxWorks\]# '


def main(argv):

    if len(argv) < 1:
        print 'Usage: ./fw_perf_setup.py <number_of_rules>'
        return

    num_rules = argv[0]
    print num_rules

    # login to target
    s = pexpect.spawn('telnet %s %d' % (primary_ip, telnet_port))
    s.logfile = sys.stdout
    s.expect(cprompt)
    s.sendline('ipcom_drv_eth_ip_attach "%s", "%s"' % (secondary_if, secondary_if))
    s.expect(cprompt)
    s.sendline('cmd')
    s.expect(cmdprompt)
    s.sendline('ifconfig %s up' % (secondary_if))
    s.expect(cmdprompt)
    s.sendline('ifconfig %s inet %s netmask %s' % (secondary_if, secondary_ip, netmask))
    s.expect(cmdprompt)
    s.sendline('ifconfig -a')
    s.expect(cmdprompt)

    s.sendline('ipf -Fr')
    s.expect(cmdprompt)

    # setup firewall
    for c in range(int(num_rules)):
        s.sendline('ipf block in quick from 11.1.1.%d to any' % (c+1))
        s.expect(cmdprompt)

    s.sendline('ipf -Pr')
    s.expect(cmdprompt)

    # logout from target1
    s.sendline('exit')
    s.expect(pexpect.EOF)

if __name__ == '__main__':
    main(sys.argv[1:])
