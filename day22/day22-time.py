# time module practice

import time
import calendar
from datetime import datetime

# strptime：
# p表示parse，表示分析的意思，所以strptime是给定一个时间字符串和分析模式，返回一个datetime类时间对象。
# strftime：
# f表示format，表示格式化，和strptime正好相反，要求给一个时间对象和输出格式，返回一个时间字符串
dmy = '20-01-2020'   # 日 月 年的格式
date = datetime.strptime(dmy, '%d-%m-%Y').date()     # 后面的date()函数表示只计算到年月日，否则就包括小时分钟秒
print('after strptime is', date)     # after strptime is 2020-01-20   转换后变成了年月日的格式


# time format: 2019-07-18 20:52:49
# print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
time_stamp = '20191113170215'
t = time.strftime('%Y-%m-%d', time.strptime(time_stamp, '%Y%m%d%H%M%S'))
print(t)          # 2019-11-14

# 查看当前时间常用的函数如下,精确到秒
cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print(cur_time)      # 2019-11-14 15:31:28


# Thu Jul 18 20:56:29 2019,
print(time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()))

# 计算程序运行的时间间隔
start = time.perf_counter()
for i in range(10):
    print(i, end="\t")
    time.sleep(1)
print()
stop = time.perf_counter()
print("time interval is %s" % (stop - start))

# print the month of 7
cal = calendar.month(2019, 7)
print(cal)

# print the calender of year 2019
cal = calendar.calendar(2019, 2, 1, 6)
# print(cal)

#
import random
print(random.randint(1, 3))   # 2
print(random.choice([11, 22, 44]))  # 22
