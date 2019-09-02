from selenium.webdriver.common.by import By
from lxz_python.base import Page


class LoginPage(Page):
    """登录页面模型"""
    url = '/'
    # 定位器
    username_loc = (By.ID, 'u')
    password_loc = (By.ID, 'p')
    submit_loc = (By.ID, 'login_button')
    error_name = (By.XPATH, '//*[@id="err_m"')

    def type_username(self, username):
        #self.find_element(*self.username_loc).send_keys(username)
        self.find_element(*self.error_name).send_keys(username)

    def type_password(self, password):
        self.find_element(*self.password_loc).send_keys(password)

    def type_submit(self):
        self.find_element(*self.submit_loc).click()
