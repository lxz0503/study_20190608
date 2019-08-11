# 但是当发生异常时，直接使用无参数的 debug()、info()、warning()、error()、critical() 方法并不能记录异常信息，
# 需要设置 exc_info 参数为 True 才可以，或者使用 exception() 方法，还可以使用 log() 方法，
# 但还要设置日志级别和 exc_info 参数
# https://cloud.tencent.com/developer/article/1354396

import logging
import os
import psutil   # 这个模块可以监测一些系统信息

logging.basicConfig(filename="test.log",
                    filemode="w",
                    format="%(asctime)s %(filename)s: [line:%(lineno)d] %(levelname)s: %(message)s",  # 这个filename是脚本名字
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.DEBUG)
# 打印出来的log格式： 2019-08-10 21:46:03 day22-1-logging.py: [line:31] DEBUG: cpu使用率：0.0
a = 5
b = 0
try:
    c = a / b
except Exception as e:
    # 下面三种方式三选一，推荐使用第一种
    logging.exception("Exception occurred")      # 只有异常发生时才会记录log
    #logging.error("Exception occurred", exc_info=True)
    #logging.log(level=logging.DEBUG, msg="Exception occurred", exc_info=True)

# 下面的不是针对异常log，而是记录普通log
p1 = psutil.Process(os.getpid())
cpu_percent = 'cpu使用率：' + str(p1.cpu_percent(1))
mem_percent = 'memory usage：' + str(p1.memory_percent)
i = 0
while i < 5:
    logging.debug(cpu_percent)    # 记录普通log，一把先要把变量内容提前设置，例如cpu_percent
    logging.debug(mem_percent)
    i = i + 1



