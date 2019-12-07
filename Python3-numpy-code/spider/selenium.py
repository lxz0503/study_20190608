import requests
import urllib.request
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def get_url(url):
    time.sleep(1)
    return(requests.get(url))


if __name__ == "__main__":
    driver = webdriver.Chrome() # 初始化一个浏览器对象
    # dcap = dict(DesiredCapabilities.PHANTOMJS)
    # dcap["phantomjs.page.settings.loadImages"] = False
    # driver = webdriver.PhantomJS( desired_capabilities=dcap)
    dep_cities = ["北京","上海","广州","深圳","天津","杭州","南京","济南","重庆","青岛","大连","宁波","厦门","成都","武汉",\
                  "哈尔滨","沈阳","西安","长春","长沙","福州","郑州","石家庄","苏州","佛山","烟台","合肥","昆明","唐山",\
                  "乌鲁木齐","兰州","呼和浩特","南通","潍坊","绍兴","邯郸","东营","嘉兴","泰州","江阴","金华","鞍山","襄阳",\
                  "南阳","岳阳","漳州","淮安","湛江","柳州","绵阳"]
    for dep in dep_cities:
        strhtml = get_url('https://m.dujia.qunar.com/golfz/sight/arriveRecommend?dep=' + urllib.request.quote(dep) + '&exclude=&extensionImg=255,175')
        arrive_dict = strhtml.json()
        for arr_item in arrive_dict['data']:
            for arr_item_1 in arr_item['subModules']:
                for query in arr_item_1['items']:
                    driver.get("https://fh.dujia.qunar.com/?tf=package")
                    # 等待出发地输入框加载完毕，最多等待10s
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "depCity")))
                    # 清空出发地文本框，输入出发地和目的地，点击“开始定制”按钮
                    driver.find_element_by_xpath("//*[@id='depCity']").clear()
                    driver.find_element_by_xpath("//*[@id='depCity']").send_keys(dep)
                    driver.find_element_by_xpath("//*[@id='arrCity']").send_keys(query["query"])
                    driver.find_element_by_xpath("/html/body/div[2]/div[1]/div[2]/div[3]/div/div[2]/div/a").click()
                    print("dep:%s arr:%s" % (dep, query["query"]))
                    for i in range(10):
                        time.sleep(random.uniform(5, 6))
                        # 如果定位不到页码按钮，说明搜索结果为空
                        pageBtns = driver.find_elements_by_xpath("html/body/div[2]/div[2]/div[8]")
                        if pageBtns == []:
                            break
                        # 找出所有的路线信息DOM元素
                        routes = driver.find_elements_by_xpath("html/body/div[2]/div[2]/div[7]/div[2]/div")
                        for route in routes:
                            result = {
                                'date': time.strftime('%Y-%m-%d', time.localtime(time.time())),
                                'dep': dep,
                                'arrive': query['query'],
                                'result': route.text
                            }
                            print(result)

                        if i < 9:
                            # 找到“下一页"按钮并点击翻页
                            btns = driver.find_elements_by_xpath("html/body/div[2]/div[2]/div[8]/div/div/a")
                            for a in btns:
                                if a.text == u"下一页":
                                    a.click()
                                    break

    driver.close()
