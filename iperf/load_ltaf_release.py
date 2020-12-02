#!/usr/bin/env python3
# coding: utf-8

import xml.etree.ElementTree as ET
import sys
import os
import logging
import re
import argparse
from fnmatch import fnmatch
logging.basicConfig(level=logging.WARNING)
#logging.basicConfig(level=logging.INFO)

def parse_xml(xml_file):
	dict_node = {}
	dict_node.setdefault('buildStatus', 'PASS')
	dict_node.setdefault('vsboptions', '')
	try:
		tree = ET.parse(xml_file)
		for node in tree.iter('logs'):
			dict_node['status_log'] = node.attrib['status_log']
			#print(node.attrib)
		for node in tree.iter('dvd'):
			str = node.attrib['dir']
			list_str = str.split('/')
			l_type = list_str[-1].split('-')[-1]
			dict_node['Spin'] = list_str[-1]
			dict_node['SpinType'] = l_type
		for node in tree.iter('test_case'):
			str = node.attrib['uri']
			list_str = str.split('/')
			dict_node['test_name'] = list_str[-1]
			dict_node['test_suite'] = list_str[-2]
		for node in tree.iter('node'):
			logging.info(node.attrib)
			dict_node['bsp'] = node.attrib['bsp']
			dict_node['tool'] = node.attrib['tool']
			dict_node['barcodes'] = node.attrib['barcodes']
			dict_node['config_label'] = node.attrib['config_label']
			dict_node['tech'] = node.attrib['tech']
			dict_node['board_name'] = node.attrib['board_name']
			dict_node['options'] = node.attrib['options']
			if 'vsboptions' in node.attrib:
				dict_node['vsboptions'] = node.attrib['vsboptions']

		for node in tree.iter('report_data'):
			if 'buildStatus' in node.attrib:
				dict_node['buildStatus']= node.attrib['buildStatus']
			dict_node['execStatus']= node.attrib['execStatus']
		
		#for key in dict_node:
		#	print(key,dict_node[key])	
		return dict_node
	except Exception as e:
		print("parse xml fail!")
		print(e)
		sys.exit(0)

def find_xml(**kw):
	for log_dir in os.listdir(kw['log']):
		result_dir = os.path.join(os.path.abspath(log_dir), 'LTAF/Result')
		if not os.path.exists(result_dir):
			os.makedirs(result_dir)
		for dirpath, dirnames, filenames in os.walk(log_dir):
			for filename in filenames:
				if fnmatch(filename, 'testRunWorkingCopy.xml'):
					create_ini(os.path.join(dirpath, filename), result_dir, **kw)
		for file in os.listdir(result_dir):
			command = 'curl -F resultfile=@{FILE} http://pek-lpgtest3.wrs.com/ltaf/upload_results.php'.format(FILE = os.path.join(result_dir, file))
			print(command)
			os.system(command)

def create_ini(filename, result_dir, **kw):
	#print(kw)
	template = '/folk/hyan1/Nightly/result.ini'
	#case_ini = 'case.ini'
	dict_ini = {}
	dict_ini.setdefault('tags', 'IPERF')
	dict_ini.setdefault('domain', 'networking')
	dict_ini.setdefault('test_component', 'networking')
	dict_ini.setdefault('function_pass', '0')
	dict_ini.setdefault('function_fail', '0')
	dict_ini.setdefault('release_name', 'vxworks_sandbox')
	dict_ini.setdefault('sprint', 'Nightly')
	# for release testing, need input USER_STORIES num
	dict_ini.setdefault('requirements', '')
	logging.info('##########################')
	logging.info(filename)
	logging.info('##########################')
	dict_node = parse_xml(filename)
	dict_ini['BSP'] = dict_node['bsp']
	dict_ini['Tool'] = dict_node['tool']
	dict_ini['Barcode'] = dict_node['barcodes']
	dict_ini['Config Label'] = dict_node['config_label']
	dict_ini['Tech'] = dict_node['tech']
	dict_ini['Board'] = dict_node['board_name']
	dict_ini['Options'] = dict_node['options']
	dict_ini['Vsboptions'] = dict_node['vsboptions']
	dict_ini['status'] = dict_node['execStatus']
	dict_ini['log'] = os.path.dirname(dict_node['status_log']).replace('/home/windriver/Logs', 'http://pek-cc-pb08l.wrs.com/vxtest/vxtest1/LOG_VX7/Vx-7_Networking/{RELEASE}/IPERF'.format(RELEASE = kw['release']))
	dict_ini['build'] = dict_node['buildStatus']
	dict_ini['test_name'] = dict_node['test_name']
	dict_ini['test_suite'] = dict_node['test_suite']
	dict_ini['SpinType'] = dict_node['SpinType']
	dict_ini['Spin'] = dict_node['Spin']
	if dict_ini['status'] == 'TIMEOUT' or dict_ini['status'] == 'EXCEPTION' or dict_ini['status'] == 'SKIP':
		dict_ini['status'] = 'BLOCKED'
	if dict_ini['status'] == 'NotStarted':
		dict_ini['status'] = 'Not Started'
	if dict_ini['status'] == 'PASS':
		dict_ini['function_pass'] = '1'
	else:
		dict_ini['function_fail'] = '1'
	if 'requirements' in kw:
		dict_ini['requirements'] = kw['requirements']
	if 'release' in kw:
		dict_ini['release_name'] = kw['release']
	if 'sprint' in kw:
		dict_ini['sprint'] = kw['sprint']
	if 'rundate' in kw:
		dict_ini['week'] = kw['rundate']

	ini_name = '.'.join([dict_ini['test_name'], 'ini'])
	case_ini = os.path.join(result_dir, ini_name)
	file_data = ""
	with open(template, 'r', encoding='utf-8') as f:
		for line in f:
			if '=' in line:
				#logging.info(line)
				item = line.split('=')[0].strip()
				#logging.info(item)
				#print(item, item_lower)
				if item in dict_ini:
					#print(item_lower, dict_node[item_lower])
					line = '{ITEM} = {VALUE} {END}'.format(ITEM = item, VALUE = dict_ini[item], END = os.linesep)
					#logging.info(line)
					#logging.info('========================')
			file_data += line 
	with open(case_ini, 'w', encoding='utf-8') as f:
		#logging.info(file_data)
		f.write(file_data)

def main():
	parse = argparse.ArgumentParser()
	parse.add_argument('--log', help='log path', dest='log', required=True)
	parse.add_argument('--rundate', help='rundate', dest='rundate', required=True)
	parse.add_argument('--release', help='ltaf release', dest='release', required=True)
	parse.add_argument('--sprint', help='ltaf sprint', dest='sprint', required=False)
	parse.add_argument('--requirements', help='USER_STORIES ID', dest='requirements', required=False)
	args = parse.parse_args()
	p_log = args.log
	p_rundate = args.rundate
	p_release = args.release
	p_sprint = args.sprint
	p_requirements = args.requirements
	kw = {}
	if p_log:
		kw['log'] = p_log
	if p_rundate:
		kw['rundate'] = p_rundate
	if p_release:
		kw['release'] = p_release
	if p_sprint:
		kw['sprint'] = p_sprint
	if p_requirements:
		kw['requirements'] = p_requirements

	find_xml(**kw)
if __name__ == '__main__':
	file = '/home/windriver/Logs/log_2018_09_12_18_27_15/p4080_18995_tcp_64/fsl_p3p4p5_platform_up/fsl_p4080_ds.BootVxBootRomfrag.Uboot.LoadVxWorks.up.fsl_common.true.gnu/testRunWorkingCopy.xml'
	#parse_xml(file)
	#create_ini(file)
	main()