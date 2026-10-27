#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:9/6/2022 7:38 PM
@file:run.py
@project:xiaozhan_git
"""
import os,time
if __name__ == "__main__":

    # os.makedirs("./allure_result" + "/" + time.strftime("%Y-%m-%d-%H-%M-%S"))
    result_dir = os.listdir('./allure_result')
    # print(result_dir[-1])
    tp = "allure_result" + "/" + result_dir[-1]
    cmd = r'cd C:\Users\xli3\study\xiaozhan_git\19-05-appium移动测试\shanghai'
    # os.system(cmd)
    # cmd = 'pytest --alluredir {0} --reruns 2'.format(tp)
    # os.system(cmd)

    #
    # cmd = r'cp -r {0} ./allure-2.19.0/bin/'.format(tp)
    cmd = r'cd C:\Users\xli3\study\xiaozhan_git\19-05-appium移动测试\shanghai\allure-2.19.0\bin'
    os.system(cmd)
    print(os.getcwd())
    # cmd = 'allure generate {0} -o report/{1}'.format(tp,tp)
    # print(cmd)
    # os.system(cmd)
    #
    # [xli3 @ pek - vx - anvl AutoTSN]$ cp -r allure_result allure-2.19.0/bin/;cd allure-2.19.0/bin/
    # [xli3 @ pek - vx - anvl bin]$  allure generate allure_result/ -o report/html;
    #
    # allure open  report/html


