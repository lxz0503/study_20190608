#coding=utf-8
from  ddt import  ddt ,data,file_data,unpack
from dataexcel import  get_data
import unittest
from selenium import  webdriver

excel=get_data('', 1)
@ddt
class test_se(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get('https://passport.ctrip.com/user/login?')
#¶Ô×Öµä²Ù×÷
    @data(*excel)
    def test_01(self,dic):
        self.driver.find_element_by_id('nloginname').send_keys(dic.get('username'))
        self.driver.find_element_by_id('npwd').send_keys(dic.get('passwd'))
        print(dic)

        self.assertEqual(dic.get('username'),dic.get('passwd'))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
