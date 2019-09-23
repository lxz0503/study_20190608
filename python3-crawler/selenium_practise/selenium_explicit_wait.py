# coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import re
from pyquery import PyQuery as pq


browser = webdriver.Chrome()
browser.get('https://www.taobao.com/')
wait = WebDriverWait(browser, 10, 0.2)

def search():
    pass
    try:
        input_box = wait.until(EC.presence_of_element_located((By.ID, 'q')))
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input_box.send_keys('美食')
        button.click()
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        return total.text
    except NoSuchElementException:
        print('no such element')
    except TimeoutException:
        print('timeout')
        return search()
    finally:
        browser.quit()

def next_page(page_num):
    try:
        input_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input_box.clear()
        input_box.send_keys(page_num)
        button.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), page_num))
    except NoSuchElementException:
        print('no such element')
    except TimeoutException:
        print('timeout')
        return next_page(page_num)

def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3]

        }


if __name__ == '__main__':
    res = search()
    # res = '共 100 页'
    total_page = int(re.compile('(\d+)').search(res).group(1))
    print(total_page)
    for i in range(2, total_page+1):
        next_page(i)