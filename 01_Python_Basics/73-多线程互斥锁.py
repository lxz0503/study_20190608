#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/6/2022 7:25 PM
@file:73-多线程互斥锁.py
@project:openpyxl_excel
"""
import threading

g_num = 0    # 全局变量
lock = threading.Lock()   # 创建一个互斥锁
# 执行到哪个任务，就上锁，直到执行完，然后释放锁

def task1():
    lock.acquire()   # 上锁
    for i in range(100):
        global g_num
        g_num += 1
    print('task1:', g_num)
    lock.release()   # 释放锁

def task2():
    lock.acquire()  # 上锁
    for i in range(100):
        global g_num
        g_num += 1
    print('task2:', g_num)
    lock.release()   # 释放锁


if __name__ == "__main__":
    first_thread = threading.Thread(target=task1)
    second_thread = threading.Thread(target=task2)
    # 启动线程
    first_thread.start()
    second_thread.start()
