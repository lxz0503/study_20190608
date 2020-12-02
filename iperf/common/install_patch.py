#!/usr/bin/env python3
# coding: utf-8

import urllib.request
import urllib.error
import shutil
import os
import argparse

def download_iperf(path):
	try:
		with urllib.request.urlopen('https://downloads.es.net/pub/iperf/iperf-3.1.3.tar.gz') \
			as response, open(os.path.join(path, 'iperf-3.1.3.tar.gz'), 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
	except urllib.error.URLError as e:
		print('url not working, use local file')
		shutil.copy('/folk/hyan1/Share/iperf-3.1.3.tar.gz', path)

def download_openssl(path):
	try:
		with urllib.request.urlopen('https://github.com/openssl/openssl/archive/OpenSSL_1_1_1d.tar.gz') \
			as response, open(os.path.join(path, 'OpenSSL_1_1_1d.tar.gz'), 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
	except urllib.error.URLError as e:
		print('url not working, use local file')
		shutil.copy('/folk/hyan1/Share/OpenSSL_1_1_1d.tar.gz', path)

def main():
	parse = argparse.ArgumentParser()
	parse.add_argument('--path', help='path', dest='path', required=True)
	args = parse.parse_args()
	path = args.path
	patch_path = os.path.join(path, 'download')
	download_iperf(patch_path)
	download_openssl(patch_path)

if __name__ == "__main__":
	main()


		