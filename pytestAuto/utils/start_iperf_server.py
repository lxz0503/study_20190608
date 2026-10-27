#!/usr/bin/env python3
# encoding=utf-8
"""
@author:Xiaozhan Li
@Email:lxz_20081025@163.com
@time:3/14/2023 3:25 PM
@project:HCAPI
"""
import time
from hm_21_paramiko_class_ssh import client_cmd

cmd_input = 'pkill iperf3'
client_cmd.run_ssh(cmd_input)
cmd_input = 'iperf3 -s -p 10000 -1 &'
client_cmd.run_ssh(cmd_input)
time.sleep(300)
# client_cmd.close()
