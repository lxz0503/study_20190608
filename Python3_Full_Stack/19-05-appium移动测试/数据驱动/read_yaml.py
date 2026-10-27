#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:8/18/2022 10:08 AM
@file:read_yaml.py
@project:xiaozhan_git
"""
import yaml

if __name__ == "__main__":
    with open('yaml_confg_read.yaml') as f:
        # data = yaml.load(f, Loader=yaml.FullLoader)
        data = yaml.safe_load(f)
    print(data)
