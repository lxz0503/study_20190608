# 带用户名密码验证功能的装饰器
# use global dict 来存储用户登录状态
# 这样就不用每次输入用户名和密码
# 多个装饰器装饰一个函数,其执行顺序是从下往上
user_list = [
    {"username": "alex1", "passwd": "123"},
    {"username": "alex2", "passwd": "123"},
    {"username": "alex3", "passwd": "123"},
    {"username": "alex4", "passwd": "123"},
]  # 所有用户的信息存储在列表里,是一个全局的变量
# 当前用户状态,是一个全局的字典
current_dict = {"username": None, "login": False}

def auth_func(func):
    def wrapper(*args, **kwargs):
        if current_dict["username"] and current_dict["login"]:
            res = func(*args, **kwargs)
            return res
        username = input("用户名:")
        passwd = input("密码:")
        for user_dict in user_list:
            if username == user_dict["username"] and passwd == user_dict["passwd"]:
                current_dict["username"] = username
                current_dict["login"] = True
                res = func(*args, **kwargs)
                return res
        else:   # 遍历完列表后，如果都没匹配上，才会执行这个else
            print("错误的用户名或者密码")
    return wrapper

@auth_func
def home():
    print("登录京东!")

@auth_func
def index():
    print("登录其他页面")

if __name__ == "__main__":
    print(current_dict)
    home()
    index()
    print(current_dict)
# ===
# {'username': None, 'login': False}
# 用户名:alex1
# 密码:123
# 登录京东!
# 其他页面
# {'username': 'alex1', 'login': True}

# 输入错误的用户名和密码两次的运行结果如下：
# {'username': None, 'login': False}
# 用户名:a
# 密码:b
# 错误的用户名或者密码
# 用户名:c
# 密码:d
# 错误的用户名或者密码
# {'username': None, 'login': False}