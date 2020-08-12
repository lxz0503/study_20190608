"""transform functions like filter,map, sorted"""
# !/usr/bin/env python3
# coding=utf-8


def func_filter(x):
    # return x % 2 == 1
    if x % 2 == 0:
        return False
    return True


def func_filter2(x):
    if x.isupper():
        return False
    return True

def func_map(x):
    return x ** 2

def to_grade(x):
    if x >= 90:
        return 'A'
    elif x >= 80 and x < 90:
        return 'B'
    elif x >= 70 and x < 80:
        return 'C'
    elif x >= 60 and x < 70:
        return 'D'
    else:
        return 'F'

def main():
    nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    chars = 'abcdEFGH'
    grades = (81, 89, 94, 61, 99, 74)
    # TODO: use filter to remove items from a list
    odds = list(filter(func_filter, nums))
    print(odds)
    # TODO: use filter to remove items from a list
    lowers = list(filter(func_filter2, chars))
    print(lowers)
    # TODO: use map to create a new sequence
    squares = list(map(func_map, nums))
    print(squares)
    # TODO: use sorted and map to change numbers to grades
    grades = sorted(grades, reverse=True)
    letters = list(map(to_grade, grades))
    print(letters)


if __name__ == '__main__':
    main()