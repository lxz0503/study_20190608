import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

b = webdriver.Chrome()
b.get("http://www.baidu.com")
print(b.title)
print(b.current_url)
if "baidu" not in b.current_url:
    print("The url u opend is not baidu")
else:
    print("you opened baidu.com")
b.maximize_window()
b.minimize_window()
ele = b.find_element_by_link_text('新闻')
#ele = b.find_element_by_css_selector('#u_sp > a:nth-child(1)')
ele.click()
#b.back()
time.sleep(3)
b.quit()

#b.find_element_by_id("kw")
#b.find_element_by_name('wd')
#ele = b.find_element_by_class_name('s_ipt')

#ele.send_keys('python')
#time.sleep(5)
#find another element for search
#b.find_element_by_id('su').click()
#ele.clear()

#ele.send_keys('selenium')
#time.sleep(5)
#b.find_element_by_id('su').click()
#ele.clear()

#b.back()
#b.quit()


#assert  'Django' in driver.title
