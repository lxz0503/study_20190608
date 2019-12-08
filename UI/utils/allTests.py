#!/usr/bin/env python
# encoding=UTF-8

import unittest
import os
import HTMLTestRunner
import time

class RunTools(object):
    def __init__(self, case_path, pattern):
        self.case_path = case_path
        self.pattern = pattern

    def choose_all_cases(self):
        discover_all_cases = unittest.defaultTestLoader.discover(self.case_path, self.pattern)
        return discover_all_cases

    @property
    def getNowTime(self):
        return time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())


if __name__ == '__main__':
    case_dir = os.path.dirname(os.path.dirname(__file__)) + '/case'
    run = RunTools(case_dir, 'test_*.py')
    suite = run.choose_all_cases()
    report_name = os.path.dirname(os.path.dirname(__file__)) + "/report/" + "sinaReport.html"
    # below line is for linux,win7 can not create D:/xiaozhan_git/study_20190608/UI/report/2019-12-08_13-43-57/sinaReport.html
    # file_name = os.path.dirname(os.path.dirname(__file__)) + "/" + filePath + "/" + run.getNowTime + "/" + fileName
    with open(report_name, 'wb') as fp:
        runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='UI report', description='UI sina test report')
        runner.run(suite)