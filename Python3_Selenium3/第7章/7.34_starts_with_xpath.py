# coding=utf-8
from selenium import webdriver
import os, time

driver = webdriver.Chrome()
prj_path = os.path.split(os.path.realpath(__file__))[0].split('第7章')[0]
html_path = os.path.join(prj_path, "第7章", "34_test.html")
# print(html_path)
driver.get(html_path)
# 选中属性id里以字母p开头的选项,返回一个列表
res = driver.find_elements_by_xpath("//*[starts-with(@id,'p')]")
for r in res:
    print(r.text)
time.sleep(3)
# 选中属性id里包含字母p的选项,返回一个列表
res = driver.find_elements_by_xpath("//*[contains(@id,'m')]")
for r in res:
    print(r.text)
time.sleep(3)
# 选中属性id里以字母t结尾的选项,返回一个列表
# https://blog.csdn.net/qq_24373725/article/details/79728729?utm_medium=distribute.pc_relevant.none-task-blog-baidujs_title-0&spm=1001.2101.3001.4242
# ends-with 是xpath2.0的语法，当前浏览器还不支持
# res = driver.find_elements_by_xpath("//*[ends-with(@id,'t')]")
# for r in res:
#     print(r.text)
# time.sleep(3)
driver.quit()

#  //a[contains(text(),"百度搜索")]
