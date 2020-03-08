#!/usr/bin/env python
# encoding=UTF-8
# run this script for whole test structure
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
    # generate test report
    report_dir = os.path.dirname(os.path.dirname(__file__)) + "/report/" + run.getNowTime
    report_name = report_dir + "/sinaReport.html"
    if not os.path.exists(report_dir):
        os.mkdir(report_dir)
    with open(report_name, 'wb') as fp:
        runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Page_Object_UI_Test report', description='Page_Object_UI_Test Sina test report')
        runner.run(suite)

