#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import xlrd
import xlwt
import xlutils
import tempfile
from tempfile import NamedTemporaryFile
import shutil
import argparse
from datetime import datetime
from iPerf_run_database import find_data, update_iperf_data, get_config

dict_case = {}
list_smp = []

def get_rerun_cases(tr_type, test_suite, release, run_date):
	test_status = ['Fail', '"Not Started"', 'Blocked']
	rerun_file = 'rerun_cases.log'
	if os.path.exists(rerun_file):
		os.remove(rerun_file)
	for st in test_status:
		cmd = 'curl -F show_type={TYPE} -F release_name={RELEASE} -F filter_rundate={RUN_DATE} \
		-F filter_tr_domain=networking  -F filter_status={STATUS} -F show_fields=test_suite,test_name,tr_status \
		http://pek-lpgtest3.wrs.com/ltaf/show_result_fields.php >> {FILE}'.format(TYPE = tr_type, 
																				RELEASE = release, 
																				RUN_DATE = run_date, 
																				STATUS = st,
																				FILE = rerun_file)
		print(cmd)
		os.system(cmd)
	with open(rerun_file, 'r', encoding='utf-8') as f:
		for line in f:
			if line.split('|')[1].strip() == test_suite:
				print(line)
				list_smp.append(line.split('|')[0].strip())
	print(list_smp)

def read_plan(plan):
	rb = xlrd.open_workbook(plan,
			                formatting_info=True,
			                on_demand=True)
	ws = rb.sheet_by_index(0)
	cells_case_name = ws.col_slice(colx=2,
			          		 	start_rowx=1,
			          		 	end_rowx=5)
	for cell in cells_case_name:
		dict_case.setdefault(cell.value, plan)
	

def create_case_index(wassp_plan_path):
	path_plan = wassp_plan_path
	for name in os.listdir(path_plan):
		if name.endswith('.xls'):
			plan = os.path.join(path_plan, name)
			read_plan(plan)

def create_rerun_plan():
	list_smp_tmp = []

	for case in list_smp:
		if case in list_smp_tmp:
			continue
		plan = dict_case[case]
		print(plan)
		with NamedTemporaryFile('w+b') as f:
			f.name = os.path.basename(plan)
			shutil.copyfile(plan, f.name)
			rb = xlrd.open_workbook(f.name,
			                    	formatting_info=True,
			                    	on_demand=True)
			ws = rb.sheet_by_index(0)
			cells_case_name = ws.col_slice(colx=2,
			          		 			start_rowx=1,
			          		 			end_rowx=5)
			#for cell in cells_case_name:
			#	print(cell.value)
			cells_result = ws.col_slice(colx=3,
			          		 		start_rowx=1,
			          		 		end_rowx=5)
			#for cell in cells_result:
			#	print(cell.value)
			from xlutils.copy import copy
			wb = copy(rb)
			wb_ws = wb.get_sheet(0)
			x = 1
			for cell in cells_case_name:
				if cell.value not in list_smp:
					wb_ws.write(x,3,0)
				else:
					list_smp_tmp.append(cell.value)
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
		#return f.name	
def time_delta(run_date):
    y = datetime.strptime(run_date, '%Y-%m-%d')
    z = datetime.now()
    diff = z - y
    return diff.days - 1

def main():
	# test run type
	tr_type = 'nightly'
	test_suite = 'IPERF_UP'
	# rerun plan 存放目录
	workdir = '/mydisk/tmp/up'
	# 原始plan 位置
	path_plan = '/folk/hyan1/wassp/iPerf_up'

	parse = argparse.ArgumentParser()
	parse.add_argument('--dvd', help='dvd', dest='dvd', required=True)
	parse.add_argument('--rundate', help='rundate', dest='rundate', required=True)
	parse.add_argument('--release', help='ltaf release', dest='release', required=True)
	args = parse.parse_args()
	if time_delta(args.rundate) > 0:
		sys.exit(0)
	release_name = args.release
	run_date = args.rundate
	dvd = args.dvd
	
	shutil.rmtree(workdir)
	os.mkdir(workdir)
	os.chdir(workdir)

	# 遍历test_plan, case 名字作为key，test_plan作为value存入字典dict_case
	create_case_index(path_plan)
	#从ltaf上查询需要rerun的cases，存入列表list_smp
	get_rerun_cases(tr_type, test_suite, release_name, run_date)
	#生成rerun plan，存放到workdir
	create_rerun_plan()

	for file in os.listdir(workdir):
		if not file.endswith('.xls'):
			continue
		print('rerun {}'.format(file))
		# rerun plan
		rerun_plan = os.path.join(workdir, file)
		# 原始test plan
		wassp_plan = os.path.join(path_plan, file)
		dict_tmp = find_data(wassp_plan)
		print(dict_tmp['workspace'])
		wassp_home = '/home/windriver/wassp-repos'
		workspace = dict_tmp['workspace']
		dict_config = get_config(wassp_plan)
		board = dict_config['Board']
		time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
		dir_name = 'log_{TIME}_{BOARD}'.format(TIME = time, BOARD = board)
		logs = os.path.join('/home/windriver/Logs', dir_name)
		if not os.path.exists(logs):
			os.makedirs(logs)
			os.system('ln -s {LOGS} {TARGET}'.format(LOGS = logs, TARGET = '/var/www/html'))
		
		command = 'runwassp -f {WASSP_PLAN} -E "WASSP_WIND_HOME={WASSP_WIND_HOME}"  -E "WASSP_HOME={WASSP_HOME}" -E "WASSP_WORKSPACE_HOME={WASSP_WORKSPACE_HOME}" -E "WASSP_LOGS_HOME={WASSP_LOGS_HOME}" --continueIfReleaseInvalid -s exec --exec-retries 5'.format(WASSP_PLAN = rerun_plan, WASSP_WIND_HOME = dvd, WASSP_HOME = wassp_home, WASSP_WORKSPACE_HOME = workspace, WASSP_LOGS_HOME = logs)
		os.system(command)
		upload_command = 'python3 /folk/hyan1/Nightly/common/load_ltaf.py --log {LOG} --rundate {RUNDATE} --release {RELEASE}'.format( LOG= logs, RUNDATE = run_date, RELEASE = release_name)
		os.system(upload_command)
		update_iperf_data(wassp_plan, run_date, logs)

if __name__ == '__main__':
	main()

