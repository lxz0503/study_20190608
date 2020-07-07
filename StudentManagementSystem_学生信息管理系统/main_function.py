#!/usr/bin/env python3
# coding=utf-8

import re
from util import *

def main():
    ctrl = True
    while ctrl:
        menu()
        option = input('请选择：')
        option_str = re.sub(r'\D', ' ', option)   # replace not number with white space
        if option_str in ['0', '1', '2', '3', '4', '5', '6', '7']:
            option_int = int(option_str)
            if option_int == 0:
                print('退出系统！')
                ctrl = False
            elif option_int == 1:
                insert()
            elif option_int == 2:
                search()
            elif option_int == 3:
                delete()
            elif option_int == 4:
                modify()
            elif option_int == 5:
                sort()
            elif option_int == 6:
                total()
            elif option_int == 7:
                show()

if __name__ == '__main__':
    main()