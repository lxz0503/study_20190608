#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:8/18/2022 11:33 AM
@file:write_yaml.py
@project:xiaozhan_git
"""
import yaml
if __name__ == "__main__":
    data = {'Search_Data': {'search_test_001': {'value': 456, 'expect': [4, 5, 6]},
                            'search_test_002': {'value': 'hello', 'expect': {'value': 'beijing'}},
                            'search_test_003': ['data1', 'data2'],
                            'search_test_004': {'value': 456},
                            'search_test_005': {'value': 456}}}
    with open('hello.yaml', 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f)
