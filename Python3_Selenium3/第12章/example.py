#coding=utf-8
from behave import *
from features.com.page.loginPage import loginPage

#以下re表示在step中定义正则表达式，要使用正则表达式
use_step_matcher('re')

#这里表示开始抓取正则表达式的匹配值，此次是为了抓取在场景文件example.feature中的url值，
#抓取到之后传值给url，然后进行下面的操作
@when('I open the login website "([^"]*)"')
def step_reg(context,url):
    loginPage(context).get_url(url)
@Then('I input username "([^"]*)"')
def step_r(context,code):
    loginPage(context).login(code)
