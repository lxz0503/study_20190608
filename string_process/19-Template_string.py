""" This is to demonstrate template string function"""
# !/usr/bin/env python3
# coding=utf-8

from string import Template


def main():
    # string formatting
    str1 = 'my name is {0}, address is {1}'.format('xiaozhan', 'beijing')
    # create a template with placeholders.   Method 2, with key arguments
    templ = Template('my name is ${name},address is ${address}')
    str2 = templ.substitute(name='xiaozhan', address='beijing')
    print(str2)
    # method 3 for string formatting, substitute with a dictionary
    data = {
        'name': 'xiaozhan',
        'address': 'beijing'
    }
    str3 = templ.substitute(data)
    print(str3)

    print(bool(set()))
    print(bool(range(0)))



if __name__ == '__main__':
    main()