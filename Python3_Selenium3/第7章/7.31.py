from selenium import webdriver
import  time
driver = webdriver.Chrome()
driver.get("https://pan.baidu.com/")
	   #代码执行到此步，需要手动去登录到百度网盘。
time.sleep(20)
cookies=driver.get_cookies()
print(cookies)
