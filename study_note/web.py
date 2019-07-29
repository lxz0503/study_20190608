# put browser driver under your python installed repository, like this:F:\Python

# for chrome released version
# https://www.cnblogs.com/wendyzhouyh/p/9775815.html

# for chrome driver
# http://chromedriver.storage.googleapis.com/index.html

import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# driver = webdriver.Chrome()
driver = webdriver.Firefox()
# you can also use Firefox

driver.get("http://guidebook.seleniumacademy.com/Selectable.html")
driver.implicitly_wait(30)
driver.maximize_window()
one = driver.find_element_by_name('one')
two = driver.find_element_by_name('two')
three = driver.find_element_by_name('three')
ActionChains(driver).key_down(Keys.CONTROL).click(one).click(two).click(three).key_up(Keys.CONTROL).perform()
input('Press ENTER to close the automated browser')
driver.quit()



