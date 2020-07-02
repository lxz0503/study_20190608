import time
from selenium import webdriver

url = "file:///D:/Pycharm/test_xiaozhan/test_table.html"
driver = webdriver.Firefox()
driver.get(url)
#ele = driver.find_element_by_xpath("//*[id='table']/tr[2]/td[2]")
#ele = driver.find_element_by_xpath('//td[contains(.,"soap")]/input[1]')

table = driver.find_element_by_id('table')
tr_list = table.find_elements_by_tag_name('tr')
for row in tr_list:
    td_list = row.find_elements_by_tag_name('td')
    for col in td_list:
        print("%20s\t" % col.text,end="")
    print()
#driver.quit()