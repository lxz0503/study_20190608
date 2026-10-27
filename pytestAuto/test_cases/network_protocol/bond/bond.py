#############################################################################
#
# Copyright (c) 2020 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

"IPNET BOND - IPNET NIC BONDING"

import os
import config
import time
import util
import subprocess
import pexpect
import socket
import re

first_nic = 'simnet1'
second_nic = 'simnet2'
bond_nic_v4addr = '1.1.1.100'
bond_nic_peer_v4addr = '1.1.1.200'
bond_nic_v6addr = '1::100'
bond_nic_peer_v6addr = '1::200'

################################################################################
#        bond_check_interface
################################################################################
def bond_check_interface(t, bondnic='', slavenic='', slave2nic=''):
    lines=t.send_and_return_all('ifconfig -a')
    
    if bondnic:
        for i in range(len(lines)):
            tokens = lines[i].split()
            if len(tokens) == 0:
                continue
            if tokens[0].find(bondnic) != -1:
                break
        else:
            return False
    
    if slavenic:
        for i in range(len(lines)):
            tokens = lines[i].split()
            if len(tokens) == 0:
                continue
            if tokens[0].find(slavenic) != -1:
                break
        else:
            return False
    
    if slave2nic:
        for i in range(len(lines)):
            tokens = lines[i].split()
            if len(tokens) == 0:
                continue
            if tokens[0].find(slave2nic) != -1:
                break
        else:
            return False
    
    return True

################################################################################
#        bond_check_slave_flag
################################################################################
def bond_check_slave_flag(t, interface):
    lines=t.send_and_return_all('ifconfig -a')
    for i in range(len(lines)):
        tokens = lines[i].split()
        if len(tokens) == 0:
            continue
        if tokens[0].find(interface) != -1:
            nextnextline = lines[i+2].split()
            for k in range(len(nextnextline)):
                if nextnextline[k].find('SLAVE') != -1:
                    return True
    else:
        return False


################################################################################
#        bond_check_bond_nic
################################################################################
def bond_check_bond_nic(t, mode, slaveifs):
    lines=t.send_and_return_all('ifconfig -a')
    for i in range(len(lines)):
        tokens = lines[i].split()
        if len(tokens) == 0:
            continue
        if tokens[0].find('bond0') != -1:
            if lines[i+1].find('Bondproto:' + mode + ' Slaveif:' + slaveifs) != -1:
                return True
    else:
        return False
        
################################################################################
#        bond_check_lagg_status
################################################################################
def bond_check_lagg_status(t, slaveif, state, mux_state, select_state):
    lines=t.send_and_return_all('C laggShow \"bond0\"')
    for i in range(len(lines)):
        if lines[i].strip() and lines[i].find(slaveif) != -1 and lines[i].find(state) != -1 \
            and lines[i].find(mux_state) != -1 and lines[i].find(select_state) != -1:
            return
    else:
        raise test_fail('%s expected: %s, %s, %s' % (slaveif, state, mux_state, select_state))

################################################################################
#        bond_check_active_status
################################################################################
def bond_check_active_status(t, slaveif, select_state):
    lines=t.send_and_return_all('C laggShow \"bond0\"')
    for i in range(len(lines)):
        if lines[i].strip() and lines[i].find(slaveif) != -1 and lines[i].find(select_state) != -1:
            return
    else:
        raise test_fail('%s expected: %s' % (slaveif, select_state))

