from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from users.models import UserProfile, EmailVerifyRecord
from django.db.models import Q
from users.form import LoginForm, RegisterForm
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from utils.email_send import send_register_eamil

# Create your views here.

# 邮箱和用户名都可以登录
# 基础ModelBackend类，因为它有authenticate方法 需要研究
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因 Q为使用并集查询
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))

            # django的后台中密码加密：所以不能password==password
            # UserProfile继承的AbstractUser中有def check_password(self, raw_password):
            if user.check_password(password):
                return user
        except Exception as e:
            return None

# 用类来实现登录函数   研究
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 实例化一个form
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get('username', None)
            pass_word = request.POST.get('password', None)

            # 成功返回user对象,失败None
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                login(request, user)
                return render(request, 'index.html')
            # 只有当用户名或密码不存在，才返回错误信息到前端
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误', 'login_form': login_form})
        # form.is_valid（）已经判断不合法了，所以这里不需要再返回错误信息到前端了
        return render(request, 'login.html', {'login_form':login_form})


# 下面是通用的函数,实现和上面的类一样的功能
# def user_login(request):
#     if request.method == 'POST':
#         # 获取用户提交的用户名和密码
#         user_name = request.POST.get('username', None)
#         pass_word = request.POST.get('password', None)
#         # 成功返回user对象,失败None
#         user = authenticate(username=user_name, password=pass_word)
#         # 如果不是null说明验证成功
#         if user is not None:
#             # 登录
#             login(request, user)
#             return render(request, 'index.html')
#         else:
#             return render(request, 'login.html', {'msg': '用户名或密码错误'})
#
#     elif request.method == 'GET':
#         return render(request, 'login.html')

# 用户注册
class RegisterView(View):
    '''用户注册'''
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email', None)
            # 如果用户已存在，则提示错误信息
            if UserProfile.objects.filter(email=user_name):
                return render(request, 'register.html', {'register_form': register_form, 'msg': '用户已存在'})

            pass_word = request.POST.get('password', None)
            # 实例化一个user_profile对象
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            # 对保存到数据库的密码加密
            user_profile.password = make_password(pass_word)
            user_profile.save()
            send_register_eamil(user_name,'register')
            return render(request,'login.html')
        else:
            return render(request, 'register.html', {'register_form':register_form})


# 激活用户
class ActiveUserView(View):
    def get(self, request, active_code):
        # 查询邮箱验证记录是否存在
        all_record = EmailVerifyRecord.objects.filter(code = active_code)

        if all_record:
            for record in all_record:
                # 获取到对应的邮箱
                email = record.email
                # 查找到邮箱对应的user
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
         # 验证码不对的时候跳转到激活失败页面
        else:
            return render(request, 'active_fail.html')
        # 激活成功跳转到登录页面
        return render(request, "login.html", )


