from selenium import webdriver
import unittest
from lxz_python.login_page import LoginPage


class TestPageObj(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()
        self.username = '11'  # 调试的时候需要换成对应的QQ号
        self.password = ' '  # 需要换成对应的密码

    def tearDown(self):
        self.driver.quit()

    def test_user_login(self):
        driver = self.driver
        login_page = LoginPage(driver)
        login_page.open()
        driver.switch_to.frame('login_frame')
        driver.find_element_by_id("switcher_plogin").click()
        login_page.type_username(self.username)
        login_page.type_password(self.password)
        login_page.type_submit()
        #self.assertIn('QQ空间-分享生活，留住感动', driver.title)
        self.assertEqual(driver.find_element_by_xpath('//*[@id="err_m"]').text, '请输入正确的账号')

if __name__ == '__main__':
    unittest.main()