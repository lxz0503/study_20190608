#############################################################################
#
# Copyright (c) 2020, 2021 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

"SNMP agentX kong tests"

import re
import time
import util

class snmp_agentx_session_limit:
    'snmp agentX test'
    def config(self):
        self.eta = 20
        self.hosts = 4
        self.telnetprompt = 'telnet>'
        self.v6 = False
        self.require_types = ['linux', 'linux', 'linux', 'ipnet']

    def test(self, log, hosts, v6, _):
        # the precondition is VIP parameter SNMP_AGENTX_MAX_SESSIONS = 1
        # note: port 705 is the agentX reserved port
        c1, c2, c3, s = hosts

        # the first linux client telnet to VxWorks port 705
        c1.send('corktelnet %s 705' % s.ip().addr, sudo = False)
        c1.expect_exact('Connected to %s.' % s.ip().addr)
        c1.expect_exact('Escape character is \'^]\'.')
        c1.send_ctrl_right_square_bracket()
        c1.expect_exact(self.telnetprompt)
        time.sleep(5)

        # the second linux client telnet to VxWorks port 705 and is refused
        c2.send('corktelnet %s 705' % s.ip().addr, sudo = False)
        c2.expect_exact('Connected to %s.' % s.ip().addr)
        c2.expect_exact('Escape character is \'^]\'.')
        c2.expect_exact('Connection closed by foreign host.')
        c2.wait_prompt()
        time.sleep(5)

        # disconnect the telnet session from the first linux client
        # to VxWorks
        c1.send('quit', sudo = False)
        c1.expect_exact('Connection closed.')

        # the third linux client telnet to VxWorks port 705 and succeed
        c3.send('corktelnet %s 705' % s.ip().addr, sudo = False)
        c3.expect_exact(r'Connected to %s.' % s.ip().addr)
        c3.expect_exact('Escape character is \'^]\'.')
        c3.send_ctrl_right_square_bracket()
        c3.expect_exact(self.telnetprompt)
        time.sleep(5)

        c3.send('quit', sudo = False)
        c3.expect_exact('Connection closed.')
