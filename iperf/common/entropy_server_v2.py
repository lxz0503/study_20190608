#!/usr/bin/env python3
# coding: utf-8

import argparse
import os

def execTool(address, tool):
	if tool == 'sts':
		cmd = '/mydisk/F8913/rndProxy  {targetAddress} 3000 | /mydisk/F8913/sts-master/sts -v 1 -i 32 -I 0 -w /mydisk/F8913/log/sts/{targetAddress} -F r -'.format(targetAddress = address)
	elif tool == 'dieharder':
		cmd = '/mydisk/F8913/rndProxy  {targetAddress} 3000 | /usr/local/bin/dieharder -a -g 200 -c \' \' -D default | tee /mydisk/F8913/log/dieharder/{targetAddress}'.format(targetAddress = address)
		#cmd = '/mydisk/F8913/rndProxy  {targetAddress} 3000 | /usr/local/bin/dieharder -d 100 -g 200 -c \' \' -D default | tee /mydisk/F8913/log/dieharder/{targetAddress}'.format(targetAddress = address)
	print(cmd)
	print(os.system(cmd))
	#child = pexpect.spawn('/bin/bash', ['-c', cmd])
	#child.expect(pexpect.EOF, timeout=None)
	#child.expect(pexpect.EOF)

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