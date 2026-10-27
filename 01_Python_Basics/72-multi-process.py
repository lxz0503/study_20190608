#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:4/5/2022 8:46 PM
@file:72-multi-process.py
@project:openpyxl_excel
"""
import multiprocessing
import time
import os

def dance():
    dance_process_id = os.getpid()
    print('dance process id is:', dance_process_id, multiprocessing.current_process())
    # parent process id
    parent_process_id = os.getppid()
    print('parent process id is:', parent_process_id, multiprocessing.current_process())
    # parent process id is: 11480 <Process name='dance process' parent=11480 started>
    for i in range(3):
        print('dance....')
        time.sleep(0.2)

def sing():
    for i in range(3):
        print('sing....')
        time.sleep(0.2)


if __name__ == "__main__":
    main_process_id = os.getpid()
    print('main process id is:', main_process_id, multiprocessing.current_process())
    # 创建子进程
    dance_process = multiprocessing.Process(target=dance,name='dance process')
    sing_process = multiprocessing.Process(target=sing,name='sing process')
    print('dance process:', dance_process)
    print('sing process:', sing_process)
    # 执行进程，进程执行是由CPU调动，无序
    dance_process.start()
    sing_process.start()
# main process id is: 17584 <_MainProcess name='MainProcess' parent=None started>
# dance process: <Process name='dance process' parent=17584 initial>
# sing process: <Process name='sing process' parent=17584 initial>