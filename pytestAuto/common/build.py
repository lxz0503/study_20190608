#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:1/15/2024 3:07 PM
@file:build.py
"""
import os

def build():
    os.chdir('/home/xli3/vxworks')
    wrenvPrefix = '/home/xli3/vxworks/wrenv.linux -p vxworks/relx'
    bsp = 'itl_generic'
    vsbCreateCmd = f'{wrenvPrefix} vxprj vsb create -force -S -bsp {bsp} {bsp}_xiaozhan'
    res = os.system(vsbCreateCmd)
    return res

if __name__ == "__main__":
    build()
