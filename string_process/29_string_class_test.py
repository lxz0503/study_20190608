"""customize string representations of object"""
# !/usr/bin/env python3
# coding=utf-8
# https://zhuanlan.zhihu.com/p/53864366       refer to this link for study


class CLanguage(object):
    def __init__(self):
        self.name = "C语言中文网"
        self.add = "http://c.biancheng.net"

    def __repr__(self):
        return "CLanguage[name=" + self.name + ", add=" + self.add + "]"

    def __str__(self):
        return 'the name is {0}, the website is {1}'.format(self.name, self.add)


if __name__ == '__main__':
    clangs = CLanguage()
    print(clangs)
    print(clangs.__dir__())
    print(dir(clangs))
    print(clangs.__dict__)     # show attributes
    # TODO: setattr() can modify
    setattr(clangs, 'name', 'beijing')
    print(clangs.name)
    # TODO: getattr() can get attribute value, if not exists, return the default value
    print(getattr(clangs, 'a', 'sh'))

