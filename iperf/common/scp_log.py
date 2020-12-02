#!/usr/bin/env python3
# coding: utf-8
import paramiko
from paramiko import SSHClient
import scp
from scp import SCPClient
import sys
import time
import argparse
import os

def progress(filename, size, sent):
	sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100))

def get_log(address, tool, log_path):
	try:
		ssh = SSHClient()
		#ssh.load_system_host_keys()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect('128.224.167.34', username='windriver', password='windriver')
		print('exec command')
		#cmd = 'pwd'
		cmd = '/usr/bin/python3 /folk/hyan1/Nightly/common/entropy_server_v2.py --addr {targetAddress} --tool {Tool}'.format(targetAddress=address, Tool=tool)
		stdin, stdout, sterr = ssh.exec_command(cmd)
		print(stdout.channel.recv_exit_status())
		print('\nstdout:%s' % '\n'.join(stdout))
		print('\nsterr:%s' % '\n'.join(sterr))
	except paramiko.AuthenticationException:
		print("Authentication failed, please verify your credentials" )
	except paramiko.SSHException as sshException:
		print("Unable to establish SSH connection: %s" % sshException)
	except paramiko.BadHostKeyException as badHostKeyException:
		print("Unable to verify server's host key: %s" % badHostKeyException)
	except Exception as e:
		print(e.args)

	try:
		if tool == 'sts':
			src = '/mydisk/F8913/log/sts/{targetAddress}/result.txt'.format(targetAddress=address)
		elif tool == 'dieharder':
			src = '/mydisk/F8913/log/dieharder/{targetAddress}'.format(targetAddress=address)
		with SCPClient(ssh.get_transport(), progress=progress) as scp_clinet:
			scp_clinet.get(src, os.path.join(log_path, 'rnd.log'))
		sys.stdout.write('\n')
		ssh.close()
	except scp.SCPException as e:
		print("Operation error: %s", e) 

def main():
	parse = argparse.ArgumentParser()
	parse.add_argument('--addr', help='targetAddress', dest='address', required=True)
	parse.add_argument('--tool', help='tool', dest='tool', required=True)
	parse.add_argument('--path', help='path', dest='path', required=True)
	args = parse.parse_args()
	address = args.address
	tool = args.tool
	log_path = args.path
	get_log(address, tool, log_path)
if __name__ == "__main__":
	main()






