# time module practice

import time
import calendar

# time format: 2019-07-18 20:52:49
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

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
