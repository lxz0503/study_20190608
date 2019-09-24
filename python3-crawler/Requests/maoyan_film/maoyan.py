import requests

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


if __name__ == '__main__':
    html = get_one_page('http://maoyan.com/board')
    print(html)