class lacp_lb:
    "Successful and unsuccessful creation and configuration of LACP"
    def config(self):
        self.hosts = 2
        self.works_on_iplite = False
        self.works_on_lkm    = False
        self.works_on_gpp    = False

    def test(self, log, hosts, v6, __):
        t,s = hosts
        t.ping(s.ip().addr, count = 2, retries = 5)
        
        if bond_check_interface(t, slavenic = first_nic, slave2nic = second_nic) == False:
            raise test_fail('target 1 slave NICs are not exist')
        
        if bond_check_interface(s, slavenic = first_nic, slave2nic = second_nic) == False:
            raise test_fail('target 2 slave NICs are not exist')
                    
        t.send_and_wait_prompt('ifconfig bond0 create')
        t.send_and_wait_prompt('ifconfig bond0 bondproto lacp slaveif ' + first_nic + ' ' + second_nic)
        if v6:
            t.send_and_wait_prompt('ifconfig bond0 inet6 add ' + bond_nic_v6addr + ' up')
        else:
            t.send_and_wait_prompt('ifconfig bond0 ' + bond_nic_v4addr + ' up')
        if bond_check_interface(t, bondnic = 'bond0') == False:
            raise test_fail('target 1 bond0 is not exist')
        if bond_check_slave_flag(t, first_nic) == False:
            raise test_fail('target 1 ' + first_nic + ' flag SLAVE is not set')
        if bond_check_slave_flag(t, second_nic) == False:
            raise test_fail('target 1 ' + second_nic + ' flag SLAVE is not set')
        if bond_check_bond_nic(t, 'lacp', first_nic + ' ' + second_nic) == False:
            raise test_fail('target 1 bond0 NIC checking failed')
            
        s.send_and_wait_prompt('ifconfig bond0 create')
        s.send_and_wait_prompt('ifconfig bond0 bondproto lacp slaveif ' + first_nic + ' ' + second_nic)
        if v6:
            s.send_and_wait_prompt('ifconfig bond0 inet6 add ' + bond_nic_peer_v6addr + ' up')
        else:
            s.send_and_wait_prompt('ifconfig bond0 ' + bond_nic_peer_v4addr + ' up')
        if bond_check_interface(s, bondnic = 'bond0') == False:
            raise test_fail('target 2 bond0 is not exist')
        if bond_check_slave_flag(s, first_nic) == False:
            raise test_fail('target 1 ' + first_nic + ' flag SLAVE is not set')
        if bond_check_slave_flag(s, second_nic) == False:
            raise test_fail('target 1 ' + second_nic + ' flag SLAVE is not set')
        if bond_check_bond_nic(s, 'lacp', first_nic + ' ' + second_nic) == False:
            raise test_fail('target 1 bond0 NIC checking failed')
            
        t.send_and_wait_prompt('C laggdStart ' + ' \"bond0\"')
        s.send_and_wait_prompt('C laggdStart ' + ' \"bond0\"')
        
        # wait for LACP negotiation done
        time.sleep(10)
        
        bond_check_lagg_status(t, first_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        bond_check_lagg_status(t, second_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        bond_check_lagg_status(s, first_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        bond_check_lagg_status(s, second_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        
        if v6:
            t.ping(bond_nic_peer_v6addr, count = 2, retries = 5)
        else:
            t.ping(bond_nic_peer_v4addr, count = 2, retries = 5)

        #cleanup
        t.send_and_wait_prompt('C laggdStop ' + ' \"bond0\"')
        s.send_and_wait_prompt('C laggdStop ' + ' \"bond0\"')
        t.send_and_wait_prompt('ifconfig bond0 down')
        t.send_and_wait_prompt('ifconfig bond0 destroy')
        if bond_check_interface(t, bondnic = 'bond0') == True:
            raise test_fail('target 1 bond0 is still exist')
        s.send_and_wait_prompt('ifconfig bond0 down')
        s.send_and_wait_prompt('ifconfig bond0 destroy')
        if bond_check_interface(s, bondnic = 'bond0') == True:
            raise test_fail('target 2 bond0 is still exist')
        
        
class lacp_shutdown_slave:
    "test shutdown one slaveif"
    def config(self):
        self.hosts = 2
        self.works_on_iplite = False
        self.works_on_lkm    = False
        self.works_on_gpp    = False

    def test(self, log, hosts, v6, __):
        t,s = hosts
        t.ping(s.ip().addr, count = 2, retries = 5)
        
        if bond_check_interface(t, slavenic = first_nic, slave2nic = second_nic) == False:
            raise test_fail('target 1 slave NICs are not exist')
        
        if bond_check_interface(s, slavenic = first_nic, slave2nic = second_nic) == False:
            raise test_fail('target 2 slave NICs are not exist')
            
        t.send_and_wait_prompt('ifconfig bond0 create')
        t.send_and_wait_prompt('ifconfig bond0 bondproto lacp slaveif ' + first_nic + ' ' + second_nic)
        if v6:
            t.send_and_wait_prompt('ifconfig bond0 inet6 add ' + bond_nic_v6addr + ' up')
        else:
            t.send_and_wait_prompt('ifconfig bond0 ' + bond_nic_v4addr + ' up')
        if bond_check_interface(t, bondnic = 'bond0') == False:
            raise test_fail('target 1 bond0 is not exist')
        if bond_check_slave_flag(t, first_nic) == False:
            raise test_fail('target 1 ' + first_nic + ' flag SLAVE is not set')
        if bond_check_slave_flag(t, second_nic) == False:
            raise test_fail('target 1 ' + second_nic + ' flag SLAVE is not set')
        if bond_check_bond_nic(t, 'lacp', first_nic + ' ' + second_nic) == False:
            raise test_fail('target 1 bond0 NIC checking failed')
            
        s.send_and_wait_prompt('ifconfig bond0 create')
        s.send_and_wait_prompt('ifconfig bond0 bondproto lacp slaveif ' + first_nic + ' ' + second_nic)
        if v6:
            s.send_and_wait_prompt('ifconfig bond0 inet6 add ' + bond_nic_peer_v6addr + ' up')
        else:
            s.send_and_wait_prompt('ifconfig bond0 ' + bond_nic_peer_v4addr + ' up')
        if bond_check_interface(s, bondnic = 'bond0') == False:
            raise test_fail('target 2 bond0 is not exist')
        if bond_check_slave_flag(s, first_nic) == False:
            raise test_fail('target 1 ' + first_nic + ' flag SLAVE is not set')
        if bond_check_slave_flag(s, second_nic) == False:
            raise test_fail('target 1 ' + second_nic + ' flag SLAVE is not set')
        if bond_check_bond_nic(s, 'lacp', first_nic + ' ' + second_nic) == False:
            raise test_fail('target 1 bond0 NIC checking failed')
            
        t.send_and_wait_prompt('C laggdStart ' + ' \"bond0\"')
        s.send_and_wait_prompt('C laggdStart ' + ' \"bond0\"')
        
        # wait for LACP negotiation done
        time.sleep(10)
        
        bond_check_lagg_status(t, first_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        bond_check_lagg_status(t, second_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        bond_check_lagg_status(s, first_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        bond_check_lagg_status(s, second_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        
        if v6:
            t.ping(bond_nic_peer_v6addr, count = 2, retries = 5)
        else:
            t.ping(bond_nic_peer_v4addr, count = 2, retries = 5)
        
        # shutdown first nic
        t.send_and_wait_prompt('ifconfig ' + first_nic + ' down')
        # wait for MII report link status
        time.sleep(20)
        bond_check_lagg_status(t, first_nic, 'ABG', 'DETACHED', 'UNSELECTED')
        bond_check_lagg_status(t, second_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        bond_check_lagg_status(s, first_nic, 'ABCG', 'DETACHED', 'UNSELECTED')
        bond_check_lagg_status(s, second_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        
        if v6:
            t.ping(bond_nic_peer_v6addr, count = 2, retries = 5)
        else:
            t.ping(bond_nic_peer_v4addr, count = 2, retries = 5)
        
        # shutdown all nic
        t.send_and_wait_prompt('ifconfig ' + second_nic + ' down')
        # wait for MII report link status
        time.sleep(20)
        bond_check_lagg_status(t, first_nic, 'ABG', 'DETACHED', 'UNSELECTED')
        bond_check_lagg_status(t, second_nic, 'ABG', 'DETACHED', 'UNSELECTED')
        bond_check_lagg_status(s, first_nic, 'ABCDEFG', 'DISTRIBUT', 'SELECTED')
        bond_check_lagg_status(s, second_nic, 'ABCG', 'DETACHED', 'UNSELECTED')
        
        if v6:
            t.ping(bond_nic_peer_v6addr, succeed=False, count = 2, retries = 5)
        else:
            t.ping(bond_nic_peer_v4addr, succeed=False, count = 2, retries = 5)
            
        # up second nic
        t.send_and_wait_prompt('ifconfig ' + second_nic + ' up')
        # wait for MII report link status
        time.sleep(20)
        bond_check_lagg_status(t, first_nic, 'ABG', 'DETACHED', 'UNSELECTED')
        bond_check_lagg_status(t, second_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        bond_check_lagg_status(s, first_nic, 'ABCG', 'DETACHED', 'UNSELECTED')
        bond_check_lagg_status(s, second_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        
        if v6:
            t.ping(bond_nic_peer_v6addr, count = 2, retries = 5)
        else:
            t.ping(bond_nic_peer_v4addr, count = 2, retries = 5)
           
        # up all nic
        t.send_and_wait_prompt('ifconfig ' + first_nic + ' up')
        # wait for MII report link status
        time.sleep(20)
        bond_check_lagg_status(t, first_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        bond_check_lagg_status(t, second_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        bond_check_lagg_status(s, first_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        bond_check_lagg_status(s, second_nic, 'ABCDEF', 'DISTRIBUT', 'SELECTED')
        
        if v6:
            t.ping(bond_nic_peer_v6addr, count = 2, retries = 5)
        else:
            t.ping(bond_nic_peer_v4addr, count = 2, retries = 5)
        
        #cleanup
        t.send_and_wait_prompt('C laggdStop ' + ' \"bond0\"')
        s.send_and_wait_prompt('C laggdStop ' + ' \"bond0\"')
        t.send_and_wait_prompt('ifconfig bond0 down')
        t.send_and_wait_prompt('ifconfig bond0 destroy')
        if bond_check_interface(t, bondnic = 'bond0') == True:
            raise test_fail('target 1 bond0 is still exist')
        s.send_and_wait_prompt('ifconfig bond0 down')
        s.send_and_wait_prompt('ifconfig bond0 destroy')
        if bond_check_interface(s, bondnic = 'bond0') == True:
            raise test_fail('target 2 bond0 is still exist')
        
        

class lacp_default_slave:
    "test use the first default slaveif"
    def config(self):
        self.hosts = 2
        self.works_on_iplite = False
        self.works_on_lkm    = False
        self.works_on_gpp    = False

    def test(self, log, hosts, v6, __):
        t,s = hosts
        t.ping(s.ip().addr, count = 2, retries = 5)
        
        if bond_check_interface(t, slavenic = first_nic, slave2nic = second_nic) == False:
            raise test_fail('target 1 slave NICs are not exist')
        
        if bond_check_interface(s, slavenic = first_nic, slave2nic = second_nic) == False:
            raise test_fail('target 2 slave NICs are not exist')
            
        t.send_and_wait_prompt('ifconfig bond0 create')
        t.send_and_wait_prompt('ifconfig bond0 bondproto lacp slaveif ' + first_nic + ' ' + second_nic)
        if v6:
            t.send_and_wait_prompt('ifconfig bond0 inet6 add ' + bond_nic_v6addr + ' up')
        else:
            t.send_and_wait_prompt('ifconfig bond0 ' + bond_nic_v4addr + ' up')
        if bond_check_interface(t, bondnic = 'bond0') == False:
            raise test_fail('target 1 bond0 is not exist')
        if bond_check_slave_flag(t, first_nic) == False:
            raise test_fail('target 1 ' + first_nic + ' flag SLAVE is not set')
        if bond_check_slave_flag(t, second_nic) == False:
            raise test_fail('target 1 ' + second_nic + ' flag SLAVE is not set')
        if bond_check_bond_nic(t, 'lacp', first_nic + ' ' + second_nic) == False:
            raise test_fail('target 1 bond0 NIC checking failed')
            
        # target 2 don't enable BOND and use real physical NIC
        if v6:
            s.send_and_wait_prompt('ifconfig ' + first_nic + ' inet6 add ' + bond_nic_peer_v6addr + ' up')
        else:
            s.send_and_wait_prompt('ifconfig ' + first_nic + ' inet add ' + bond_nic_peer_v4addr + ' up')
            
        t.send_and_wait_prompt('C laggdStart ' + ' \"bond0\"')
        
        # wait for LACP negotiation done
        time.sleep(10)
        
        # check default flag in first nic
        bond_check_lagg_status(t, first_nic, 'ABCDEFG', 'DISTRIBUT', 'SELECTED')
        bond_check_lagg_status(t, second_nic, 'ABCG', 'DETACHED', 'UNSELECTED')

        if v6:
            t.ping(bond_nic_peer_v6addr, count = 2, retries = 5)
        else:
            t.ping(bond_nic_peer_v4addr, count = 2, retries = 5)
        
        #cleanup
        t.send_and_wait_prompt('C laggdStop ' + ' \"bond0\"')
        t.send_and_wait_prompt('ifconfig bond0 down')
        t.send_and_wait_prompt('ifconfig bond0 destroy')
        if bond_check_interface(t, bondnic = 'bond0') == True:
            raise test_fail('target 1 bond0 is still exist')
        
        if v6:
            s.send_and_wait_prompt('ifconfig ' + first_nic + ' inet6 del ' + bond_nic_peer_v6addr)
        else:
            s.send_and_wait_prompt('ifconfig ' + first_nic + ' inet del ' + bond_nic_peer_v4addr)

class ipnet_bond_configure:
    "test bond interface configuration and delete"
    def config(self):
        self.hosts = 1
        self.works_on_iplite = False
        self.invalid_nic     = " simerr"
        self.works_on_lkm    = False
        self.works_on_gpp    = False

    def test(self, log, hosts, v6, __):
        t = hosts

        if bond_check_interface(t, slavenic = first_nic, slave2nic = second_nic) == False:
            raise test_fail('target 1 slave NICs are not exist')

        t.send_and_wait_prompt('ifconfig bond0 create')
        t.send('ifconfig bond0 bondproto failover slaveif')
        t.expect_exact_and_wait_prompt('ifconfig: miss slaveif configuration')
        t.send('ifconfig bond0 bondproto failover slaveif ' + first_nic + self.invalid_nic)
        t.expect_re_and_wait_prompt('Setting bond parameters')
        if bond_check_slave_flag(t, first_nic) == True:
            raise test_fail('target 1 ' + first_nic + ' flag SLAVE have set')
        t.send_and_wait_prompt('ifconfig bond0 bondproto failover slaveif ' + first_nic + ' ' + second_nic) 
        if bond_check_slave_flag(t, first_nic) == False:
            raise test_fail('target 1 ' + first_nic + ' flag SLAVE have set')
        if bond_check_slave_flag(t, second_nic) == False:
            raise test_fail('target 1 ' + second_nic + ' flag SLAVE have set')
        if v6:
            t.send_and_wait_prompt('ifconfig bond0 inet6 add ' + bond_nic_peer_v6addr + ' up')
        else:
            t.send_and_wait_prompt('ifconfig bond0 ' + bond_nic_peer_v4addr + ' up')

        t.send('C laggdStart ' + ' \"bond0\"')
        t.expect_re_and_wait_prompt('value = 0' + "*?")

        t.send('C laggdStop ' + ' \"bond0\"')
        t.expect_re_and_wait_prompt('value = 0' + "*?")
        t.send('ifconfig bond0 destroy')
        t.expect_re_and_wait_prompt('Destroying' + "*?")
        t.send_and_wait_prompt('ifconfig bond0 down')
        t.send_and_wait_prompt('ifconfig bond0 destroy')

        if bond_check_slave_flag(t, first_nic) == True:
            raise test_fail('target 1 ' + first_nic + ' flag SLAVE have set')
        if bond_check_slave_flag(t, second_nic) == True:
            raise test_fail('target 1 ' + second_nic + ' flag SLAVE have set')
        t.send('ifconfig ' + ' \"bond0\"')
        t.expect_re_and_wait_prompt('not found')

class ipnet_bond_failover_mode:
    "test bond interface failover mode"
    def config(self):
        self.hosts = 2
        self.works_on_iplite = False
        self.works_on_lkm    = False
        self.works_on_gpp    = False

    def test(self, log, hosts, v6, __):
        t,s = hosts
        t.ping(s.ip().addr, count = 2, retries = 5)
        
        if bond_check_interface(t, slavenic = first_nic, slave2nic = second_nic) == False:
            raise test_fail('target 1 slave NICs are not exist')

        if bond_check_interface(s, slavenic = first_nic, slave2nic = second_nic) == False:
            raise test_fail('target 2 slave NICs are not exist')

        t.send_and_wait_prompt('ifconfig bond0 create')
        t.send_and_wait_prompt('ifconfig bond0 bondproto failover slaveif ' + first_nic + ' ' + second_nic) 
        if bond_check_slave_flag(t, first_nic) == False:
            raise test_fail('target 1 ' + first_nic + ' flag SLAVE have set')
        if bond_check_slave_flag(t, second_nic) == False:
            raise test_fail('target 1 ' + second_nic + ' flag SLAVE have set')
        if v6:
            t.send_and_wait_prompt('ifconfig bond0 inet6 add ' + bond_nic_v6addr + ' up')
        else:
            t.send_and_wait_prompt('ifconfig bond0 ' + bond_nic_v4addr + ' up')
        t.send('C laggdStart ' + ' \"bond0\"')
        t.expect_re_and_wait_prompt('value = 0' + "*?")

        s.send_and_wait_prompt('ifconfig bond0 create')
        s.send_and_wait_prompt('ifconfig bond0 bondproto failover slaveif ' + first_nic + ' ' + second_nic) 
        if bond_check_slave_flag(t, first_nic) == False:
            raise test_fail('target 1 ' + first_nic + ' flag SLAVE have set')
        if bond_check_slave_flag(t, second_nic) == False:
            raise test_fail('target 1 ' + second_nic + ' flag SLAVE have set')
        if v6:
            s.send_and_wait_prompt('ifconfig bond0 inet6 add ' + bond_nic_peer_v6addr + ' up')
        else:
            s.send_and_wait_prompt('ifconfig bond0 inet ' + bond_nic_peer_v4addr + ' up')
        s.send('C laggdStart ' + ' \"bond0\"')
        s.expect_re_and_wait_prompt('value = 0' + "*?")

        bond_check_active_status(t, first_nic, "Selected")
        bond_check_active_status(s, first_nic, "Selected")

        if v6:
            t.ping(bond_nic_peer_v6addr, count = 2, retries = 5)
        else:
            t.ping(bond_nic_peer_v4addr, count = 2, retries = 5)

        t.send_and_wait_prompt('ifconfig ' + first_nic + ' down')
        s.send_and_wait_prompt('ifconfig ' + first_nic + ' down')

        time.sleep(2)

        bond_check_active_status(t, second_nic, "Selected")
        bond_check_active_status(s, second_nic, "Selected")
        
        if v6:
            t.ping(bond_nic_peer_v6addr, count = 2, retries = 5)
        else:
            t.ping(bond_nic_peer_v4addr, count = 2, retries = 5)

        t.send_and_wait_prompt('ifconfig ' + first_nic + ' up')
        s.send_and_wait_prompt('ifconfig ' + first_nic + ' up')
        t.send_and_wait_prompt('C laggdStop ' + ' \"bond0\"')
        s.send_and_wait_prompt('C laggdStop ' + ' \"bond0\"')
        t.send_and_wait_prompt('ifconfig bond0 down')
        t.send_and_wait_prompt('ifconfig bond0 destroy')
        s.send_and_wait_prompt('ifconfig bond0 down')
        s.send_and_wait_prompt('ifconfig bond0 destroy')
        

class ipnet_bond_loadbalance_mode:
    "test bond interface loadbalance mode"
    def config(self):
        self.hosts = 2
        self.works_on_iplite = False
        self.works_on_lkm    = False
        self.works_on_gpp    = False

    def test(self, log, hosts, v6, __):
        t,s = hosts
        t.ping(s.ip().addr, count = 2, retries = 5)
        
        if bond_check_interface(t, slavenic = first_nic, slave2nic = second_nic) == False:
            raise test_fail('target 1 slave NICs are not exist')
        
        if bond_check_interface(s, slavenic = first_nic, slave2nic = second_nic) == False:
            raise test_fail('target 2 slave NICs are not exist')
            
        t.send_and_wait_prompt('ifconfig bond0 create')
        t.send_and_wait_prompt('ifconfig bond0 bondproto loadbalance slaveif ' + first_nic + ' ' + second_nic) 
        if bond_check_slave_flag(t, first_nic) == False:
            raise test_fail('target 1 ' + first_nic + ' flag SLAVE have set')
        if bond_check_slave_flag(t, second_nic) == False:
            raise test_fail('target 1 ' + second_nic + ' flag SLAVE have set')
        if v6:
            t.send_and_wait_prompt('ifconfig bond0 inet6 add ' + bond_nic_v6addr + ' up')
        else:
            t.send_and_wait_prompt('ifconfig bond0 inet ' + bond_nic_v4addr + ' up')
        t.send('C laggdStart ' + ' \"bond0\"')
        t.expect_re_and_wait_prompt('value = 0' + "*?")

        s.send_and_wait_prompt('ifconfig bond0 create')
        s.send_and_wait_prompt('ifconfig bond0 bondproto loadbalance slaveif ' + first_nic + ' ' + second_nic) 
        if bond_check_slave_flag(t, first_nic) == False:
            raise test_fail('target 1 ' + first_nic + ' flag SLAVE have set')
        if bond_check_slave_flag(t, second_nic) == False:
            raise test_fail('target 1 ' + second_nic + ' flag SLAVE have set')
        if v6:
            s.send_and_wait_prompt('ifconfig bond0 inet6 add ' + bond_nic_peer_v6addr + ' up')
        else:
            s.send_and_wait_prompt('ifconfig bond0 ' + bond_nic_peer_v4addr + ' up')
        s.send('C laggdStart ' + ' \"bond0\"')
        s.expect_re_and_wait_prompt('value = 0' + "*?")

        bond_check_active_status(t, first_nic, "Selected")
        bond_check_active_status(t, second_nic, "Selected")
        bond_check_active_status(s, first_nic, "Selected")
        bond_check_active_status(s, second_nic, "Selected")

        if v6:
            t.ping(bond_nic_peer_v6addr, count = 2, retries = 5)
        else:
            t.ping(bond_nic_peer_v4addr, count = 2, retries = 5)

        t.send_and_wait_prompt('ifconfig ' + first_nic + ' down')
        s.send_and_wait_prompt('ifconfig ' + first_nic + ' down')

        time.sleep(2)

        bond_check_active_status(t, first_nic, "Unselected")
        bond_check_active_status(t, second_nic, "Selected")
        bond_check_active_status(s, first_nic, "Unselected")
        bond_check_active_status(s, second_nic, "Selected")

        if v6:
            t.ping(bond_nic_peer_v6addr, count = 2, retries = 5)
        else:
            t.ping(bond_nic_peer_v4addr, count = 2, retries = 5)

        t.send_and_wait_prompt('ifconfig ' + first_nic + ' up')
        s.send_and_wait_prompt('ifconfig ' + first_nic + ' up')
        t.send_and_wait_prompt('ifconfig ' + second_nic + ' down')
        s.send_and_wait_prompt('ifconfig ' + second_nic + ' down') 

        time.sleep(2)

        bond_check_active_status(t, first_nic, "Selected")
        bond_check_active_status(t, second_nic, "Unselected")
        bond_check_active_status(s, first_nic, "Selected")
        bond_check_active_status(s, second_nic, "Unselected")

        if v6:
            t.ping(bond_nic_peer_v6addr, count = 2, retries = 5)
        else:
            t.ping(bond_nic_peer_v4addr, count = 2, retries = 5)

        t.send_and_wait_prompt('ifconfig ' + second_nic + ' up')
        s.send_and_wait_prompt('ifconfig ' + second_nic + ' up')
        t.send_and_wait_prompt('C laggdStop ' + ' \"bond0\"')
        s.send_and_wait_prompt('C laggdStop ' + ' \"bond0\"')
        t.send_and_wait_prompt('ifconfig bond0 down')
        t.send_and_wait_prompt('ifconfig bond0 destroy')
        s.send_and_wait_prompt('ifconfig bond0 down')
        s.send_and_wait_prompt('ifconfig bond0 destroy')
