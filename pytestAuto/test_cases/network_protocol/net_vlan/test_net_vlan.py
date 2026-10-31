#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/23/2024 4:30 PM
@file:test_ntp.py
"""
import allure
import pytest
import sys


from utils.log_record import log
from utils.case_record import record_result, record_result_expect
from utils.ezTargets import QemuTarget, VxWorksImage, LinuxImage


class NetworkInterface(object):
    def __init__(self, session, name):
        self.session = session
        self.name = name
        self.vr = 0

    def get_name(self):
        return self.name

    def up(self):
        return self.invoke_cmd('up')

    def down(self):
        return self.invoke_cmd('down')

    def set_vr(self, vr):
        if self.invoke_cmd('vr %d' % vr):
            self.vr = vr
            return True
        return False

    def get_vr(self):
        return self.vr

    def invoke_cmd(self, cmd, prompt='# '):  # xiaozhan, add prompt for vx
        cmd = 'ifconfig -V %d %s %s' % (self.vr, self.name, cmd)
        lines = self.session.sendAndReturnAll(cmd, prompt)  # xiaozhan, modify
        if len(lines) > 0:
            return False
        return True

    def invoke_ip_cmd(self, cmd, prompt='# '):  # xiaozhan, add prompt for vx
        cmd = 'ip -V %d link %s' % (self.vr, cmd)
        lines = self.session.sendAndReturnAll(cmd, prompt)
        if len(lines) > 0:
            return False
        return True


class Ethernet(NetworkInterface):
    pass


class Vlan(NetworkInterface):
    def __init__(self, session, name):
        super().__init__(session, name)
        self.is_created = False

    def cleanup(self):
        self.down()
        self.destroy()

    def create(self):
        return self.invoke_cmd('create')

    def destroy(self):
        return self.invoke_cmd('destroy')

    def set_tag_parent_if(self, tag, parent_eth):
        return self.invoke_cmd('vlan %d vlanif %s#%d' %
                               (tag, parent_eth.get_name(), parent_eth.get_vr()))

    def show(self):
        return self.invoke_cmd('')

    def mtu(self):
        return self.invoke_cmd('mtu 1400')

    def lladdr(self):
        return self.invoke_cmd("lladdr 00:00:00:00:00:05")

    def promisc(self):
        return self.invoke_cmd("promisc")

    def clrpromisc(self):
        return self.invoke_cmd("-promisc")

    def add(self, tag):
        return self.invoke_ip_cmd('add %s link eth0 type vlan id %d' % (self.name, tag))

    def delete(self):
        return self.invoke_ip_cmd('delete %s' % self.name)

    def ipshow(self):
        return self.invoke_ip_cmd('show dev %s' % self.name)


class TestNetVlan(object):
    def setup_class(self):
        # different test suite has different path
        self.image_path = '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-vlan/vxWorks'
        self.vxprompt = '# '
        self.result = []
        self.pass_num = self.fail_num = 0
        self.module = 'ipnet.vlan'
        # set up network on qemu
        vximage = VxWorksImage(self.image_path, debug=False)
        self.vx_targets = [QemuTarget('QEMU-Q35-%s' % x, logFile='qemu%s.log' % x) for x in range(1, 2)]
        [x.boot(vximage) for x in self.vx_targets]

        # qemu VxWorks
        self.t1 = self.vx_targets[0]
        # config ipv6 for each qemu vxworks
        self.t1.sendAndExpect('cmd', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet6 add 2000::10 prefixlen 64 up', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet add 10.236.1.10 prefixlen 24 up', self.vxprompt)
        self.t1_ip, self.t1_ip6 = self.t1.get_ip()

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_create_and_configure(self, version):
        with allure.step('Successful and unsuccessful creation and configuration of VLAN interface'):
            t = self.t1
            name = 'create_and_configure'
            case_name = self.module + '.' + name + '-' + version
            # t.add_vr(1)   # xiaozhan, remove this, seems not useful
            try:
                vlan1 = Vlan(t, 'vlan1')
                vlan2 = Vlan(t, 'vlan1')

                if vlan1.create() is False:
                    log.error('Failed to create vlan')
                    assert False
                if vlan2.create() is True:
                    log.error('Should fail since a VLAN with that name already exists')
                    assert False

                vlan2.name = 'vlan2'
                if vlan2.create() is False:
                    log.error('Failed to create vlan')
                    assert False

                # parent_eth = Ethernet(t, t.netif().ifname)
                parent_ifname = 'eth0'  # t.netif().ifname     xiaozhan,
                parent_eth = Ethernet(t, parent_ifname)  # xiaozhan, add eth0 to simplify this function

                for vr in range(2, -1, -1):  # xiaozhan, vr= 2 1 0
                    vlan1.set_vr(vr)

                    if vlan1.set_tag_parent_if(1, parent_eth) is False:
                        log.error('Could not set VLAN ID and parent interface')
                        assert False

                    if vlan2.set_tag_parent_if(1, parent_eth) is True:
                        log.error('Should fail to set the VLAN ID since it is already used')
                        assert False

                    if vlan1.set_tag_parent_if(10, parent_eth) is False:
                        log.error('Could not set VLAN ID and parent interface')
                        assert False

                    if vlan2.set_tag_parent_if(1, parent_eth) is False:
                        log.error('Could not set VLAN ID and parent interface')
                        assert False

                    if vlan2.set_tag_parent_if(2, parent_eth) is False:
                        log.error('Could not set VLAN ID and parent interface')
                        assert False

                if vlan1.up() is False:
                    log.error('Failed to bring interface UP')
                    assert False

                if vlan1.set_tag_parent_if(20, parent_eth) is True:
                    log.error('Should not be possible to change the VLAN ID while the interface is UP')
                    assert False

                if vlan1.down() is False:
                    log.error('Failed to bring interface DOWN')
                    assert False

                if vlan1.set_tag_parent_if(20, parent_eth) is False:
                    log.error('Could not set VLAN ID and parent interface')
                    assert False

                if vlan1.set_tag_parent_if(20, Ethernet(t, 'invalid_if')) is True:
                    log.error('Should not be possible to set the parent interface to something that do not exist')
                    assert False

                for vlan_id in range(10, 4095, 111):
                    if vlan1.set_tag_parent_if(vlan_id, parent_eth) is False:
                        log.error('Could not set VLAN ID and parent interface')
                        assert False

                for vlan_id in (0, 4096, -1, 12345):
                    if vlan1.set_tag_parent_if(vlan_id, parent_eth) is True:
                        log.error('Should not be possible to set an invalid VLAN ID')
                        assert False
                vlan1.cleanup()
                vlan2.cleanup()
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4', 'IPv6'])
    def test_compact_and_configure(self, version):
        with allure.step('Compact format of VLAN interface and configure'):
            t = self.t1
            name = 'compact_and_configure'
            case_name = self.module + '.' + name + '-' + version
            # t.add_vr(1)   # xiaozhan, remove this, seems not useful
            parent_ifname = 'eth0'
            try:
                vlan = Vlan(t, ' %s.20' % parent_ifname)

                if vlan.create() is False:
                    log.error('Failed to create vlan')
                    assert False

                if vlan.up() is False:
                    log.error('Failed to bring interface UP')
                    assert False

                if vlan.mtu() is False:
                    log.error('Failed to set MTU on VLAN interface')
                    assert False

                if vlan.lladdr() is False:
                    log.error('Failed to set lladdr on VLAN interface')
                    assert False

                if vlan.show() is True:
                    log.error('Failed to show VLAN interface')
                    assert False

                if vlan.promisc() is False:
                    log.error('Failed to set promisc mode on VLAN interface')
                    assert False

                if vlan.show() is True:
                    log.error('Failed to show VLAN interface')
                    assert False

                if vlan.clrpromisc() is False:
                    log.error('Failed to clr promisc mode on VLAN interface')
                    assert False

                if vlan.show() is True:
                    log.error('Failed to show VLAN interface')
                    assert False

                if vlan.promisc() is False:
                    log.error('Failed to set promisc mode on VLAN interface')
                    assert False

                if vlan.down() is False:
                    log.error('Failed to bring interface DOWN')
                    assert False

                vlan.cleanup()
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    def teardown_class(self):
        # clean up vxworks
        for t in self.vx_targets:
            t.cleanup()
            t.logFile.close()
        # process self.result ----store result,upload to Database or sth like that
        for i in self.result:
            if i[1] == 'PASS':
                self.pass_num += 1
            else:
                self.fail_num += 1
        log.info(self.result)
        log.info(f'total:{len(self.result)}, pass:{self.pass_num}, fail:{self.fail_num}')
