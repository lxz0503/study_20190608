#! /usr/bin/env python3
# coding=utf-8

from xml.etree.ElementTree import Element, ElementTree, tostring

e = Element('Data')   # 根节点
# e.set('name', 'abc')
# e.text = '123'
print(tostring(e))     # b'<Data name="abc">123</Data>'
e1 = Element('Row')   # 创建节点e1
e2 = Element('Open')  # 创建节点e2
e2.text = '2020-01-24'  # 设置节点e2的内容
e3 = Element('price')   # 创建并设置设置节点e3的内容
e3.text = '20'
e1.append(e2)       # 把节点e2和e3挂到节点e1的下面
e1.append(e3)
e.append(e1)       # 把节点e1挂到节点e的下面
# print(tostring(e))
et = ElementTree(e)     # 写入一个xml文件
et.write('xml_test.xml')
