# -*- coding: utf-8 -*-


class Page(object):
    """基础类，用于所以页面对象类继承"""
    login_url = 'https://i.qq.com'

    def __init__(self, selenium_driver, base_url=login_url):
        self.base_url = base_url
        self.driver = selenium_driver
        self.timeout = 30

    def on_page(self):
        return self.driver.current_url == (self.base_url + self.url)

    def _open(self, url):
        url = self.base_url + url
        self.driver.get(url)
        assert self.on_page(), 'did not land on %s' % url

    def open(self):
        self._open(self.url)

    def find_element(self, *loc):
        return self.driver.find_element(*loc)

    def script(self, src):
        return self.driver.execute_script(src)




