#############################################################################
#
# Copyright (c) 2022 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################


"SNMP excluding version 1&2c kong tests"

import time
from iptestengine import test_fail

class snmp_exclude_v1_v2c_cmd:
    'snmp v1 v2c in v3-only mode command test'
    def config(self):
        self.eta = 20
        self.hosts = 2
        self.prompt = "snmptalk"
        self.v6 = False

    def test(self, log, hosts, v6, _):
        c, s = hosts
        c.send("C snmptalk")
        time.sleep(1)
        c.expect_exact(self.prompt)
        c.send("dest %s" % s.ip().addr)
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        c.send("port 161")
        c.expect_exact("snmptalk@%s>" % s.ip().addr)
        # The v1&v2c commands are disabled in v3-only mode
        c.send("version 1 public private")
        c.expect_exact("Usage:")
        c.send("version 2c public private")
        c.expect_exact("Usage:")
        c.send("quit")
        c.expect_exact("exit snmptalk cmdline.")

class snmp_exclude_v1_v2c_udp:
    'snmp v1 v2c in v3-only mode udp test'
    def config(self):
        self.eta = 20
        self.hosts = 2
        self.v6 = False
        self.require_types = ['linux', 'ipnet']

    def test(self, log, hosts, v6, _):
        c, s = hosts

        cmd = "snmpget -v3 -a MD5 -A initialmd5 -X initialmd5 -l authNoPriv -u initialmd5 " \
              "{} iso.3.6.1.2.1.11.3.0 -r 0".format(s.ip().addr)
        ret = c.send_and_return_all(cmd)
        expect = "snmpInBadVersions.0 = Counter32: 0"
        if expect not in ret[0]:
            raise test_fail("SNMP exclude v1 & v2c test failed.")

        time.sleep(5)

        cmd = "snmpget -v2c -c public {} iso.3.6.1.2.1.11.3.0 -r 0".format(
            s.ip().addr)
        ret = c.send_and_return_all(cmd)
        expect = "Timeout: No Response from {}".format(s.ip().addr)
        if expect not in ret[0]:
            raise test_fail("SNMP exclude v1 & v2c test failed.")

        time.sleep(5)

        cmd = "snmpget -v3 -a MD5 -A initialmd5 -X initialmd5 -l authNoPriv -u initialmd5 " \
              "{} iso.3.6.1.2.1.11.3.0 -r 0".format(s.ip().addr)
        ret = c.send_and_return_all(cmd)
        expect = "snmpInBadVersions.0 = Counter32: 1"
        if expect not in ret[0]:
            raise test_fail("SNMP exclude v1 & v2c test failed.")
