#coding=utf-8
from selenium.webdriver.common.by import By
class Base:
    def __init__(self,driver):
        self.driver = driver

     #*loc 函数参数是指传入的是不定参数，这个知识点在前面章节已经提到过
     #意思是findele函数可以传入1个参数，也可以传入2个参数等等。
    def findele(self,*loc):
        return  self.driver.find_element(*loc)

    def get_url(self,url):
        self.driver.get(url)

    def get_title(self):
        return self.driver.title
