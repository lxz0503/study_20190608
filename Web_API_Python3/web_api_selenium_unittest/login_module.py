#coding:utf-8
from selenium import webdriver
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from userdata import get_webinfo,get_userinfo, XlUserinfo
from log_module import Xlloginfo



def get_ele_times(driver, times, func):
    return WebDriverWait(driver, times).until(func)

def openBrower():
    '''
    return webdriver Handle
    '''
    webdriver_handle = webdriver.Firefox()
    return webdriver_handle
def openUrl(handle, url):
    '''
    load url
    '''
    handle.get(url)
    handle.maximize_window()

def findElement(d, arg):
    '''
    arg must be dict
    1: text_id:
    2：userid
    3: pwdid
    4: loginid
    return useEle, pwdEle, loginEle
    '''
    if 'text_id' in arg:
        ele_login = get_ele_times(d, 10, lambda d: d.find_element_by_link_text(arg['text_id']))
        ele_login.click()
    useEle = d.find_element_by_id(arg['userid'])
    pwdEle = d.find_element_by_id(arg['pwdid'])
    loginEle = d.find_element_by_id(arg['loginid'])
    return useEle, pwdEle, loginEle

def sendVals(eletuple, arg):
    '''
    ele tuple
    account : uname, pwd
    '''
    listkey = ['uname', 'pwd']
    i = 0
    for key in listkey:
        eletuple[i].send_keys('')
        eletuple[i].clear()
        eletuple[i].send_keys(arg[key])
        i+=1
    eletuple[2].click()

def checkResult(d, err_id, arg, log):
    result = False
    time.sleep(2)
    try:
        err = d.find_element_by_id(err_id)
        print("Account And Pwd Error!")
        #msg = 'uname=%s pwd=%s:error:%s\n'%(arg['uname'],arg['pwd'], err.text)
        log.log_write(arg['uname'], arg['pwd'], 'Error', err.text)
       
    except:
        print("Account And Pwd Right!")
        msg = 'uname=%s pwd=%s:pass\n' % (arg['uname'],arg['pwd'])
        #log.log_write(msg)
        log.log_write(arg['uname'], arg['pwd'], 'Pass')
        result = True
    return result

def logout(d, ele_dict):
    d.find_element_by_class_name(ele_dict['usermenu']).click()
    d.find_element_by_link_text(ele_dict['logout']).click()


def login_test(ele_dict,user_list):
    d = openBrower()
    #log = Loginfo()
    log = Xlloginfo()
    log.log_init('sheet1', 'uname', 'pwd', 'result', 'msg')
    openUrl(d, ele_dict['url'])
    ele_tuple = findElement(d, ele_dict)
    for arg in user_list:
        sendVals(ele_tuple, arg)
        result = checkResult(d, ele_dict['errorid'], arg, log)
        if result:
            #logout
            logout(d, ele_dict)
            #longin
            ele_tuple = findElement(d, ele_dict)
    log.log_close()
    d.quit()
   
if __name__ == '__main__':
    #url = 'http://www.maiziedu.com/'
    #login_text = '登录'
    #account = 'maizi_test@139.com'
    #pwd = 'abc123456'
    '''
    ele_dict = {'url':url, 'text_id':login_text, 'userid':'id_account_l',\
                'pwdid':'id_password_l', 'loginid':'login_btn','uname':account, 'pwd':pwd,\
                'errorid':'该账号格式不正确'}
    user_list = [{'uname':account, 'pwd':pwd}]
    '''
    ele_dict = get_webinfo(r'D:\Pycharm\test_xiaozhan\lxz_python\webinfo.txt')
    #user_list = get_userinfo(r'C:\Users\hyg\Desktop\test\userinfo.txt')
    xinfo = XlUserinfo(r'D:\Pycharm\test_xiaozhan\lxz_python\userinfo.xls')
    user_list = xinfo.get_sheetinfo_by_index(0)

    #file webinfo/usrinfo ele_dict= get_webinfo(path) user_list=get_userinfo(path)
    login_test(ele_dict, user_list)



