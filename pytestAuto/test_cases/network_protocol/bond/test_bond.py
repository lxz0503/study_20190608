#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:2/20/2024 10:40 AM
@file:test_bond.py
"""
import allure
import pytest
import sys


from utils.log_record import log
from test_cases.network_protocol.bond.boot_qemu import BootQemu

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
    lines = t.sendAndReturnAll('ifconfig -a', BootQemu.vxprompt)

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
    lines = t.sendAndReturnAll('ifconfig -a', BootQemu.vxprompt)
    for i in range(len(lines)):
        tokens = lines[i].split()
        if len(tokens) == 0:
            continue
        if tokens[0].find(interface) != -1:
            nextnextline = lines[i + 2].split()
            for k in range(len(nextnextline)):
                if nextnextline[k].find('SLAVE') != -1:
                    return True
    else:
        return False


################################################################################
#        bond_check_bond_nic
################################################################################
def bond_check_bond_nic(t, mode, slaveifs):
    lines = t.sendAndReturnAll('ifconfig -a', BootQemu.vxprompt)
    for i in range(len(lines)):
        tokens = lines[i].split()
        if len(tokens) == 0:
            continue
        if tokens[0].find('bond0') != -1:
            if lines[i + 1].find('Bondproto:' + mode + ' Slaveif:' + slaveifs) != -1:
                return True
    else:
        return False


################################################################################
#        bond_check_lagg_status
################################################################################
def bond_check_lagg_status(t, slaveif, state, mux_state, select_state):
    lines = t.sendAndReturnAll('C laggShow \"bond0\"', BootQemu.vxprompt)
    for i in range(len(lines)):
        if lines[i].strip() and lines[i].find(slaveif) != -1 and lines[i].find(state) != -1 \
                and lines[i].find(mux_state) != -1 and lines[i].find(select_state) != -1:
            return
    else:  # xiaozhan, modify
        log.error('%s expected: %s, %s, %s' % (slaveif, state, mux_state, select_state))
        assert False


################################################################################
#        bond_check_active_status
################################################################################
def bond_check_active_status(t, slaveif, select_state):
    lines = t.sendAndReturnAll('C laggShow \"bond0\"', BootQemu.vxprompt)
    for i in range(len(lines)):
        if lines[i].strip() and lines[i].find(slaveif) != -1 and lines[i].find(select_state) != -1:
            return
    else:  # xiaozhan, modify
        log.error('%s expected: %s' % (slaveif, select_state))
        assert False


class TestBond(BootQemu):

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_ipnet_bond_configure(self, version):
        """test bond interface configuration and delete"""
        self.invalid_nic = " simerr"

        # old KONG case
        t = self.t1

        if not bond_check_interface(t, slavenic=first_nic, slave2nic=second_nic):
            log.error('target 1 slave NICs do not exist')
            assert False

        t.sendAndExpect('ifconfig bond0 create', self.vxprompt)
        ret = t.sendAndReturnAll('ifconfig bond0 bondproto failover slaveif', self.vxprompt)
        print(f'debug===={ret}====')
        assert 'ifconfig: miss slaveif configuration' in ret

        cmd = 'ifconfig bond0 bondproto failover slaveif ' + first_nic + self.invalid_nic
        ret = t.sendAndReturnAll(cmd, self.vxprompt)
        assert 'Setting bond parameters' in ret
        if bond_check_slave_flag(t, first_nic):
            log.error('target 1 ' + first_nic + ' flag SLAVE have set')
            assert False

        cmd = 'ifconfig bond0 bondproto failover slaveif ' + first_nic + ' ' + second_nic
        t.sendAndExpect(cmd, self.vxprompt)

        if not bond_check_slave_flag(t, first_nic):
            log.error('target 1 ' + first_nic + ' flag SLAVE have set')
            assert False

        if not bond_check_slave_flag(t, second_nic):
            log.error('target 1 ' + second_nic + ' flag SLAVE have set')
            assert False

        if version == 'v6':
            t.sendAndExpect('ifconfig bond0 inet6 add ' + bond_nic_peer_v6addr + ' up', self.vxprompt)
        else:
            t.sendAndExpect('ifconfig bond0 ' + bond_nic_peer_v4addr + ' up', self.vxprompt)

        ret = t.sendAndReturnAll('C laggdStart ' + ' \"bond0\"', self.vxprompt)
        assert 'value = 0' in ret

        ret = t.sendAndReturnAll('C laggdStop ' + ' \"bond0\"', self.vxprompt)
        assert 'value = 0' in ret

        ret = t.sendAndReturnAll('ifconfig bond0 destroy', self.vxprompt)
        assert 'Destroying' in ret

        t.sendAndExpect('ifconfig bond0 down', self.vxprompt)
        t.sendAndExpect('ifconfig bond0 destroy', self.vxprompt)

        if bond_check_slave_flag(t, first_nic):
            log.error('target 1 ' + first_nic + ' flag SLAVE have set')
            assert False

        if bond_check_slave_flag(t, second_nic):
            log.error('target 1 ' + second_nic + ' flag SLAVE have set')
            assert False

        ret = t.sendAndReturnAll('ifconfig ' + ' \"bond0\"', self.vxprompt)
        assert 'not found' in ret


if __name__ == "__main__":
    pass
