#!/usr/bin/env python3
# coding: utf-8
# 
import os.path
import argparse
import time
from datetime import datetime
import json
import shutil
from tempfile import NamedTemporaryFile
import xlrd
import xlwt
import xlutils
from iPerf_run_database import find_data, update_iperf_data, get_config
import sys

dict_case = {}

def create_case_result(file):
    global dict_case
    with open(os.path.join(file,'Summary/details.json'), 'r') as f:
    	data = json.load(f)
    	for case in data:
    		#print('%s:%s' %(case.split('/')[5], data[case]))
    		dict_case.setdefault(case.split('/')[5], data[case])

def create_rerun_plan(file, plan):
	create_case_result(file)
	with NamedTemporaryFile('w+b') as f:
		f.name = os.path.basename(plan)
		#print('filename is:', f.name)
		shutil.copy(plan, f.name)
		rb = xlrd.open_workbook(f.name,
			                    formatting_info=True,
			                    on_demand=True)
		ws = rb.sheet_by_index(0)
		cells_case_name = ws.col_slice(colx=2,
			          		 start_rowx=1,
			          		 end_rowx=5)
		for cell in cells_case_name:
			print(cell.value)
		cells_result = ws.col_slice(colx=3,
			          		 start_rowx=1,
			          		 end_rowx=5)
		for cell in cells_result:
			print(cell.value)
		from xlutils.copy import copy
		wb = copy(rb)
		wb_ws = wb.get_sheet(0)
		x = 1
		for cell in cells_case_name:
			if cell.value in dict_case and dict_case[cell.value] == 'PASS':
				wb_ws.write(x,3,0)
			x = x+1
		wb.save(f.name)	
		rb = xlrd.open_workbook(f.name,
			                    formatting_info=True,
			                    on_demand=True)
		ws = rb.sheet_by_index(0)
		cells_case_name = ws.col_slice(colx=2,
			          		 start_rowx=1,
			          		 end_rowx=5)
		for cell in cells_case_name:
			print(cell.value)
		cells_result = ws.col_slice(colx=3,
			          		 start_rowx=1,
			          		 end_rowx=5)
		for cell in cells_result:
			print(cell.value)
		for item in dict_case:
			print('%s:%s' %(item, dict_case[item]))
	return f.name	

def time_delta(run_date):
    y = datetime.strptime(run_date, '%Y-%m-%d')
    z = datetime.now()
    diff = z - y
    return diff.days - 1

def main():
	parse = argparse.ArgumentParser()
	#parse.add_argument('--log', help='rerun log path', dest='log', required=True)
	parse.add_argument('--plan', help='test plan', dest='plan', required=True)
	#parse.add_argument('--workspace', help='workspace', dest='workspace', required=True)
	parse.add_argument('--dvd', help='dvd', dest='dvd', required=True)
	parse.add_argument('--rundate', help='rundate', dest='rundate', required=True)
	parse.add_argument('--release', help='ltaf release', dest='release', required=True)
	args = parse.parse_args()
	if time_delta(args.rundate) > 0:
		sys.exit(0)
	wassp_plan = args.plan
	dict_tmp = find_data(wassp_plan)
	print(dict_tmp['workspace'])
	wassp_home = '/home/windriver/wassp-repos'
	workspace = dict_tmp['workspace']
	log_path = dict_tmp['log_path']
	rerun_plan = create_rerun_plan(log_path, wassp_plan)
	dvd = args.dvd
	dict_config = get_config(wassp_plan)
	board = dict_config['Board']
	timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
	dir_name = 'log_{TIME}_{BOARD}'.format(TIME = timestamp, BOARD = board)
	logs = os.path.join('/home/windriver/Logs', dir_name)
	if not os.path.exists(logs):
		os.makedirs(logs)
		os.system('ln -s {LOGS} {TARGET}'.format(LOGS = logs, TARGET = '/var/www/html'))
	command = 'runwassp -f {WASSP_PLAN} -E "WASSP_WIND_HOME={WASSP_WIND_HOME}"  -E "WASSP_HOME={WASSP_HOME}" -E "WASSP_WORKSPACE_HOME={WASSP_WORKSPACE_HOME}" -E "WASSP_LOGS_HOME={WASSP_LOGS_HOME}" --continueIfReleaseInvalid -s exec --exec-retries 5'.format(WASSP_PLAN = rerun_plan, WASSP_WIND_HOME = dvd, WASSP_HOME = wassp_home, WASSP_WORKSPACE_HOME = workspace, WASSP_LOGS_HOME = logs)
	os.system(command)
	#sprint = 'Nightly'
	#week = '{:%Y-%m-%d}'.format(datetime.now())
	#week = 'week'+str(datetime.now().isocalendar()[1])
	week = 'week'+time.strftime('%y',time.localtime())+'{:0>2s}'.format(str(datetime.now().isocalendar()[1]))
	release = args.release
	#release = 'vxworks_sandbox'
	domain = 'networking'
	#upload_command = 'bash /home/windriver/wassp-repos/testcases/vxworks7/LTAF_meta/ltaf_vxworks.sh -sprint "{SPRINT}" -week {WEEK} -ltaf {LTAF} -log {LOG} -domain {DOMAIN} -nightly'.format(SPRINT = sprint, WEEK = week, LTAF = release, LOG = logs, DOMAIN = domain) 
	upload_command = 'python3 /folk/hyan1/Nightly/common/load_ltaf.py --log {LOG} --rundate {RUNDATE} --release {RELEASE} --sprint Weekly'.format( LOG= logs, RUNDATE = week, RELEASE = release)
	os.system(upload_command)
	update_iperf_data(wassp_plan, week, logs)
if __name__ == '__main__':
	main()