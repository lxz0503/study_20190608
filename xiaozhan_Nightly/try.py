#!/usr/bin/env python3
import os
dvd = '/net/pek-vx-system1/buildarea1/yliu2/nightly/vx20210315121337_vx_2103'
cmd = dvd + '/' + 'vxworks'
cmd = ls cmd
process = os.popen(cmd)
output3 = process.read()
process.close()

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

with open('xiaozhan.ini', 'wt') as f:
    # f.write('VXVER=' + 'vxworks/' + get_ver() + '\n')
    # f.write('DVD=' + 'vxworks/' + get_dvd() + '\n')
    print('DVD={DVD}'.format(DVD=get_dvd()), file=f)
    print('{RELEASE}'.format(RELEASE=get_release()))
    print('RUNDATE={RUNDATE}'.format(RUNDATE=week))
    print('VXVER={VXVER}'.format(VXVER='vxworks/' + get_ver()))

