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
sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.nightlyInfo import nightlyInfo

if __name__ == '__main__':
    # run pytest
    # pytest.main(['-vs', '--alluredir=./allure_trial', '--clean-alluredir', '--reruns=1', '--dist', 'loadfile'])
    pytest.main(['-vs', '--alluredir=./allure_trial', '--clean-alluredir', '--reruns=1', '-n=auto'])
    # os.system('allure generate ./allure_trial/ -o ./report_trial/ --clean')
    # os.system('allure open ./report_trial')
    
