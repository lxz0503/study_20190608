#!/usr/bin/env python3
# encoding=utf-8
"""
@author:Xiaozhan Li
@Email:lxz_20081025@163.com
@time:11/17/2022 8:16 PM
@project:HCAPI
"""
import pandas as pd
import nightlyInfo
import configparser
import os

# if you are not using jenkins
# dir_list = sorted(os.listdir('../report'))
# print(dir_list[-1])
# report_dir = '../report/' + dir_list[-1]

# if you are using jenkins, the report dir is
# /home/wrsadmin/Jenkins/workspace/TSN0/allure-report/data/suites.csv

csv_log = '/home/xli3/Jenkins/workspace/pytestAuto/report_trial/data/suites.csv'
df = pd.read_csv(csv_log)
# df.to_excel('tsn_case.xlsx')
# print(df.head())
df = df[['Name', 'Status']]
# print(df.values)   # 

status = "Fail"
function_pass = '0'
function_fail = '0'
for test_name, case_status in df.values:
    print(test_name, case_status)
    if case_status == "passed":
        status = "Pass"
        function_pass = '1'
    elif case_status == "failed":
        status = "Fail"
        function_fail = '1'
    elif case_status == 'skipped':
        status = "Not run"
        function_fail = '1'
    else:
        print('Unknown status')
    # TODO upload LTAF
    nightly_date, release_name, spin = nightlyInfo.nightlyInfo()
    log = 'http://pek-cc-pb08l.wrs.com/vxtest/vxtest1/LOG_VX7/Vx-7_Networking/vx7-SR0610-features/F10020'
    config = configparser.ConfigParser()
    config.read("original_nightly.ini")
    config.set("LTAF", "test_name", test_name)
    config.set("LTAF", "status", status)
    config.set("LTAF", "function_pass", function_pass)
    config.set("LTAF", "function_fail", function_fail)
    config.set("LTAF", "spin", spin)
    config.set("LTAF", "Logs", log)
    config.set("LTAF", "week", nightly_date)
    config.set("LTAF", "release_name", release_name)
    config.write(open('original_nightly.ini', "r+"))

    # os.system(
    #     "curl -F resultfile=@/home/windriver/ANVL/original_nightly.ini http://pek-lpgtest3.wrs.com/ltaf/upload_nightly_results.php")
    # os.system("cp /home/windriver/ANVL/LTAF/original_nightly.ini /home/windriver/ANVL")

#
# [xli3@pek-vx-29075 utils]$ cat /folk/vxMW/nightly/jenkinsEnvInjection/configs/vx7_ci_nightly_spin.config
# NIGHTLYSPIN=vx20221120020016_vx_2303
# lastS=vx20221119020017_vx_2303
# LTAFRELEASE=vx7-integration-native
# timestamp=20221121172227
# PatchBranch=vx7-integration


    # with open(spinConfig, 'r') as fd:
    #     content = fd.read()
    #     found = re.search('%s=(.*?)\n' % name, content)
    #     if found is not None:
    #         return found.groups()[0].strip()
    #     else:
    #         return ''

# parser timestamp --- 20221121172227
# return time.strftime('%Y-%m-%d', time.strptime(tsStr, '%Y%m%d%H%M%S'))
