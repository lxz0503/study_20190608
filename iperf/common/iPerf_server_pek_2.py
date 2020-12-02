#!/usr/bin/env python3
# coding: utf-8
import paramiko
from paramiko import SSHClient

try:
		ssh = SSHClient()
		#ssh.load_system_host_keys()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect('128.224.167.37', username='windriver', password='windriver')
		print('exec command')
		#cmd = 'pwd'
		cmd = 'pkill iperf3'
		print('kill the previous process')
		stdin, stdout, sterr = ssh.exec_command(cmd)
		print(stdout.channel.recv_exit_status())
		cmd = 'iperf3 -s -p 10000 -1 &'
		print('iPerf Server is listening')
		stdin, stdout, sterr = ssh.exec_command(cmd)
		print('exit')
		print(stdout.channel.recv_exit_status())
		#print('\nstdout:%s' % '\n'.join(stdout))
		#print('\nsterr:%s' % '\n'.join(sterr))
		ssh.close()
except paramiko.AuthenticationException:
	print("Authentication failed, please verify your credentials" )
except paramiko.SSHException as sshException:
	print("Unable to establish SSH connection: %s" % sshException)
except paramiko.BadHostKeyException as badHostKeyException:
	print("Unable to verify server's host key: %s" % badHostKeyException)
except Exception as e:
	print(e.args)