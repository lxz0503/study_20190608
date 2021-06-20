# coding=utf-8
from selenium import webdriver

# 一般登录用的用户名和密码都是嵌套在iframe里面
driver = webdriver.Chrome()
# 打开主页面QQ邮箱登录页面
driver.get('https://en.mail.qq.com/cgi-bin/loginpage')
# 驱动切换到iframe，根据iframe的name切换
# driver.switch_to.frame("login_frame")
# 根据iframe的id
driver.switch_to.frame(driver.find_element_by_id('login_frame'))
# 对用户名赋值
driver.find_element_by_id('u').send_keys('xiaozhan')
driver.find_element_by_css_selector("*[id='p']").send_keys('xiaozhan')
driver.find_element_by_css_selector("*[id='p_low_login_enable']").click()
driver.find_element_by_css_selector("*[class='btn']").click()

# 退出浏览器操作
driver.quit()

