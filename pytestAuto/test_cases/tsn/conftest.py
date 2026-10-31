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
from utils.read_yaml import read_yaml


@pytest.fixture(scope='session', autouse=True)  # annotate this line if debug
def fixture_image():
    with allure.step('Build TSN image for IA'):
        res = read_yaml('config/debug.yaml')
        debug = res['debug']
        build_image = res['build_image']
        if debug is True:
            if build_image is True:
                os.system(r'/home/xli3/pytestAuto/utils/buildIA_BranchTSN.sh')
            else:
                pass
        else:
            os.system(r'/home/xli3/pytestAuto/utils/buildIA-TSN-PERF.sh')
       
    with allure.step('Check image for IA'):
        image = image_type('IA')
        assert image == 'IA'
    yield image
    # TODO xiaozhan,
    pass
