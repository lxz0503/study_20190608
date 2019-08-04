# 记录屏幕输出的log，可以用用下面的方法
# 也可以用tee名利重定向，简单有效
# python test.py 2>&1 | tee test.log
# 还可以用下面的，没看懂
import sys

class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'a')

    def write(self, message):      # 断点调试发现上来就跳转这里执行，不明白
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

# 具体使用可以把上面的类封装到一个模块，然后在外面初始化调用，例如下面
if __name__ == "__main__":
    sys.stdout = Logger("a.log", sys.stdout)     # 初始化类的实例对象
    sys.stderr = Logger("a.log_file", sys.stderr)     # redirect std err, if necessary
    # now it works
    print('print something')