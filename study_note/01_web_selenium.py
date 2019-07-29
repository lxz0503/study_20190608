from selenium import webdriver
import time

browser = webdriver.Chrome()
browser.get('https://httpbin.org/forms/post')
custname = browser.find_element_by_name("custname")
custname.clear()
custname.send_keys("python测试开发")

time.sleep(2)
for size_element in browser.find_elements_by_name("size"):
    if size_element.get_attribute('value') == 'medium':
        size_element.click()

time.sleep(2)
for topping in browser.find_elements_by_name('topping'):
    if topping.get_attribute('value') in ['bacon', 'cheese']:
        topping.click()

time.sleep(2)
browser.find_element_by_tag_name('form').submit()
# {
#   "args": {},
#   "data": "",
#   "files": {},
#   "form": {
#     "comments": "",
#     "custemail": "",
#     "custname": "python\u6d4b\u8bd5\u5f00\u53d1",
#     "custtel": "",
#     "delivery": "",
#     "size": "medium",
#     "topping": [
#       "bacon",
#       "cheese"
#     ]
#   },
#   "headers": {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Accept-Language": "en-US,en;q=0.9",
#     "Cache-Control": "max-age=0",
#     "Content-Length": "132",
#     "Content-Type": "application/x-www-form-urlencoded",
#     "Host": "httpbin.org",
#     "Origin": "https://httpbin.org",
#     "Referer": "https://httpbin.org/forms/post",
#     "Upgrade-Insecure-Requests": "1",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
#   },
#   "json": null,
#   "origin": "147.11.252.42, 147.11.252.42",
#   "url": "https://httpbin.org/post"
# }