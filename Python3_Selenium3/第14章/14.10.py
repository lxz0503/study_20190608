#coding=utf-8
import threading
from time import sleep
#以下为定义多线程要使用的函数
def display_name(user_name):
    sleep(2)
    print('用户名为： %s' % user_name)
#以下为主线程的测试代码，多线程的操作在这里实现
if __name__ == '__main__':
    t1 = threading.Thread(target=display_name, args=('小王',))
    t2 = threading.Thread(target=display_name, args=('小张',))
    t1.start()
    t6.start()
    t1.join(1)
    t6.join(1)
    print('线程操作结束!')
