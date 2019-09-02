#打开百度，点击新闻，在出现的搜索框里输入 python
#ele对应着新闻这个元素
#ele1对应着搜索框
#ele2对应值百度新闻里面的搜索框的  百度一下 这个按钮
import time
from selenium import webdriver
b = webdriver.Firefox()
b.get('http://www.baidu.com')
#ele = b.find_element_by_link_text('新闻')
ele = b.find_element_by_css_selector('a.mnav:nth-child(1)')
ele.click()

#ele1 = b.find_element_by_css_selector('input[class=\'word\']')
ele1 = b.find_element_by_css_selector('input[id=\'ww\']')
ele1.send_keys('python')

#ele2 = b.find_element_by_class_name('btn')
ele2 = b.find_element_by_css_selector('input[type=\'button\']')
ele2.click()

b.back()
ele3 = b.find_element_by_class_name('item-image')
ele3.click()
#做完以上操作，进入一个页面，发现没有后退
time.sleep(5)
b.quit()

#b.back()
#time.sleep(5)
#b.back()
#time.sleep(5)
#b.quit()
