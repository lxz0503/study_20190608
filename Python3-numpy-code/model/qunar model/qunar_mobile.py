# -*- coding: utf-8 -*-
import requests
import json
import urllib.request
import time
import csv
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def globalVals():
    global driver
    global driver_
    global dep_cities
    global next_page_idx
    global qunar


    driver = webdriver.Chrome()
    driver_ = webdriver.Chrome()

    dep_cities = ["杭州"]


def init_csv():
    global f
    global f_
    global writer
    global writer_
    csvFile = "D:/qunar_routes.csv"
    f = open(csvFile, "a+", newline="", encoding='utf-8')

    writer = csv.writer(f)



def close_csv():
    global f
    global f_

    f.close()
    f_.close()


def get_url(url):
    time.sleep(5)
    return(requests.get(url))


def dump_routes_csv(dep,arr):
    global driver
    global driver_
    global writer
    routes = driver.find_elements_by_xpath("html/body/div/div/div[1]/div[3]/div[1]/div[4]/div[2]/div/div")
    for route in routes:
        try:
            print("route info:%s" % route.text)
            url = route.get_attribute("data-url")
            print("url:%s" % url)
            driver_.get(url)
            time.sleep(random.uniform(2, 3))

            try:
                rating = driver_.find_element_by_css_selector("div.rating > span")
                type = driver_.find_element_by_css_selector("div.lv")
                hotel = '\n'.join([rating.text, type.text])
            except:
                try:
                    driver_.find_element_by_xpath("//*[@id='js-hotel']/div/div[1]/div").click()
                except:
                    driver_.find_element_by_css_selector("div.m-richtext.m-hotel > div.list > div.item > div > div > div.flex").click()
                time.sleep(random.uniform(2, 3))
                hotel = driver_.find_element_by_xpath("//*[@id='main-page']/div[2]/div[1]/div[1]/span").text

            print("hotel info:%s" % hotel)
            writer.writerow([dep, arr, route.text, hotel])
        except Exception as e:
            print(str(e))
            continue


def dump_summary_csv(dep, arr):
    global writer_
    writer_.writerow([dep, arr])


if __name__ == "__main__":
    globalVals()
    init_csv()

    for dep in dep_cities:
        strhtml = get_url('https://m.dujia.qunar.com/golfz/sight/arriveRecommend?dep=' + urllib.request.quote(dep) + '&exclude=&extensionImg=255,175')
        arrive_dict = json.loads(strhtml.text)
        for arr_item in arrive_dict['data']:
            if arr_item['title'] != "国内":
                continue
            for arr_item_1 in arr_item['subModules']:
                for query in arr_item_1['items']:

                    driver.get("https://touch.dujia.qunar.com/p/list?cfrom=zyx&dep=" + urllib.request.quote(dep) + \
                               "&query=" + urllib.request.quote(query['query']) + "%e8%87%aa%e7%94%b1%e8%a1%8c&it=n_index_free")
                    try:

                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "item g-flexbox list-item ")))
                    except Exception as e:
                        print (str(e))
                    print("dep:%s arr:%s" % (dep,query["query"]))
                    for i in range(50):
                        time.sleep(random.uniform(2, 3))
                        print("page %d" % (i+1))
                        # 模拟page down键的输入
                        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
                    dump_routes_csv(dep, query["query"])
                    # dump_summary_csv(dep, query["query"])
                    close_csv()
                    driver.close()
                    driver_.close()
                    exit(0)


    close_csv()
    driver.close()
    driver_.close()

