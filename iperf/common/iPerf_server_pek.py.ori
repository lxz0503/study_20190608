#!/usr/bin/env python3
# coding: utf-8

from pexpect import pxssh
import re

try:
	s = pxssh.pxssh()
	hostname = '128.224.166.211'
	username = 'target'
	password = 'vxTarget'
	s.login(hostname, username, password, auto_prompt_reset=False)
	s.PROMPT='windriver-S5520HC>'
	s.prompt()
	print(s.before)
	s.sendline('ps -aux | grep iperf')
	s.prompt()
	print(s.before)
	if re.search('10000', str(s.before)):
		s.sendline('pkill iperf3')
		print('kill the previous process')
		s.prompt()
		print(s.before)
	s.sendline('iperf3 -s -p 10000 -1 &')
	print('iPerf Server is listening')
	s.prompt()
	print(s.before)
	print('==logout==')
	s.logout()
except pxssh.ExceptionPxssh as e:
	print("pxssh failed to login.")
	print(e)






