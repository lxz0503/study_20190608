# 创建一个Exception类的对象，传递一个参数
# 当条件满足时，使用raise函数抛出异常
def input_password():
    # 提示用户输入密码
    # 判断密码长度>=8，返回用户输入的密码
    pwd = input("请输入密码：")
    if len(pwd) >= 8:
        return pwd

    print("主动抛出异常")
    # 创建异常对象时，可以使用错误信息字符串作为参数
    ex = Exception("密码长度不够")
    # 如果<8,就主动抛出异常
    raise ex 


try:
    print(input_password())
except Exception as result:
    print(result)