# 但是当发生异常时，直接使用无参数的 debug()、info()、warning()、error()、critical() 方法并不能记录异常信息，
# 需要设置 exc_info 参数为 True 才可以，或者使用 exception() 方法，还可以使用 log() 方法，
# 但还要设置日志级别和 exc_info 参数
# https://cloud.tencent.com/developer/article/1354396

import logging

logging.basicConfig(filename="test.log",
                    filemode="w",
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)
a = 5
b = 0
try:
    c = a / b
except Exception as e:
    # 下面三种方式三选一，推荐使用第一种
    logging.exception("Exception occurred")
    #logging.error("Exception occurred", exc_info=True)
    #logging.log(level=logging.DEBUG, msg="Exception occurred", exc_info=True)

##


