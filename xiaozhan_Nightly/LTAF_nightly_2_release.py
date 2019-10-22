#!/usr/bin/env python3
# coding: utf-8

import os
import requests
from lxml import etree
from tempfile import NamedTemporaryFile
import logging
import argparse

class Case(object):
	def __init__(self, case):
		self.release_name = 'vx7-integration-native'
		self.test_name = case.xpath('.//td[3]/text()')
		self.test_suite = case.xpath('.//td[4]/text()')
		self.sprint = case.xpath('.//td[5]/text()')
		self.week = case.xpath('.//td[6]/text()') # run_date
		self.build = case.xpath('.//td[7]/text()')
		self.status = case.xpath('.//td[8]/div/@value')
		self.log = case.xpath('.//td[9]/div/@value')
		self.test_component = case.xpath('.//td[10]/text()')
		self.tester = case.xpath('.//td[11]/div/@value')
		self.requirements = case.xpath('.//td[13]/text()')
		self.defects = case.xpath('.//td[14]/div/@value')
		self.function_pass = case.xpath('.//td[15]/div/@value')
		self.function_fail = case.xpath('.//td[16]/div/@value')
		self.domain = case.xpath('.//td[17]/div/@value')
		self.Key = case.xpath('.//td[19]/text()')
		self.BSP = case.xpath('.//td[20]/text()')
		self.Config_Label = case.xpath('.//td[21]/text()') # Config Label in ini
		self.Tech = case.xpath('.//td[22]/text()')
		self.Tool = case.xpath('.//td[23]/text()')
		self.Host_OS = case.xpath('.//td[24]/text()') # Host OS in ini
		self.Board = case.xpath('.//td[25]/text()')
		self.Options = case.xpath('.//td[26]/text()')
		self.Buildoptions = case.xpath('.//td[27]/text()')
		self.Vsboptions = case.xpath('.//td[28]/text()')
		self.SpinType = case.xpath('.//td[30]/text()')
		self.Taskid = case.xpath('.//td[31]/div/@value')
		self.Spin = case.xpath('.//td[35]/div/@value')
		self.Barcode = case.xpath('.//td[37]/text()')
		self.tags = case.xpath('.//td[38]/div/@value')
		self.set_attr_tostring()

	def get_attr(self):
		print(self.__dict__)
		#if attr in self.__dict__:
		#	self.attr = 
	
	def set_attr(self, **kwargs):
		for attr in kwargs:
			if attr in self.__dict__:
				self.__dict__[attr] = kwargs[attr]

	def set_attr_tostring(self):
		for attr in self.__dict__:
			if isinstance(self.__dict__[attr], list):
				if len(self.__dict__[attr]):
					self.__dict__[attr] = self.__dict__[attr][0]
				# list length is 0
				else:
					self.__dict__[attr] = ''


	def create_ini(self):
		template = '/folk/hyan1/Nightly/result.ini'
		dict_ini = {}
		dict_ini['release_name'] = self.release_name
		dict_ini['test_name'] = self.test_name
		dict_ini['test_suite'] = self.test_suite
		dict_ini['sprint'] = self.sprint
		dict_ini['week'] = self.week
		dict_ini['build'] = self.build
		dict_ini['status'] = self.status
		dict_ini['log'] = self.log
		dict_ini['test_component'] = self.test_component
		dict_ini['tester'] = self.tester
		dict_ini['requirements'] = self.requirements
		dict_ini['defects'] = self.defects
		dict_ini['function_pass'] = self.function_pass
		dict_ini['function_fail'] = self.function_fail
		dict_ini['domain'] = self.domain
		dict_ini['Key'] = self.Key
		dict_ini['BSP'] = self.BSP
		dict_ini['Config Label'] = self.Config_Label
		dict_ini['Tech'] = self.Tech
		dict_ini['Tool'] = self.Tool
		dict_ini['Host OS'] = self.Host_OS
		dict_ini['Board'] = self.Board
		dict_ini['Options'] = self.Options
		dict_ini['Buildoptions'] = self.Buildoptions
		dict_ini['Vsboptions'] = self.Vsboptions
		dict_ini['SpinType'] = self.SpinType
		dict_ini['Taskid'] = self.Taskid
		dict_ini['Spin'] = self.Spin
		dict_ini['Barcode'] = self.Barcode
		dict_ini['tags'] = self.tags

		file_data = ""
		with open(template, 'r', encoding='utf-8') as f:
			for line in f:
				if '=' in line:
					logging.info(line)
					item = line.split('=')[0].strip()
					logging.info(item)
					#print(item, item_lower)
					if item in dict_ini:
						#print(item_lower, dict_node[item_lower])
						line = '{ITEM} = {VALUE} {END}'.format(ITEM = item, VALUE = dict_ini[item], END = os.linesep)
						logging.info(line)
						logging.info('========================')
				file_data += line 
		with NamedTemporaryFile('w+t', delete=False) as f:
			#print('file name', f.name)
			f.write(file_data)
		return  f.name

	def case_update(self, ini):
		command = 'curl -F resultfile=@{FILE} \
			http://pek-lpgtest3.wrs.com/ltaf/upload_results.php'.format(FILE = ini)
		os.system(command)
		os.remove(ini)

