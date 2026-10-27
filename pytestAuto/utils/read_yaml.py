#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:8/18/2022 10:08 AM
@file:read_yaml.py
@project:xiaozhan_git
"""
import yaml
import os
import sys
#sys.path.insert(0, '/home/xli3/pytestAuto')

def get_prj_path():
    return os.path.dirname(os.path.dirname(__file__)) + '/'


def read_yaml(yaml_path):
    print(get_prj_path())
    # with open(get_prj_path() + yaml_path) as f:   # this is for windows, default project path is pytestAuto
    with open(yaml_path) as f:               # this is for linux, run this under /home/xlie/pytestAuto
        # data = yaml.load(f, Loader=yaml.FullLoader)
        data = yaml.safe_load(f)
    return data


if __name__ == '__main__':
    #print(get_prj_path())
    # res = read_yaml('config/debug.yaml')
    res = read_yaml('config/vxBuildConfig_tsn.yaml')
    # vsbConfigCmd = '/home/wrsadmin/SPIN/vx20240109165519_vx_2403/wrenv.linux -p vxworks/24.03 LM_LICENSE_FILE=27000@ala-lic4.wrs.com'
    vsbConfigCmd = '/home/xli3/vxworks/wrenv.linux -p vxworks/relx vxprj vsb config -s'

    if 'layer' in res['RTNET']['vsb']:
        for c in res['RTNET']['vsb']['layer']:
            vsbConfigCmd += ' -add _WRS_CONFIG_%s=y' % c.upper()

    print(vsbConfigCmd)
