#!/usr/bin/env python3
# encoding=utf-8
"""
@author:xli3
@time:3/12/2024 12:14 PM
@file:conftest.py
"""

import pytest
import allure
import sys

sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.image import image_type
from utils.read_yaml import read_yaml
from utils.vxBuild import buildVxworks, copyVxImage


@pytest.fixture(scope='session', autouse=True)
def fixture_image_ftp(spin=False, build_image=False):
    if spin is True:
        installPath = '/home/xli3/SPIN/vx20240216144442_vx_2409'  # xiaozhan, this is only for SPIN
    else:
        installPath = '/home/xli3/vxworks'  # xiaozhan debug, this is for branch
    cfg = read_yaml('config/vxBuildConfigFTP.yaml')
    bsp = 'itl_generic'
    tool = 'llvm'
    smp = True
    m64bit = True
    debug = False
    cpu = 'SKYLAKE'
    ipv6 = True
    # module = 'FTP'
    module = None
    # xiaozhan, debug
    if build_image is True:
        buildVxworks(cfg['FTP'], installPath, bsp, tool, smp, m64bit, cpu, ipv6, module, spin)  # xiaozhan, debug
        # copyVxImage('./%s_vip/default' % bsp, '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-crypto')
        copyVxImage('/home/xli3/vxworks/%s_vip/default' % bsp,
                    '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-ftp')  # xiaozhan, debug
    else:
        pass

    with allure.step('Check image for IA'):
        image = image_type('IA')
        assert image == 'IA'
    yield image
    pass


if __name__ == "__main__":
    pass
