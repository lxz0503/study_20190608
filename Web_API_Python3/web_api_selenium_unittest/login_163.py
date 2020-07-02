#this is a test to log in 163 mail box
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


url = 'http://www.maiziedu.com/'
login_text = '登录'
account = 'maizi_test@139.com'
pwd = 'abc123456'


def hitLogin(driver, time, func):
    return WebDriverWait(driver, time).until(func)

def openBrowser():
    return webdriver.Firefox()

def openUrl(d,url):
    d.get(url)
    d.maximize_window()

def findElements(d):
    ele_login = hitLogin(d, 60, lambda d: d.find_element_by_link_text('登录'))
    ele_login.click()

    user_ele = d.find_element_by_xpath('// *[ @ id = "id_account_l"]')
    user_ele.send_keys(account)

    pwd_ele = d.find_element_by_xpath('//*[@id="id_password_l"]')
    pwd_ele.send_keys(pwd)

    login_ele = d.find_element_by_xpath('//*[@id="login_btn"]').click()

    return user_ele, pwd_ele, login_ele



def loginTest():
    d = openBrowser()
    openUrl(d, url)
    findElements(d)

if __name__ == '__main__':
    loginTest()