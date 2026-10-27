#coding=utf-8
from selenium import  webdriver

def before_all(context):
    context.driver = webdriver.Chrome("chromedriverÂ·¾¶")

def after_tag(contex):
    context.driver.quit()
