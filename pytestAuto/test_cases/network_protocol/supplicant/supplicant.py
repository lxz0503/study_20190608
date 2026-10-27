#############################################################################
#
# Copyright (c) 2020-2021 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

#

# Supplicant tests
#   This is just to test basic supplicant Supplicant command. Complete function test need
#   setup the physical environment following 802.1x standard which include besides vxWorks:
#       1) A Switch as Authenticator 
#       2) A Radius Server as Authentication Server 
#


import time
import re
import pdb

###############################################################################
# DATA
###############################################################################


###############################################################################
# Common utility functions
###############################################################################


################################################################################
# supplicant cmd test
################################################################################
class cmd:
    'Test supplicant cmd'
    def config(self):
        self.hosts = 1
        self.eta = 9
        self.v4 = True
        self.v6 = False 
        self.works_on_iplite = False

    def test(self, log, hosts, v6, __):
        a = self.t1

        a.set_sysvar("ip8021x.if_name", "simtest-eth0-loopback")

        a.send(a.las_prefix() + 'ipd kill ip8021x')
        a.expect_exact_and_wait_prompt('ipd: kill ip8021x ok')

        a.send(a.las_prefix() + 'ipd start ip8021x')
        a.expect_exact_and_wait_prompt('ipd: start ip8021x ok')

        a.send(a.las_prefix() + 'supplicant list')
        a.expect_exact_and_wait_prompt('suppId = 0, interface = simtest-eth0-loopback, INITIALIZED')

        a.send(a.las_prefix() + 'supplicant delete 0')
        a.wait_prompt()

        a.send(a.las_prefix() + 'supplicant add')
        a.wait_prompt()

        a.send(a.las_prefix() + 'ipd reconfigure ip8021x')
        a.expect_exact_and_wait_prompt('ipd: reconfigure ip8021x ok')

        a.send(a.las_prefix() + 'supplicant list')
        a.expect_exact_and_wait_prompt('suppId = 0, interface = simtest-eth0-loopback, INITIALIZED')

        a.send(a.las_prefix() + 'supplicant connect 0')
        a.wait_prompt()

        a.send(a.las_prefix() + 'supplicant getstatus 0;\n')
        a.expect_exact_and_wait_prompt('SM state = CONNECTING')

        a.send(a.las_prefix() + 'supplicant disconnect 0')
        a.wait_prompt()

        a.send(a.las_prefix() + 'supplicant getstatus 0;\n')
        a.expect_exact_and_wait_prompt('SM state = DISCONNECTED')

        a.send(a.las_prefix() + 'supplicant logoff 0')
        a.wait_prompt()

        a.send(a.las_prefix() + 'supplicant getstatus 0;\n')
        a.expect_exact_and_wait_prompt('SM state = DISCONNECTED')

###############################################################################
# END OF FILE
###############################################################################
