# 类名命名方法，大驼峰，单词首字母大写，单词之间没有下划线
# self,哪一个对象调用的方法，self就是哪一个对象的引用
# 在方法内部，通过self.来访问对象的属性，调用其他方法
# __str__(self)方法可以打印对象，返回值必须是字符串
# 使用super().父类方法 来直接继承父类的方法,super().fun()
# 对象也可以作为方法的参数传递进去,


class Page(object):
    """基础类，用于所以页面对象类继承"""
    login_url = 'https://i.qq.com'

    def __init__(self, selenium_driver, base_url=login_url):
        self.base_url = base_url
        self.driver = selenium_driver
        print("the base url is %s" % self.base_url)


    def open(self, url):
        url = self.base_url + url
        return url

page = Page("firefox", "aaaaa")
print(page.open("bbbb"))

