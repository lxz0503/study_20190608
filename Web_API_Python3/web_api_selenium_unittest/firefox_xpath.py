#xpath with firefox

import time
from selenium import webdriver

url = "http://www.sogou.com"
driver = webdriver.Firefox()
driver.get(url)
now_handle = driver.current_window_handle
print(now_handle)
driver.get('http://www.sogou.com')
driver.find_element_by_id('query').send_keys('Joradn')
# driver.find_element_by_id('stb').click()
driver.find_element_by_css_selector('input#stb').click()
time.sleep(3)
driver.quit()
# driver.find_element_by_xpath('//h3[@class="t"]/a[@class="favurl"]').click()
# time.sleep(5)

#ele = b.find_element_by_css_selector('input[name="first name"]')
#ele.send_keys('aaaa')
#print(id(ele))
