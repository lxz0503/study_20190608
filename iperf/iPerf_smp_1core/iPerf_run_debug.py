#!/usr/bin/env python3
# coding: utf-8
# 
import os
import sys
sys.path.append('/folk/hyan1/')
from datetime import datetime
import argparse
import xlrd
from itertools import compress
from Nightly.common.connect import Connect
from iPerf_run_database import get_log_data, get_config
import logging
import re
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)

case_name = ''
def get_baseline(plan):
	global case_name
	case_run, mode = read_plan(plan)
	board_name, case_name = case_run.split('.')
	logging.info('=' * 60)
	print(mode, board_name, case_name)
	conn = Connect.get_connection()
	mydb = conn.iperf_db
	if mode == 'smp':
	    mycol = mydb.iperf_smp_bl_tb
	if mode == 'up':
	    mycol = mydb.iperf_up_bl_tb
	if mode == 'smp_1core':
	    mycol = mydb.iperf_smp_1core_bl_tb
	myquery = {"board":board_name}
	#print(mycol.find_one(myquery)[case_name])
	return mycol.find_one(myquery)[case_name]

def read_plan(plan):
	list_case = []
	list_flag = []
	rb = xlrd.open_workbook(plan,
			                formatting_info=True,
			                on_demand=True)
	ws = rb.sheet_by_index(0)
	cells_case_name = ws.col_slice(colx=2,
			          		 	start_rowx=1,
			          		 	end_rowx=5)
	cell_case_flag = ws.col_slice(colx=3,
								start_rowx=1,
								end_rowx=5)
	for cell in cells_case_name:
		list_case.append(cell.value)
	for flag in cell_case_flag:
		list_flag.append(int(flag.value))
	logging.info(list_case)
	logging.info(list_flag)
	case_run = list(compress(list_case, list_flag))[0]
	logging.info(case_run)
	mode = re.search(r'config_label=(\w+)', ws.cell_value(0,3)).group(1)
	logging.info(mode)
	return case_run, mode

def main():
	parse = argparse.ArgumentParser()
	parse.add_argument('--plan', help='wassp test plan', dest='plan', required=True)
	parse.add_argument('--dvd', help='the spin to test', dest='dvd', required=True)
	args = parse.parse_args()
	wassp_plan = args.plan
	dict_config = get_config(wassp_plan)
	board = dict_config['Board']
	time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
	dir_name = 'log_{TIME}_{BOARD}'.format(TIME = time, BOARD = board)
	dvd = args.dvd
	wassp_home = '/buildarea1/hyan1/wassp-repos'
	workspace = os.path.join('/net/pek-vx-nwk1/buildarea1/hyan1/Workspace', dir_name)
	if not os.path.exists(workspace):
		os.makedirs(workspace)
	logs = os.path.join('/net/pek-vx-nwk1/buildarea1/hyan1/Logs', dir_name)
	if not os.path.exists(logs):
		os.makedirs(logs)
		os.system('ln -s {LOGS} {TARGET}'.format(LOGS = logs, TARGET = '/var/www/html'))
	
	#insert_data(wassp_plan, logs, workspace)
	# run on git
	if os.path.dirname(dvd).endswith('hyan1'):
		command = 'runwassp -f {WASSP_PLAN} -E "WASSP_HOME={WASSP_HOME}" -E "WASSP_WORKSPACE_HOME={WASSP_WORKSPACE_HOME}" -E "WASSP_LOGS_HOME={WASSP_LOGS_HOME}" -E "WASSP_VXWORKS_INSTALL_BASE={WASSP_WIND_HOME}" -E "WASSP_VXWORKS_VERNUM=7" -E "WASSP_VXWORKS_VER=helix" -E "WASSP_VXWORKS_TYPE=vxworks" --continueIfReleaseInvalid --exec-retries 3'.format(WASSP_PLAN = wassp_plan, WASSP_WIND_HOME = dvd, WASSP_HOME = wassp_home, WASSP_WORKSPACE_HOME = workspace, WASSP_LOGS_HOME = logs)
		print('============= {}'.format(command))
	# run on spin
	else:
		command = 'runwassp -f {WASSP_PLAN} -E "WASSP_WIND_HOME={WASSP_WIND_HOME}"  -E "WASSP_HOME={WASSP_HOME}" -E "WASSP_WORKSPACE_HOME={WASSP_WORKSPACE_HOME}" -E "WASSP_LOGS_HOME={WASSP_LOGS_HOME}" --continueIfReleaseInvalid --exec-retries 3'.format(WASSP_PLAN = wassp_plan, WASSP_WIND_HOME = dvd, WASSP_HOME = wassp_home, WASSP_WORKSPACE_HOME = workspace, WASSP_LOGS_HOME = logs)
		print('============= {}'.format(command))
	# run wassp
	os.system(command)
	
	dict_data = get_log_data(logs)
	base = get_baseline(wassp_plan)

	print(float(dict_data[case_name]))
	print(base)
	print(float(dict_data[case_name]) / float(base))
	print(dict_data)

	if float(dict_data[case_name]) / float(base) < 0.9:
    	# fail
		dict_data.setdefault('result',1)
		exit(1)
	else:
        # pass
		dict_data.setdefault('result',0)
		exit(0)
	
	#upload_command = 'python3 /folk/hyan1/Nightly/common/load_ltaf.py --log {LOG} --rundate {RUNDATE} --release {RELEASE}'.format( LOG= logs, RUNDATE = week, RELEASE = release)
	#os.system(upload_command)
	#insert_iperf_data(wassp_plan, week, os.path.basename(dvd), logs)
	#insert_baseline_data(wass/folk/hyan1/wassp/iPerf_smp/03_fsl_arm_25005_imx6_sabrelite.xlsp_plan, os.path.basename(dvd), logs)

if __name__ == '__main__':
	main()
    
