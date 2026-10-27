# coding=utf-8
from selenium import webdriver

# xpath 相对路径定位元素，通过id属性
driver = webdriver.Chrome()
driver.get("https://passport.meituan.com/account/unitivelogin?")
driver.find_element_by_xpath('//*[@id="login-email"]').send_keys('134')
# xpath 相对路径定位元素，通过name属性
driver.find_element_by_xpath('//*[@name="email"]').send_keys('134')
# xpath 相对路径定位元素，通过class属性
driver.find_element_by_xpath('//*[@class="f-text phone-input"]').send_keys('134')
# 下面的也可以，指定了input标签
driver.find_element_by_xpath('//input[@id="login-email"]').send_keys('134')