class Result(object):
	def __init__(self):
		self.url = 'http://pek-lpgtest3.wrs.com/ltaf/nightly_results.php'
		self.payload = {
			'releasename':'',
			'clearfilter':'true',
			'tf_tr_whentostart':'',
			'tf_test_component':'',
			'tf_tr_tags':'',
			'tf_per_page':'3000',
			'tf_test_suite':'',
			'tf_tr_status':'',
			'tf_tr_tester':'',
			'tf_tr_sprint':'',
			'tf_tr_search':'',
			}

	def payload_update(self, **kwargs):
		for attr in kwargs:
			if attr in self.payload:
				self.payload[attr] = kwargs[attr]

	# kwargs, the payload need to update
	def get_results(self, **kwargs):
		self.payload_update(**kwargs)
		response = requests.get(self.url, params = self.payload)
		print(response.url)
		# html is the etree root node
		html = etree.HTML(response.text)
		# cases is a list ,the item is etree Element type, each item is a case
		cases = html.xpath('//tr[@name="trbeforeck"]')
		return cases

def result_load(nightly_release_name, nightly_sprint, run_date, tag, \
	test_suite, release_name, requirements, sprint, week, status, tester, \
	component, domain, key, debug):
	nightly_results = Result()
	dict_payload = {}
	dict_payload['releasename'] = nightly_release_name 
	dict_payload['tf_tr_whentostart'] = run_date 
	dict_payload['tf_test_component'] = component
	dict_payload['tf_tr_tags'] = tag
	dict_payload['tf_test_suite'] = test_suite
	dict_payload['tf_tr_status'] = status
	dict_payload['tf_tr_tester'] = tester
	dict_payload['tf_tr_sprint'] = nightly_sprint
	dict_payload['tf_tr_search'] = key
	

	nightly_cases = nightly_results.get_results(**dict_payload)
	print('{} cases will be load'.format(len(nightly_cases)))
	k = input('upload? (y/n)')
	if k == 'y':
		for item in nightly_cases:
			case = Case(item)
			attr = {}
			attr['release_name'] = release_name
			attr['requirements'] = requirements
			attr['sprint'] = sprint
			attr['week'] = week
			attr['domain'] = domain
			case.set_attr(**attr)
			case.get_attr()
			#print(case.test_name)
			ini_file = case.create_ini()
			if not debug:
				print('loading')
				case.case_update(ini_file)
	else:
		print('Abort')


def main():
	parse = argparse.ArgumentParser()
	parse.add_argument('--nightly_release_name', help='nightly_release_name', dest='nightly_release_name', required=True)
	parse.add_argument('--run_date', help='run_date', dest='run_date', required=True)
	parse.add_argument('--tag', help='tag', dest='tag', required=True)
	parse.add_argument('--release_name', help='release_name', dest='release_name', required=True)
	parse.add_argument('--requirements', help='requirements', dest='requirements', required=True)
	parse.add_argument('--sprint', help='sprint', dest='sprint', required=True)
	parse.add_argument('--week', help='week', dest='week', required=True)
	parse.add_argument('--test_suite', help='test_suite', dest='test_suite', required=False)
	parse.add_argument('--status', help='status', dest='status', required=False)
	parse.add_argument('--tester', help='tester', dest='tester', required=False)
	parse.add_argument('--component', help='component', dest='component', required=False)
	parse.add_argument('--debug', help='debug', dest='debug', nargs='?', const=1, type=int, required=False)
	parse.add_argument('--nightly_sprint', help='nightly_sprint', dest='nightly_sprint', required=False)
	parse.add_argument('--domain', help='domain', dest='domain', required=False)
	parse.add_argument('--key', help='key', dest='key', required=False)

	args = parse.parse_args()
	nightly_release_name = args.nightly_release_name
	run_date = args.run_date
	tag = args.tag
	release_name = args.release_name
	requirements = args.requirements
	# release sprint
	sprint = args.sprint
	# release run date
	week = args.week

	if args.test_suite:
		test_suite = args.test_suite
	else:
		test_suite = ''

	if args.status:
		status = args.status
	else:
		status = 'Pass'

	if args.tester:
		tester = args.tester
	else:
		tester = ''

	if args.debug:
		print(args.debug)
		debug = args.debug
	else:
		debug = 0

	if args.component:
		component = args.component
	else:
		component = 'networking'

	if args.nightly_sprint:
		nightly_sprint = args.nightly_sprint
	else:
		nightly_sprint = 'Nightly'

	if args.domain:
		domain = args.domain
	else:
		domain = 'networking'

	if args.key:
		key = args.key
	else:
		key = ''



	result_load(nightly_release_name, nightly_sprint, run_date, tag, \
		test_suite, release_name, requirements, sprint, week, status, \
		tester, component, domain, key, debug)

if __name__ == '__main__':
	main()