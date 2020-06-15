# 装饰器本身就是一个函数，不会修改被修饰函数里面的代码，不能修改函数的调用方式。这是原则
# 可以理解为在一个函数外面加另外一个函数，来实现某些功能
# 应用场景，例如, 不能修改函数体
# 装饰器 = 高阶函数 + 函数嵌套 + 闭包
# 带固定参数的装饰器
# import time
#
# def deco(f):                # 以函数名作为参数,就是高阶函数  high level function
#     def wrapper(a,b):       # 函数嵌套       function nesting
#         start_time = time.time()
#         f(a,b)
#         end_time = time.time()
#         execution_time = (end_time - start_time)*1000
#         print("time is %d ms" % execution_time)
#     return wrapper          # 返回值是嵌套函数的函数名
#
# @deco
# def f(a,b):
#     print("be on")
#     time.sleep(1)
#     print("result is %d" %(a+b))   # 执行完这一步，跳转到def wrapper(a,b)里面的f(a,b)
#
# if __name__ == '__main__':
#     f(3,4)            # 此处设置断点，查看函数如何执行,顺序是先执行deco()函数，在执行f(a,b)之前跳转到def f(a,b)函数里面

# 无固定参数的装饰器
import time
def deco(f):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        f(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        print("time is %d ms" % execution_time)
    return wrapper

@deco
def f(a, b):
    print("be on")
    time.sleep(1)
    print("result is %d" %(a+b))

@deco
def f2(a, b, c):
    print("be on")
    time.sleep(1)
    print("result is %d" %(a+b+c))
#
if __name__ == '__main__':
    f2(3,4,5)
    f(3,4)