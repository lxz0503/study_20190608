#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:1/15/2024 2:14 PM
@file:get-vx-env.py
"""
import os


def getVxworksEnv(installPath):
    if os.path.exists(installPath + '/vxworks'):
        wrenvPrefix = '%s/wrenv.sh -p vxworks' % installPath
        # get pkgs_path from $WIND_PKGS
        cmd = wrenvPrefix + ' env | grep WIND_PKGS='
        lines = os.popen(cmd).readlines()
        pkgsPath = lines[0].strip().lstrip('WIND_PKGS=')
    else:
        raise BaseException('%s not correct since vxworks was not found' % installPath)
    return pkgsPath, wrenvPrefix


if __name__ == "__main__":
    # print(getVxworksEnv('/home/xli3/vxworks'))
    builds = ['vxBuild'] * 6
    print(builds)

    # [xli3@pek-vx-29075 common]$ python3 get-vx-env.py
    # ('/home/xli3/vxworks/vxworks/relx/source/os', '/home/xli3/vxworks/wrenv.sh -p vxworks')
