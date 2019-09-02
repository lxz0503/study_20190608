#this is a test to log in http://www.maiziedu.com
#with independent data stored in dictionary
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


def getEleTime(driver, time, func):
    #设置了页面等待时间，用来找到耗时比较长的页面元素
    return WebDriverWait(driver, time).until(func)


def openBrowser():
    ''' return a webdriver handle'''
    webdriver_handle = webdriver.Firefox()
    return webdriver_handle


def openUrl(handle, url):
    handle.get(url)
    handle.maximize_window()


def findElement(d, arg):
    #this is to find username, password and login button
    #耗时比较长，默认60秒后超时，查找'登录'这个元素耗时比较长
    if 'text_id' in arg:
        ele_login = getEleTime(d, 60, lambda d: d.find_element_by_link_text(arg['text_id']))
        ele_login.click()
    user_ele = d.find_element_by_id(arg['user_id'])  #//*[@id="id_account_l"]，找到对应用户名的那个元素
    pwd_ele = d.find_element_by_xpath(arg['pwd_id'])  #//*[@id="id_password_l"]，找到对应密码的那个元素
    login_ele = d.find_element_by_id(arg['login_id'])  #找到对应登录按钮的那个元素
    return user_ele, pwd_ele, login_ele   #返回三个元素，组成一个三元祖


def sendVals(ele_tuple, arg):
    #this is to input username and password
    #arg is a dictionary
    list_key = ['username', 'pwd']
    i = 0
    for key in list_key:
        ele_tuple[i].send_keys('')
        ele_tuple[i].clear()
        #分别对应用户名和密码那个元素，然后输入内容
        ele_tuple[i].send_keys(arg[key])
        i += 1
    #this is to click login button
    ele_tuple[2].click()


def checkResult(d, path):
    try:
        d.find_element_by_xpath(path)  #//*[@id="login-form-tips"]
        print("账号或者密码错误，请重新输入")
    except:
        print("right")


def loginTest(ele_dict, user_list):
    d = openBrowser()
    openUrl(d, ele_dict['url'])
    #找到各个登录用的元素
    ele_tuple = findElement(d, ele_dict)
    #找到元素后，分别点击或者输入内容
    for arg in user_list:
        #arg is a dictionary---every user/pwd
        sendVals(ele_tuple, arg)
    #检查结果，根据xpath匹配到错误的账号或者密码
        checkResult(d, ele_dict['error_id'])  #//*[@id="login-form-tips"]


if __name__ == '__main__':
    url = 'http://www.maiziedu.com/'
    login_text = '登录'
    username = 'maizi_test@139.com'
    pwd = 'abc123456'

    # text_id----登录元素
    # user_id/pwd_id/login_id----输入账号元素
    # uname/pwd----输入账号信息
    # error_id----检查错误条件
    ele_dict = {'url': url, 'text_id': login_text, 'user_id': 'id_account_l', 'pwd_id': '//*[@id="id_password_l"]',
                'login_id': 'login_btn', 'error_id': '//*[@id="login-form-tips"]'}
    #user information should be independent,because there are many users
    user_list = [{'username': username, 'pwd': pwd}]  #every user/pwd is a dictionary
    loginTest(ele_dict, user_list)




