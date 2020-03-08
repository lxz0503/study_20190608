# 异常的传递，指当函数或者方法出现异常，会将异常传递给调用函数的一方
# 如果传递到主程序，仍然没有异常处理，程序才会被终止
# 在实际开发中，可以在主程序增加异常捕获，就不用在代码中增加大量的异常捕获
def demo1():
    return int(input("please input a integer:"))

def demo2():
    return demo1()

# 主程序
try:
    print(demo2())
# except ValueError:
#     print("input a right number")
except Exception as result:
    print("unknown error:%s" % result)
