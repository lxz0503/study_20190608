#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:3/7/2024 1:11 PM
@file:case_record.py
"""


def get_case_name(module, name, version):
    return module + '.' + name + '-' + version


def record_result_expect(result, ret, case_name):
    if ret == 'PASS':
        result.append((case_name, 'PASS'))
    else:
        result.append((case_name, 'FAIL'))
        assert False


def record_result(result, res, ret, case_name):
    if isinstance(ret, str):
        if res in ret:
            result.append((case_name, 'PASS'))
        else:
            result.append((case_name, 'FAIL'))
            assert False

    elif isinstance(ret, list):
        for i in ret:
            if res in i:
                record = 'PASS'
            else:  # If one fails the whole will fail
                result.append((case_name, 'FAIL'))
                assert False
        # after the end of for loop
        if record == 'PASS':
            result.append((case_name, 'PASS'))
    else:
        pass


if __name__ == "__main__":
    pass
