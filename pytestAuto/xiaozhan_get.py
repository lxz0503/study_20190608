#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:1/27/2024 3:53 PM
@file:xiaozhan_get.py
"""
import os


def verify_existence(lines, file_name):
    """Verify existence of file "filename\""""
    # log.info(f'Verify existence of file {file_name}')
    for i in range(len(lines)):
        line = lines[i]
        files = str.split(line)  # xiaozhan, need to modify
        print('----', files)
        for j in range(len(files)):
            if os.path.basename(files[j]).lower() == file_name:
                return True
    else:
        return False

if __name__ == "__main__":
    configYaml = '%s/%s' % (
        os.path.join(os.path.dirname(os.path.realpath(__file__))), 'config/qemuTargetConfig.yaml')
    print(f'config path is', configYaml)
    user = None
    user = 'ubuntu' if user is None else user
    print(user)
    print(verify_existence(lines, file_name))


