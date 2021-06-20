#coding=utf-8
import threading
from time import sleep

def dispaly_name(user_name):
    sleep(2)
    print('用户名为： %s' % user_name)


class MyThread(threading.Thread):
    def __init__(self,func,args):
        super(MyThread,self).__init__()
        self.func = func
        self.args = args

    def run(self):
        print("ThreadName: "+self.name)
        self.func(self.args)

if __name__ == "__main__":
    t1 = MyThread(func=dispaly_name,args=("小王",))
    t2 = MyThread(func=dispaly_name,args=("小张",))
    t1.start()
    t6.start()
    t1.join(1)
    t6.join(1)
    print("线程操作结束！")
