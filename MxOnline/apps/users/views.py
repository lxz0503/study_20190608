from django.shortcuts import render
from django.contrib.auth import authenticate,login

# Create your views here.

def user_login(request):
    if request.method == 'POST':
        # 获取用户提交的用户名和密码
        user_name = request.POST.get('username', None)
        pass_word = request.POST.get('password', None)
        # 成功返回user对象,失败None
        user = authenticate(username=user_name, password=pass_word)
        # 如果不是null说明验证成功
        if user is not None:
            # 登录
            login(request, user)
            return render(request, 'index.html')
        else:
            return render(request, 'login.html', {'msg': '用户名或密码错误'})

    elif request.method == 'GET':
        return render(request, 'login.html')


# define user and city and then they can be written into the html and shown in browser
# after login, it will run this function
def home(request):
    return render(request, 'home.html', {'user': 'admin', 'city': 'beijing'})
