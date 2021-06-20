# coding=utf-8
from Base.base import Base
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class LoginPage(Base):
    # 八大定位
    leave = {'id': 'notice01'}
    arrive = {'css': '#notice08'}
    date = {'id': 'dateObj'}
    current = {'css': '#searchtype > li.current'}
    # try below methods
    # username，By.ID, By.NAME
    name_text = (By.XPATH, '//input[@name="phone"]')
    # password
    pwd_text = (By.XPATH, '//input[@name="password"]')
    # login button
    login_btn = (By.XPATH, '//button[text()="login"]')
    # error information
    error_area = (By.XPATH, '//div[@class="login"]')


    def login(self, leave_city, arr_city):
        self.send_key(loginPage.username).send_keys('tim')
        self.send_key(loginPage.leave).send_keys(leave_city)
        self.send_key(loginPage.arrive).send_keys(arr_city)

    # 如果是针对一个页面，下面也可以作为某个case的断言的判断
    def is_exist_ele(self):
        """
        等待10秒，如果元素出现，返回True，否则返回False
        :return:
        """
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@class="error"]')))
            return True
        except:
            return False

    # 例如网站登录页面，需要用手机号和密码那种，经常会出现各种错误提示
    def get_error_info(self):
        # WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="error"]')))
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.error_area))  # 用元组替代上面的明文
        # return self.by_xpath('//div[@class="error"]').text  # 返回文本内容，然后在case断言中比对文本内容
        # 下面的方法，如果需要修改定位方式为其他种，例如By.ID,直接去修改类属性即可
        return self.find_ele(self.error_area).text  # 返回文本内容，然后在case断言中比对文本内容


if __name__ == '__main__':
    print(list(loginPage.username.keys())[0])
    print(list(loginPage.username.values()))
    print(loginPage.username)
