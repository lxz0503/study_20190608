# encoding=utf-8
from selenium import webdriver
import time


def get_qq_today():
    dr = webdriver.Firefox()
    title_and_content = []
    dr.get('http://www.qq.com/')
    time.sleep(2)
    qq_today_link = dr.find_element_by_css_selector('li.news-top a')
    title_and_content.append(qq_today_link.text)
    href = qq_today_link.get_attribute('href')
    print(href)
    dr.get(href)
    time.sleep(2)
    return href


    #title_and_content.append(dr.find_element_by_id('articleContent').get_attribute('innerHTML'))
    #print(title_and_content)
    #return title_and_content


if __name__ == '__main__':
    get_qq_today()