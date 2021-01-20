"""This can get car complaint information from website"""
# !/usr/bin/env python3
# coding=utf-8

import requests
import time
from bs4 import BeautifulSoup
import pandas as pd

def get_time():
    cur_time = str(time.localtime().tm_year) + '-' + str(time.localtime().tm_mon) + '-' + str(time.localtime().tm_mday)
    return cur_time


def get_page_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
    }
    res = requests.get(url, headers=headers, timeout=10)
    html = res.text
    # print(html)
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def analysis(soup):
    # find complete complaint information,you should have knowledge of html
    temp = soup.find('div', class_="tslb_b")
    # create DataFrame
    df = pd.DataFrame(columns=[
        'id', 'brand', 'car_model', 'type', 'desc', 'problem', 'datetime', 'status'
    ])
    tr_list = temp.find_all('tr')
    for tr in tr_list:
        # ToDo: extract complaint information
        temp = {}
        td_list = tr.find_all('td')
        # the first tr does not have td,and others all have 8 td
        if len(td_list) > 0:
            temp['id'], temp['brand'], temp['car_model'], temp['type'], temp['desc'], temp['problem'], temp['datetime'], temp['status'] = \
            td_list[0].text, td_list[1].text, td_list[2].text, td_list[3].text, td_list[4].text, td_list[5].text, td_list[6].text, td_list[7].text
        # print(id, brand, car_model, type, desc, problem, datetime, status)
        df = df.append(temp, ignore_index=True)
    return df


if __name__ == '__main__':
    page_num = 2
    base_url = 'http://www.12365auto.com/zlts/0-0-0-0-0-0_0-0-0-0-0-0-0-'
    result = pd.DataFrame(columns=[
        'id', 'brand', 'car_model', 'type', 'desc', 'problem', 'datetime', 'status'
    ])
    for i in range(page_num):
        request_url = base_url + str(i + 1) + '.shtml'
        soup = get_page_content(request_url)
        df = analysis(soup)
        # print(df)
        result = result.append(df)
    result.to_csv('car_complaint.csv', index=False)
    result.to_excel('car_complaint.xlsx', index=False)