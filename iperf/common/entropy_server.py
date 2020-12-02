#!/usr/bin/env python3
# coding: utf-8

from pexpect import pxssh
import re
import argparse
import sys

def execTool(address, tool):
	if tool == 'sts':
		time_out = 60
		cmd = '/mydisk/F8913/rndProxy  {targetAddress} 3000 | /mydisk/F8913/sts-master/sts -v 1 -i 32 -I 0 -w /mydisk/F8913/log/sts/{targetAddress} -F r -'.format(targetAddress = address)
		cmd_cat = 'cat /mydisk/F8913/log/sts/{targetAddress}/result.txt'.format(targetAddress = address)
	elif tool == 'dieharder':
		time_out = 1800
		#cmd = '/mydisk/F8913/rndProxy  {targetAddress} 3000 | dieharder -a -g 200 -c \' \' -D default -D histogram -D description | tee /mydisk/F8913/log/dieharder/{targetAddress}'.format(targetAddress = address)
		cmd = '/mydisk/F8913/rndProxy  {targetAddress} 3000 | dieharder -a -g 200 -c \' \' -D default | tee /mydisk/F8913/log/dieharder/{targetAddress}'.format(targetAddress = address)
		#cmd = '/mydisk/F8913/rndProxy  {targetAddress} 3000 | dieharder -d 0 -g 200 -c \' \' -D default | tee /mydisk/F8913/log/dieharder/{targetAddress}'.format(targetAddress = address)
		cmd_cat = 'cat /mydisk/F8913/log/dieharder/{targetAddress}'.format(targetAddress = address)
	print('{tool} is running'.format(tool = tool))
	print(cmd)
	try:
		s = pxssh.pxssh(encoding='utf-8')
		s.timeout = time_out
		#s.logfile = sys.stdout
		hostname = '128.224.167.34'
		username = 'windriver'
		password = 'windriver'
		s.login(hostname, username, password, auto_prompt_reset=True)
		s.sendline(cmd)
		s.prompt()
		#print(s.before)
		s.sendline(cmd_cat)
		s.prompt()
		print(s.before)
		print('==logout==')
		s.logout()
	except pxssh.ExceptionPxssh as e:
		print("pxssh failed to login.")
		print(e)

def main():
	parse = argparse.ArgumentParser()
	parse.add_argument('--addr', help='targetAddress', dest='address', required=True)
	parse.add_argument('--tool', help='tool', dest='tool', required=True)
	args = parse.parse_args()
	address = args.address
	tool = args.tool
	execTool(address, tool)
if __name__ == "__main__":
	main()




