#############################################################################
#
# Copyright (c) 2006-2013 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

"IEEE 802.1Q - Virtual LAN"



class NetworkInterface:
    def __init__(self, session, name):
        self.session = session
        self.name = name
        self.vr = 0

    def getName(self):
        return self.name

    def up(self):
        return self.invokeCmd('up')

    def down(self):
        return self.invokeCmd('down')

    def setVR(self, vr):
        if self.invokeCmd('vr %d' % vr):
            self.vr = vr
            return True
        return False

    def getVR(self):
        return self.vr

    def invokeCmd(self, cmd):
        success = True
        cmd = 'ifconfig -V %d %s %s' % (self.vr, self.name, cmd)
        lines = self.session.send_and_return_all(cmd)
        if len(lines) > 0:
            return False
        return True

    def invokeIPCmd(self, cmd):
        success = True
        cmd = 'ip -V %d link %s' % (self.vr, cmd)
        lines = self.session.send_and_return_all(cmd)
        if len(lines) > 0:
            return False
        return True


class Ethernet(NetworkInterface):
    def __init__(self, session, name):
        NetworkInterface.__init__(self, session, name)


class Vlan(NetworkInterface):
    def __init__(self, session, name):
        NetworkInterface.__init__(self, session, name)
        self.is_created = False

    def cleanup(self):
        self.down()
        self.destroy()

    def create(self):
        return self.invokeCmd('create')

    def destroy(self):
        return self.invokeCmd('destroy')

    def setTagAndParentIf(self, tag, parent_ethernet):
        return self.invokeCmd('vlan %d vlanif %s#%d' %
                              (tag, parent_ethernet.getName(), parent_ethernet.getVR()))

    def show(self):
        return self.invokeCmd('')

    def mtu(self):
        return self.invokeCmd('mtu 1400')

    def lladdr(self):
        return self.invokeCmd("lladdr 00:00:00:00:00:05")

    def promisc(self):
        return self.invokeCmd("promisc")

    def clrpromisc(self):
        return self.invokeCmd("-promisc")

    def add(self, tag):
        return self.invokeIPCmd('add %s link eth0 type vlan id %d' %
                                (self.name, tag))

    def delete(self):
        return self.invokeIPCmd('delete %s' %
                                (self.name))

    def ipshow(self):
        return self.invokeIPCmd('show dev %s' %
                                (self.name))


class create_and_configure:
    "Successful and unsuccessful creation and configuration of VLAN interface"
    def config(self):
        self.hosts = 1
        self.eta = 1
        self.works_on_iplite = False
        self.works_on_lkm    = False
        self.works_on_gpp    = False

    def test(self, log, hosts, v6, _):
        nut = hosts

        nut.add_vr(1)

        try:
            vlan1 = Vlan(nut, 'vlan1')
            vlan2 = Vlan(nut, 'vlan1')

            if vlan1.create() == False:
                raise test_fail('Failed to create vlan')
            if vlan2.create() == True:
                raise test_fail('Should fail since a VLAN with that name already exists')

            vlan2.name = 'vlan2'
            if vlan2.create() == False:
                raise test_fail('Failed to create vlan')

            parent_eth = Ethernet(nut, nut.netif().ifname)

            for vr in range(2, -1, -1):
                vlan1.setVR(vr)

                if vlan1.setTagAndParentIf(1, parent_eth) == False:
                    raise test_fail('Could not set VLAN ID and parent interface')

                if vlan2.setTagAndParentIf(1, parent_eth) == True:
                    raise test_fail('Should fail to set the VLAN ID since it is already used')

                if vlan1.setTagAndParentIf(10, parent_eth) == False:
                    raise test_fail('Could not set VLAN ID and parent interface')

                if vlan2.setTagAndParentIf(1, parent_eth) == False:
                    raise test_fail('Could not set VLAN ID and parent interface')

                if vlan2.setTagAndParentIf(2, parent_eth) == False:
                    raise test_fail('Could not set VLAN ID and parent interface')
            if vlan1.up() == False:
                raise test_fail('Failed to bring interface UP')

            if vlan1.setTagAndParentIf(20, parent_eth) == True:
                raise test_fail('Should not be possible to change the VLAN ID while the interface is UP')

            if vlan1.down() == False:
                raise test_fail('Failed to bring interface DOWN')

            if vlan1.setTagAndParentIf(20, parent_eth) == False:
                raise test_fail('Could not set VLAN ID and parent interface')

            if vlan1.setTagAndParentIf(20, Ethernet(nut, 'invalid_if')) == True:
                raise test_fail('Should not be possible to set the parent interface to something that do not exist')

            for vlan_id in range(10, 4095, 111):
                if vlan1.setTagAndParentIf(vlan_id, parent_eth) == False:
                    raise test_fail('Could not set VLAN ID and parent interface')

            for vlan_id in (0, 4096, -1, 12345):
                if vlan1.setTagAndParentIf(vlan_id, parent_eth) == True:
                    raise test_fail('Should not be possible to set an invalid VLAN ID')
        finally:
            vlan1.cleanup()
            vlan2.cleanup()


class compact_and_configure:
    "Compact format of VLAN interface and configure"
    def config(self):
        self.hosts = 1
        self.eta = 1
        self.works_on_iplite = False
        self.works_on_lkm    = False
        self.works_on_gpp    = False

    def test(self, log, hosts, v6, _):
        nut = hosts
        parent_ifname = nut.netif().ifname

        nut.add_vr(1)

        try:
            vlan = Vlan(nut, ' %s.20' % parent_ifname)

            if vlan.create() == False:
                raise test_fail('Failed to create vlan')

            if vlan.up() == False:
                raise test_fail('Failed to bring interface UP')

            if vlan.mtu() == False:
                raise test_fail('Failed to set MTU on VLAN interface')

            if vlan.lladdr() == False:
                raise test_fail('Failed to set lladdr on VLAN interface')

            if vlan.show() == True:
                raise test_fail('Failed to show VLAN interface')

            if vlan.promisc() == False:
                 raise test_fail('Failed to set promisc mode on VLAN interface')

            if vlan.show() == True:
                raise test_fail('Failed to show VLAN interface')

            if vlan.clrpromisc() == False:
                 raise test_fail('Failed to clr promisc mode on VLAN interface')

            if vlan.show() == True:
                raise test_fail('Failed to show VLAN interface')

            if vlan.promisc() == False:
                 raise test_fail('Failed to set promisc mode on VLAN interface')

            if vlan.down() == False:
                raise test_fail('Failed to bring interface DOWN')

        finally:
            vlan.cleanup()


