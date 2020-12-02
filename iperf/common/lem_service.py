#!/usr/bin/env python3
# coding: utf-8

import urllib.request
import urllib.error
import subprocess

try:
	response = urllib.request.urlopen('http://128.224.166.211:9090/')
	print(response.read().decode('utf-8'))
	print(response.status)
except urllib.error.URLError as e:
	print('LEM Server down!')
	print('Start LEM Service ...')
	out_bytes = subprocess.check_output('/folk/hyan1/Nightly/lem.sh', shell=True)