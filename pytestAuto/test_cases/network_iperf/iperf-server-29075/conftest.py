#!/usr/bin/env python3
# encoding=utf-8
# @Author = xiaozhan Li
# @Time = 10/31/2022 12:48 PM
# @Email = lxz_20081025@163.com
# @Name = conftest-xiaozhan.py
import pytest
import allure
import os

from utils.image import image_type
from utils.hm_21_paramiko_class_ssh import client_cmd_29075
from utils.read_yaml import read_yaml

@pytest.fixture(scope='session', autouse=True)
def fixture_image_28610():
    with allure.step('Build IPERF image for ZCU102 target 28610'):
        res = read_yaml('config/debug.yaml')
        debug = res['debug']
        build_image = res['build_image']
        if debug is True:
            if build_image is True:
                os.system(r'/home/xli3/pytestAuto/utils/buildZCU102_Branch.sh')
            else:
                pass
        else:
            os.system(r'/home/xli3/pytestAuto/utils/buildZCU102.sh')

    with allure.step('Check image for ZCU102'):
        image = image_type('ZCU102')
        # check what will happen if assert fails
        assert image == 'ZCU102'
    yield image
    pass   # It is just a placeholder


@pytest.fixture(scope='session', autouse=True)
def fixture_iperf():
    # Start IPERF on Ubuntu server. Setup before test starts
    cmd_input = 'pkill iperf3'
    client_cmd_29075.run_ssh(cmd_input)
    cmd_input = 'iperf3 -s -p 10000 &'
    client_cmd_29075.run_ssh(cmd_input)
    yield
    # Teardown after test session finishes
    cmd_input = 'pkill iperf3'
    client_cmd_29075.run_ssh(cmd_input)
    client_cmd_29075.close()


