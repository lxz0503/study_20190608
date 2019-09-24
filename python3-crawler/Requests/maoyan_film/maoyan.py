import requests
from requests.exceptions import RequestException
import re

def get_one_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
    }
    try:
        response = requests.get('https://maoyan.com/board', headers=headers)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(e)
        return None

def parse_one_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a'
                         + '.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                         + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    # pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a', re.S)
    items = re.findall(pattern, html)
    print(items)


if __name__ == '__main__':
    html = get_one_page('http://maoyan.com/board')
    # print(html)
    parse_one_page(html)
