#!/usr/bin/env python3
# coding: utf-8

import sys
import argparse
import re

def get_result(log):
	"""
	"""
	with open(log,'r') as f:
		pat = re.compile(r'(\d+)/.*not')
		pat_1 = re.compile(r'(\w+).* (WEAK)')
		for line in f:
			line = line.strip()
			m = pat.search(line)
			n = pat_1.match(line)
			if m:
				result = m.group(1)
			elif n:
				result = 1
	return result

if __name__ == '__main__':
	parse = argparse.ArgumentParser()
	parse.add_argument('-f', '--file', help='log file to process', dest='filename', required=True)
	args = parse.parse_args()
  	
	dict_data = {}
	log = args.filename
	result = get_result(log)
	dict_data.setdefault('result',result)
	print(dict_data)
