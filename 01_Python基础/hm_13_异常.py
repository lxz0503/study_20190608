# 利用下面的方法可以捕获任何未知错误
# except Exception as result
# 尽量少用异常处理,因为会降低代码的可读性
# 只有在有些异常无法预知的情况下，才会用异常处理

# !usr/bin/env python
try:
    num = int(input("input a integer:"))
    result = 8/num
    print("the result is %s" % result)
except ValueError:
    print("value error")
except ZeroDivisionError:
    print("zero value error")
except Exception as result:
    print("未知错误:%s" % result)
else:
    print("尝试成功，无异常，就执行此处代码")
finally:
    print("无论成功与否，都执行此处代码")
