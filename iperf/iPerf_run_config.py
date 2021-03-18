#!/usr/bin/env python3
# coding: utf-8
# 

import os
from datetime import datetime

def get_dvd():
    spinfile = '/net/pek-vx-system1/buildarea1/yliu2/nightly/spinReady'
    #spinfile = '/net/pek-vx-system1/buildarea1/hyan1/wassp/spinReady'
    if os.path.exists(spinfile):
        with open(spinfile,'rt') as f:
            for line in f:
                testspin = line
        dvdpath = os.path.join('/net/pek-vx-system1/buildarea1/yliu2/nightly', testspin)
        return dvdpath.strip()
    else:
        print('spin not ready!')
        exit(1)

def get_release():
    config_file = '/folk/vxMW/nightly/jenkinsEnvInjection/configs/vx7_nightly_spin.config'
    if os.path.exists(config_file):
        with open(config_file, 'rt') as f:
            for line in f:
                if line.startswith('LTAFRELEASE'):
                    return line.strip()
    else:
        print('config file not ready!')
        exit(0)

def get_ver():
    config_file = '/folk/vxMW/nightly/jenkinsEnvInjection/configs/vx7_nightly_spin.config'
    if os.path.exists(config_file):
        with open(config_file, 'rt') as f:
            for line in f:
                if line.startswith('VXVER'):
                    return line.strip('VXVER=')
    else:
        print('config file not ready!')
        exit(1)

def main():
    week = '{:%Y-%m-%d}'.format(datetime.now())
    if os.path.exists('/net/pek-vx-system1/buildarea1/hyan1/wassp/nightly_config.ini'):
        os.remove('/net/pek-vx-system1/buildarea1/hyan1/wassp/nightly_config.ini')
    with open('/net/pek-vx-system1/buildarea1/hyan1/wassp/nightly_config.ini', 'wt') as f:
        # below is similar with
        # f.write('VXVER=' + 'vxworks/' + get_ver() + '\n')
        print('DVD={DVD}'.format(DVD=get_dvd()), file=f)
        print('{RELEASE}'.format(RELEASE=get_release()), file=f)
        print('RUNDATE={RUNDATE}'.format(RUNDATE=week), file=f)
        print('VXVER={VXVER}'.format(VXVER='vxworks/' + get_ver()), file=f)


if __name__ == '__main__':
    main()
