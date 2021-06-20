# coding=utf-8
import time
from Base.base import Base
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class SearchPage(Base):   # 继承了Base
    def search_leave(self):
        self.log.info('departure city')        # class Base里面有self.log
        return self.by_id("departCityName")

    def search_arrive(self):
        return self.by_id('arriveCityName')

    def remove_readonly(self):
        return self.js("document.getElementById('departDate').removeAttribute('readonly')")

    def search_date(self, riqi):   # this must be after above step(remove readonly)
        self.by_id("departDate").clear()
        time.sleep(2)
        # self.by_id('departDate').send_keys(self.date_n(2))   # this is one method
        self.by_id('departDate').send_keys(riqi)     # this is another method to set date
        # 鼠标点击空白处
        ActionChains(self.driver).move_by_offset(0, 0).click().perform()

    def search_btn(self):
        try:
            return self.by_class_name("searchbtn").click()  # after this, sleep(5)
        except Exception as e:
            self.log.error('can not search')

    # 如果是针对一个页面，下面也可以作为某个case的断言的判断
    def is_exist_ele(self, element):
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(element))
            return True
        except:
            return False

    # 例如网站登录页面，需要用手机号和密码那种，经常会出现各种错误提示
    def get_error_info(self):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="error"]')))
        return self.by_xpath('//div[@class="error"]').text   # 返回文本内容，然后在case断言中比对文本内容
