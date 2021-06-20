# coding=utf-8
from selenium import webdriver  # import 'webdriver' ģ��
import time

driver = webdriver.Chrome()
driver.implicitly_wait(5)
driver.maximize_window()
driver.get('https://passport.juhe.cn/cas/login?service=https%3A%2F%2Fwww.juhe.cn%2Flogin%2Fcas%2Fauth%2Fucenter%3FsourceChannel%3DjHwww-juhe-cn&from=pc')
print("before login:")
# ��ӡȫ��cookie
for cookie_detail in driver.get_cookies():
    print(cookie_detail)
# �ȴ�30�룬�����ֶ���Ԥ�����˺š�����
time.sleep(30)
print("after login:")
for cookie_detail in driver.get_cookies():
    print(cookie_detail)
driver.quit()
