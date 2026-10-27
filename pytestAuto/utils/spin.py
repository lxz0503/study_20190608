#!/usr/bin/env python
import shutil


def get_spin_type():
    # xiaozhan, add tow copy here
    shutil.copy("/folk/vxMW/nightly/jenkinsEnvInjection/configs/vx7_ci_nightly_spin.config",
                "/home/xli3/pytestAuto/config")
    shutil.copy("/folk/vxMW/nightly/jenkinsEnvInjection/configs/vx7_nightly_spin.config",
                "/home/xli3/pytestAuto/config")

    config_dir_ci = '/home/xli3/pytestAuto/config/vx7_ci_nightly_spin.config'
    config_dir_nightly = '/home/xli3/pytestAuto/config/vx7_nightly_spin.config'

    spin = ""
    with open(config_dir_ci, 'r') as f:
        line = f.readline()
        spin_name = line.rstrip('\n').split('=')[1]
        # print('spin_name is', spin_name)
        if len(spin_name) != 0:
            spin = 'CISPIN'

    with open(config_dir_nightly, 'r') as f:
        line = f.readline()
        spin_name = line.rstrip('\n').split('=')[1]
        # print('spin_name is', spin_name)
        if len(spin_name) != 0:
            spin = 'SPIN'
    return spin


if __name__ == '__main__':
    a = get_spin_type()
    print(a)
