#!/usr/bin/env python3
# coding: utf-8
# 
import os.path
import argparse
from datetime import datetime
from iPerf_run_database import find_data, update_iperf_data


def main():
	parse = argparse.ArgumentParser()
	#parse.add_argument('--log', help='rerun log path', dest='log', required=True)
	parse.add_argument('--plan', help='test plan', dest='plan', required=True)
	#parse.add_argument('--workspace', help='workspace', dest='workspace', required=True)
	parse.add_argument('--dvd', help='dvd', dest='dvd', required=True)
	parse.add_argument('--rundate', help='rundate', dest='rundate', required=True)
	parse.add_argument('--release', help='ltaf release', dest='release', required=True)
	args = parse.parse_args()
	plan = args.plan
	dict_tmp = find_data(plan)
	print(dict_tmp['workspace'])
	wassp_home = '/home/windriver/wassp-repos'
	workspace = dict_tmp['workspace']
	dvd = args.dvd
	dir_name = 'log_{:%Y_%m_%d_%H_%M_%S}'.format(datetime.now())
	logs = os.path.join('/home/windriver/Logs', dir_name)
	if not os.path.exists(logs):
		os.makedirs(logs)
		os.system('ln -s {LOGS} {TARGET}'.format(LOGS = logs, TARGET = '/var/www/html'))
	command = 'runwassp -f {WASSP_PLAN} -E "WASSP_WIND_HOME={WASSP_WIND_HOME}"  -E "WASSP_HOME={WASSP_HOME}" -E "WASSP_WORKSPACE_HOME={WASSP_WORKSPACE_HOME}" -E "WASSP_LOGS_HOME={WASSP_LOGS_HOME}" --continueIfReleaseInvalid -s exec --exec-retries 5'.format(WASSP_PLAN = plan, WASSP_WIND_HOME = dvd, WASSP_HOME = wassp_home, WASSP_WORKSPACE_HOME = workspace, WASSP_LOGS_HOME = logs)
	os.system(command)
	sprint = 'Nightly'
	#week = '{:%Y-%m-%d}'.format(datetime.now())
	week = args.rundate
	release = args.release
	#release = 'vxworks_sandbox'
	domain = 'networking'
	#upload_command = 'bash /home/windriver/wassp-repos/testcases/vxworks7/LTAF_meta/ltaf_vxworks.sh -sprint "{SPRINT}" -week {WEEK} -ltaf {LTAF} -log {LOG} -domain {DOMAIN} -nightly'.format(SPRINT = sprint, WEEK = week, LTAF = release, LOG = logs, DOMAIN = domain) 
	upload_command = 'python3 /folk/hyan1/Nightly/common/load_ltaf.py --log {LOG} --rundate {RUNDATE} --release {RELEASE}'.format( LOG= logs, RUNDATE = week, RELEASE = release)
	os.system(upload_command)
	update_iperf_data(plan, week, logs)
if __name__ == '__main__':
	main()