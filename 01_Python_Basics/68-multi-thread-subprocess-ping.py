#!/usr/bin/env python3
# coding=utf-8

import subprocess
import threading
import os,time

def is_reachable(ip):
    # 打印线程ID，证明是在不同线程运行
    current_thread = threading.current_thread()
    print('current thread:', current_thread)
    #
    cmd = "ping -c 1 " + ip
    process = os.popen(cmd)
    output = process.read()
    process.close()
    if "icmp_req" in output:
        print('{0} is alive'.format(ip))
    else:
        print('{0} is not reachable'.format(ip))


def main():
    # 打印主线程ID
    main_thread = threading.current_thread()
    print('main thread:', main_thread)
    #
    with open('ips.txt') as f:
        ips = f.readlines()
        threads = []
        for ip in ips:
            thr = threading.Thread(target=is_reachable, args=(ip,))    # 以元组的方式传参，逗号不能省略
            thr.start()
            threads.append(thr)
    # join的原理就是依次检验线程池中的线程是否结束，没有结束就阻塞直到线程结束，如果结束则跳转执行下一个线程的join函数
        for thr in threads:
            thr.join()

if __name__ == '__main__':
    main()

# 关于thread.setDaemon()
# 若在主线程中创建了子线程，当主线程结束时根据子线程daemon（设置thread.setDaemon(True)）
# 属性值的不同可能会发生下面的两种情况之一：
#
# 如果某个子线程的daemon属性为False，主线程结束时会检测该子线程是否结束，
# 如果该子线程还在运行，则主线程会等待它完成后再退出；
# 如果某个子线程的daemon属性为True，主线程运行结束时不对这个子线程进行检查而直接退出，
# 同时所有daemon值为True的子线程将随主线程一起结束，而不论是否运行完成