#!/usr/bin/env python3
# encoding=utf-8
"""
@author:Xiaozhan Li
@Email:lxz_20081025@163.com
@time:10/29/2022 3:17 PM
@project:HCAPI
"""
import pytest
import sys
import os

# modify sys.path to avoid module import error
project_root_dir = os.path.dirname(os.path.realpath(__file__))
if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

from utils.nightlyInfo import nightlyInfo
from utils.read_yaml import read_yaml

if __name__ == '__main__':
    res = read_yaml('config/debug.yaml')
    debug = res['debug']
    print(f'debug is {debug}')
    if debug is True:
        # pytest will be running in parallel and use the local branch instead of spin
        pytest.main(['-vs', '--alluredir=./allure_trial', '--clean-alluredir', '--reruns=1', '-n=auto'])
        # os.system('allure generate ./allure_trial/ -o ./report_trial/ --clean')
        # os.system('allure open ./report_trial')
    else:
        # Check if there is new spin.If no, it will stop and not run pytest
        nightly_date, release_name, spin, branch = nightlyInfo()
        print(f'{nightly_date},{release_name},{spin},{branch}')
        pytest.main(['-vs', '--alluredir=./allure_trial', '--clean-alluredir', '--reruns=1'])
