# http://c.biancheng.net/view/2270.html       refer to this link
# 装饰器本身就是一个闭包函数，不会修改被修饰函数里面的代码，不能修改函数的调用方式。这是原则
# 可以理解为在一个函数外面加另外一个函数，来实现某些功能
# 应用场景，例如, 不能修改函数体
# 装饰器 = 高阶函数 + 函数嵌套 + 闭包
# 带固定参数的装饰器
# import time
#
# def deco(f):                # 有且只有一个参数，以函数名作为参数,就是高阶函数  high level function
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
#     f(3,4)            # 此处设置断点，查看函数如何执行,顺序是先执行deco()函数，跳到11行，然后12行，再地19行，20行，执行完22行，
                        # 再回到def wrapper(a,b)里面的f(a,b)，再第13行，14，15行,再返回到25行，函数执行结束

# 无固定参数的装饰器
import time
def deco(f):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        f(*args, **kwargs)   # *args是用元组传参数，**kwargs是用字典传参数
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
def f2(a, b, c):     # tuple (3,4,5)
    print("be on")
    time.sleep(1)
    print("result is %d" % (a+b+c))
#
if __name__ == '__main__':
    f2(3,4,5)
    # f(3,4)