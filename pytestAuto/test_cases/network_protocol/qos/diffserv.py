#############################################################################
#
# Copyright (c) 2006-2014 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

'DiffServ'
import time

def test_marker(log, nodes, v6, ioctl_values, pre_ds, post_ds):
    marker_ids = []
    map_ids = []
    try:
        nets = (40, 41)

        hosts = nodes[1:]
        gw = nodes[0]

        gw_shell = gw.ipcom_shell()
        hosts_shell = [ host.ipcom_shell() for host in hosts ]

        gwsock = gw_shell.socket('inet' + v6, 'dgram')

        # Diffserv setup
        for i in range(len(ioctl_values)):
            value = ioctl_values[i]
            marker_id = int(gwsock.ioctl(option='siocxdscreate', value=('%s' % value)))
            marker_ids.append(marker_id)
            map_ids.append((pre_ds[i], marker_id))

        for map_id in map_ids:
            gwsock.ioctl(option='siocxadsmap', value=('{%d,%d}' % map_id))

        # Network setup
        gw_addrs   = [ gw.alloc_ip(v6, net = nets[0]), gw.alloc_ip(v6, net = nets[1]) ]
        hosts_addr = [ hosts[i].alloc_ip(v6, net = nets[i]) for i in range(2) ]

        gw_vlans = [ gw.add_vlan(addr = addr) for addr in gw_addrs ]
        hosts_vlan = [ hosts[i].add_vlan(addr = hosts_addr[i], vlan = gw_vlans[i].id) for i in range(2) ]
        hosts[0].add_route(dst = hosts_addr[1], gw = gw_addrs[0])
        hosts[1].add_route(dst = hosts_addr[0], gw = gw_addrs[1])

        # Send data over the gateway
        socks = [ host_shell.socket('inet'+v6, 'dgram') for host_shell in hosts_shell ]

        socks[1].setsockopt(level='socket', option='rcvtimeo', data='2000')
        socks[1].bind(addr=hosts_addr[1])
        _, port = socks[1].getsockname(v6)

        socks[0].connect(addr=hosts_addr[1], port=port)

        pre_ds = pre_ds + (1,)
        post_ds = post_ds + (1,)
        for i in range(len(pre_ds)):
            if v6:
                socks[0].setsockopt('ipv6', 'tclass', pre_ds[i])
                socks[1].setsockopt('ipv6', 'recvtclass', 1)
                ancillary_data = ('ipv6', 'tclass', post_ds[i])
            else:
                socks[0].setsockopt('ip', 'tos', pre_ds[i])
                socks[1].setsockopt('ip', 'recvtos', 1)
                ancillary_data = ('ip', 'tos', post_ds[i])
            for j in range(1, 10):
                socks[0].send(data='abc'*j)
                socks[1].recv(ancillary_data=ancillary_data)

        for sock in socks:
            sock.close()

    finally:
        # Diffserv cleanup
        for map_id in map_ids:
            gwsock.ioctl(option='siocxddsmap', value=('{%d,%d}' % map_id))
            time.sleep(1)

        invalid_marker_id = 0
        for marker_id in marker_ids:
            gwsock.ioctl(option='siocxdsdestroy', value=marker_id)
            time.sleep(1)
            if invalid_marker_id <= marker_id:
                invalid_marker_id = marker_id + 1

        gwsock.ioctl(option='siocxdsdestroy', value=invalid_marker_id, succeed=False)
        time.sleep(1)
        gwsock.close()



class simplemarker:
    'Simple marker will remark packets entering with one DS value to another fixed DS value'
    def config(self):
        self.hosts = 3
        self.eta = 5
        self.works_on_iplite  = False
        self.works_on_gpp = False
        self.works_on_lkm = False
        self.required_product_version('ipnet', '6.5.0.10')

    def test(self, log, nodes, v6, __):
        test_marker(log,
                    nodes,
                    v6,
                    ('{SimpleMarker,1,42,0}', '{SimpleMarker,3,43,2}'),
                    (7, 8),
                    (42, 43))

class srtcm_color_blind:
    """Single Rate Tree Color Marker will remark packets entering with one DS
    value to one of tree fixed DS values denoted green, yellow and red.
    Color blind mode assume that the packet has not been color marked before.
    """
    def config(self):
        self.hosts = 3
        self.eta = 5
        self.works_on_iplite  = False
        self.works_on_gpp = False
        self.works_on_lkm = False
        self.required_product_version('ipnet', '6.5.0.10')

    def test(self, log, nodes, v6, __):
        log('color blind mode')
        test_marker(log,
                    nodes,
                    v6,
                    ('{srTCM,1,10000,5000,3000,51,52,53}', '{srTCM,1,20000,7000,2000,61,62,63}'),
                    (12, 20),
                    (51, 61))

class srtcm_color_aware:
    """Single Rate Tree Color Marker will remark packets entering with one DS
    value to one of tree fixed DS values denoted green, yellow and red.
    Color aware mode will check if the packet has not been color marked before.
    """
    def config(self):
        self.hosts = 3
        self.eta = 5
        self.works_on_iplite  = False
        self.works_on_gpp = False
        self.works_on_lkm = False
        self.required_product_version('ipnet', '6.5.0.10')

    def test(self, log, nodes, v6, __):
        log('color aware mode')
        test_marker(log,
                    nodes,
                    v6,
                    ('{srTCM,2,10000,5000,3000,51,52,53}', '{srTCM,2,20000,7000,2000,61,62,63}'),
                    (12, 14),
                    (52, 63))

