#!/usr/bin/env python3
# coding: utf-8

import sys
sys.path.append('/folk/hyan1/')
import pymongo
from Nightly.common.connect import Connect
from fnmatch import fnmatch
import os
from Nightly.common.get_data import get_throughput
import xlrd


def insert_data(plan, log_path, workspace):
	conn = Connect.get_connection()
	mydb = conn.rerun_db
	mycol = mydb.rerun_up_tb
	plan_file = os.path.basename(plan)
	mydict = {"plan":plan_file, "log_path":log_path, "workspace":workspace}
	mycol.insert_one(mydict)
	#for rec in mycol.find():
	#	print(rec)

def delete_data():
	conn = Connect.get_connection()
	mydb = conn.rerun_db
	mycol = mydb.rerun_up_tb
	mycol.delete_many({})
	#conn.close()

def find_data(plan):
	conn = Connect.get_connection()
	mydb = conn.rerun_db
	mycol = mydb.rerun_up_tb
	plan_file = os.path.basename(plan)
	myquery = {"plan":plan_file}
	print(myquery)
	print(mycol.find_one(myquery))
	return mycol.find_one(myquery)

def get_config(plan):
	dict_config = {}
	rb = xlrd.open_workbook(plan,
							formatting_info=True,
							on_demand=True)
	ws = rb.sheet_by_index(0)
	config_info = ws.col_slice(colx=0,
							   	start_rowx=30,
							   	end_rowx=35)
	for cell in config_info:
		list_config = cell.value.split('=')
		dict_config.setdefault(list_config[0], list_config[1])
	return dict_config

def insert_iperf_data(plan, run_date, spin, log_path):
	conn = Connect.get_connection()
	mydb = conn.iperf_db
	mycol = mydb.iperf_up_tb
	dict_data = get_log_data(log_path)
	dict_config = get_config(plan)
	#print(dict_data)
	#get_config(plan)
	mydict = {"run_date":run_date, "spin":spin, "board":dict_config['Board'], "Bits":dict_config['Bits'], "Mode":dict_config['Mode'], "CPU":dict_config['CPU'], "BSP":dict_config['BSP'], "TCP_64":dict_data['TCP_64'], "TCP_1024":dict_data['TCP_1024'], "TCP_65536":dict_data['TCP_65536'], "UDP_1400":dict_data['UDP_1400']}
	print(mydict)
	mycol.insert_one(mydict)

def insert_baseline_data(plan, spin, log_path):
	conn = Connect.get_connection()
	mydb = conn.iperf_db
	mycol = mydb.iperf_up_bl_tb
	dict_data = get_log_data(log_path)
	dict_config = get_config(plan)
	mydict = {"spin":spin, "board":dict_config['Board'], "Bits":dict_config['Bits'], "Mode":dict_config['Mode'], "CPU":dict_config['CPU'], "BSP":dict_config['BSP'], "TCP_64":dict_data['TCP_64'], "TCP_1024":dict_data['TCP_1024'], "TCP_65536":dict_data['TCP_65536'], "UDP_1400":dict_data['UDP_1400']}
	print(mydict)
	mycol.insert_one(mydict)

def update_iperf_data(plan, run_date, log_path):
	conn = Connect.get_connection()
	mydb = conn.iperf_db
	mycol = mydb.iperf_up_tb
	dict_data = get_rerunlog_data(log_path)
	print(dict_data)
	dict_config = get_config(plan)
	myquery = {"board":dict_config['Board'], "run_date":run_date}
	if dict_data:
		mycol.update_many(myquery,{"$set":dict_data})

def get_rerunlog_data(log_path):
	dict_data = {}
	for dirpath, dirnames, filenames in os.walk(log_path):
			for filename in filenames:
				if fnmatch(filename, 'target.log'):
					dict_filter = get_throughput(os.path.join(dirpath, filename))
					if dict_filter['frame'] == '64':
						dict_data['TCP_64'] = dict_filter['sender']
					elif dict_filter['frame'] == '1024':
						dict_data['TCP_1024'] = dict_filter['sender']
					elif dict_filter['frame'] == '65536':
						dict_data['TCP_65536'] = dict_filter['sender']
					elif dict_filter['frame'] == '1400':
						dict_data['UDP_1400'] = dict_filter['sender']
	return dict_data

def get_log_data(log_path):
	dict_data = {}
	for dirpath, dirnames, filenames in os.walk(log_path):
			for filename in filenames:
				if fnmatch(filename, 'target.log'):
					dict_filter = get_throughput(os.path.join(dirpath, filename))
					if dict_filter['frame'] == '64':
						dict_data['TCP_64'] = dict_filter['sender']
					elif dict_filter['frame'] == '1024':
						dict_data['TCP_1024'] = dict_filter['sender']
					elif dict_filter['frame'] == '65536':
						dict_data['TCP_65536'] = dict_filter['sender']
					elif dict_filter['frame'] == '1400':
						dict_data['UDP_1400'] = dict_filter['sender']
	for frame in ['TCP_64','TCP_1024','TCP_65536','UDP_1400']:
		dict_data.setdefault(frame,0)
	return dict_data

if __name__ == '__main__':
	plan = "/folk/hyan1/wassp/ia_18180_idpQ35.xls"
	log_path = "/home/windriver/Logs/log_2018_09_07_16_47_24"
	run_date = '2018-09-07'
	spin = 'vx20180905131602_vx7-native'
	#log_path = "/home/windriver/Logs/log_2018_09_01_21_26_42"
	#workspace = "/home/windriver/Workspace/log_2018_09_01_21_26_42"
	delete_data()
	#insert_iperf_data(plan, run_date, spin, log_path)
	#find_data('/folk/hyan1/wassp/ia_18180_idpQ35.xls')
	#update_iperf_data(plan, run_date, log_path)