import unittest
import HTMLTestRunner

class RunTools(object):
    def __init__(self, case_path, pattern):
        self.case_path = case_path
        self.pattern = pattern

    def choose_all_cases(self):
        discover_all_cases = unittest.defaultTestLoader.discover(self.case_path, self.pattern)
        return discover_all_cases


if __name__ == '__main__':
    # suite = unittest.TestSuite()
    # suite.addTest(WebTest('test_visitURL'))    #
    # suite.addTest(unittest.TestLoader().loadTestsFromTestCase(WebTest))   #

    ####
    case_dir = r'D:\xiaozhan_git\study_20190608\API_Python\web_api_selenium_unittest\my_discover_unittest\TestCases'
    run = RunTools(case_dir, 'test*.py')
    suite = run.choose_all_cases()

    #####
    # file_name = "F:\\Pycharm\\Selenium_Xiaozhan\\report.html"
    file_name = r"D:\xiaozhan_git\study_20190608\API_Python\web_api_selenium_unittest\my_discover_unittest\Test_Report\report.html"
    with open(file_name, 'wb+') as fp:
        runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='report', description='web api test')
        runner.run(suite)