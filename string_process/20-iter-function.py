"""iter()"""
# !/usr/bin/env python3
# coding=utf-8


def main():
    # use iter() to create a iterator
    week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    i = iter(week)
    print(next(i))
    print(next(i))
    # iter() using a fuction and a sentinel
    with open('reg_text', 'r') as fp:
        for line in iter(fp.readline, ''):
            print(line)
    #
    for i, m in enumerate(week, start=1):
        print(i, m)


if __name__ == '__main__':
    main()