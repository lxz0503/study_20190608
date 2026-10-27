#############################################################################
#
# Copyright (c) 2018, 2021-2022 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################


"SNMP version 1&2c udp kong tests"

import re
import time
import util

class snmp_manager_cmd:
    'snmp manager basic cmds test'
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
        c.send("version")
        c.expect_exact("version 1|2c <read_community> <write_community>")
        c.send("version 1 public private")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("version:1")
        c.send("status")
        c.expect_exact("read community:public")
        c.send("help")
        c.expect_exact("Command is any interactive command followed by its arguments.")
        c.send("get sysName.0")
        c.expect_exact("sysName.0    	String")
        c.send("set sysName.0 interpeak")
        c.expect_exact("sysName.0    	String(9): interpeak")
        c.send("get sysName.0")
        c.expect_exact("sysName.0    	String(9): interpeak")
        c.send("next sysName.0")
        c.expect_exact("sysLocation.0    	String")
        c.send("walk")
        time.sleep(120)
        c.expect_exact("No more in MIB")
        c.send("quit")
        c.expect_exact("exit snmptalk cmdline.")

class snmp_v2c_udp:
    'snmp v2c udp transport test'
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
        c.send("version 2c public private")
        c.expect_exact(self.prompt)
        c.send("status")
        c.expect_exact("version:2c")
        c.send("status")
        c.expect_exact("write community:private")
        c.send("get sysName.0")
        c.expect_exact("sysName.0    	String")
        c.send("set sysName.0 interpeak")
        c.expect_exact("sysName.0    	String(9): interpeak")
        c.send("get sysName.0")
        c.expect_exact("sysName.0    	String(9): interpeak")
        c.send("next sysName.0")
        c.expect_exact("sysLocation.0    	String")
        c.send("walk")
        time.sleep(120)
        c.expect_exact("No more in MIB")
        c.send("quit")
        c.expect_exact("exit snmptalk cmdline.")
