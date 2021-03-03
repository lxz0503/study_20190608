#!/usr/bin/env python3
# coding=utf-8

# 在显示元组内容的时候，避免了用0,1,2等数字，而是用有意义的名字来显示
from collections import namedtuple

# the first parameter is a str, usually name it with the same variable
Student = namedtuple('Student', ['name', 'age', 'sex', 'email'])
s = Student('xiaozhan', '35', 'male', '123@163.com')
print('The element of tuple is\n{0}-{1}-{2}-{3}'.format(s.name, s.age, s.sex, s.email))

#
s1 = Student(name='beijing', age=40, sex='male', email='1111@163.com')
print('The element of tuple is\n{0}-{1}-{2}-{3}'.format(s1.name, s1.age, s1.sex, s1.email))