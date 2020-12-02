#!/usr/bin/env python3
# coding: utf-8

import sys
sys.path.append('/folk/hyan1/')
import argparse
import re
from Nightly.common.connect import Connect

def get_baseline(case_path):
    pat = re.compile(r'iperf_(.*)')
    mode = case_path.split('/')[-2].lower()
    m = pat.search(mode)
    try:
        mode_name = m.group(1)
    except AttributeError as e:
        print('AttributeError:', e)
        mode_name = 'smp'
    case = case_path.split('/')[-1]
    board_name, case_name = case.split('.')
    #print(mode_name, board_name, case_name)
    conn = Connect.get_connection()
    mydb = conn.iperf_baseline_db
    if mode_name == 'smp':
        mycol = mydb.iperf_smp_bl_tb
    if mode_name == 'up':
        mycol = mydb.iperf_up_bl_tb
    if mode_name == 'smp_1core':
        mycol = mydb.iperf_smp_1core_bl_tb
    myquery = {"board":board_name}
    #print(type(mycol.find_one(myquery)[case_name]))
    data = mycol.find_one(myquery)
    criteria = '{}_{}'.format(case_name, 'criteria')
    return case_name, data[case_name], data[criteria]


def get_throughput(log):
    """
    """

    dict_data = {}
    with open(log,'r') as f:
        pat = re.compile(r'iperf3.*-l\s(\d+)')
        for line in f:
            line = line.strip()
            m = pat.search(line)
            # get the package length
            if m:
                dict_data.setdefault('frame',m.group(1))
                continue
            # get the TCP throughput
            if line.endswith('Mbits/sec'):
                data = line.split()[-2]
                dict_data.setdefault('sender', data)
                break
            #if line.endswith('sender'):
            #    data = line.split()[-3]     
            #    dict_data.setdefault('sender',data)
            #if line.endswith('receiver'):
            #    data = line.split()[-3]
            #    dict_data.setdefault('receiver',data)
            # get UDP throughput of iperf 3.1.3
            if line.endswith('%)'):
                data = line.split()[-6]
                dict_data.setdefault('sender',data)
                break
            # get UDP throughput of iperf 3.7
            if line.endswith('sender'):
                data = line.split()[-7]
                dict_data.setdefault('sender',data)   
                break
            
    return dict_data

if __name__ == '__main__':

    parse = argparse.ArgumentParser()
    parse.add_argument('-f', '--file', help='log file to process', dest='filename', required=True)
    parse.add_argument('-p', '--path', help='the case path', dest='casepath', required=True)
    args = parse.parse_args()
  
    log = args.filename
    case_path = args.casepath
    dict_data = get_throughput(log)
    case_name, base, criteria = get_baseline(case_path)

    if float(dict_data['sender']) / float(base) < float(criteria):
        # fail
        dict_data.setdefault('result',1)
    else:
        # pass
        dict_data.setdefault('result',0)
    print(float(dict_data['sender']))
    print(base)
    print(float(dict_data['sender']) / float(base))
    print(dict_data)
  
