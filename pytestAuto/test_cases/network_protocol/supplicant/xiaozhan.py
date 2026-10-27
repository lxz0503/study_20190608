#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:2/8/2024 6:07 PM
@file:xiaozhan.py
"""
import re

def buildVip(cfg, overrides={}):
    print(f'{cfg}')
    if overrides:
        print('pppp')
        if 'vxparam' in overrides:
            for c in overrides['vxparam']:
                print('a')


if __name__ == "__main__":
    cfg = 'aaa'
    buildVip(cfg)
    ret = ['Subtest: test_signed_mod_replace_ab', 'Subtest: test_signed_mod_replace_ba', 'Subtest: test_mpi', 'Subtest: test_smallprime', 'Subtest: test_smallsafeprime', 'Subtest: test_is_prime', 'Subtest: test_not_prime', 'Subtest: test_mod_exp', 'Subtest: test_mod_exp_consttime', 'INFO:  @ ../test/bntest.c:3150', 'bntest                         successfully', '[vxWorks]']
    ret = '\n'.join(ret)
    # pattern = re.search(r'bntest\s+successfully', ret)[0]
    pattern = re.search(r'bntest\s+successfully', ret)[0]
    print(pattern)
    # assert 'bntest                         successfully' in ret
    assert pattern in ret
    cmd = ["-----BEGIN RSA PRIVATE KEY-----",
                               "-----BEGIN ENCRYPTED PRIVATE KEY-----"]
    print('--- send=%s' % cmd)
