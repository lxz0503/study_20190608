#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/17/2024 9:35 AM
@file:conftest.py
"""
import pytest
import allure

from utils.image import image_type
from utils.read_yaml import read_yaml
from utils.vxBuild import buildVxworks, copyVxImage


@pytest.fixture(scope='session', autouse=True)
def fixture_image_ntp(spin=False, build_image=False):
    if spin:
        installPath = '/home/xli3/SPIN/vx20240116114147_vx_2403'      # xiaozhan, this is only for SPIN
    else:
        installPath = '/home/xli3/vxworks'      # xiaozhan debug, this is for branch
    cfg = read_yaml('config/vxBuildConfigNTP.yaml')
    bsp = 'itl_generic'
    tool = 'llvm'
    smp = True
    m64bit = True
    debug = False
    cpu = 'SKYLAKE'
    ipv6 = True
    # xiaozhan, debug
    if build_image is True:
        buildVxworks(cfg['NTP'], installPath, bsp, tool, smp, m64bit, cpu, ipv6, spin)  # xiaozhan, debug
        copyVxImage('./%s_vip/default' % bsp, '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-ntp')
    else:
        pass

    with allure.step('Check image for IA'):
        image = image_type('IA')
        assert image == 'IA'
    yield image
    pass
