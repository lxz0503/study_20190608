from django.shortcuts import render
import json
import urllib
from django.conf import settings
from . import models, forms
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.sessions.models import Session
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# Create your views here.
# def index(request):
#     years = range(1960,2021)
#     try:
#         urid = request.GET['user_id']
#         urpass = request.GET['user_pass']
#         uryear = request.GET['byear']
#         urfcolor = request.GET.getlist('fcolor')
#     except:
#         urid = None

#     if urid != None and urpass == '12345':
#         verified = True
#     else:
#         verifeid = False
#     return render(request, 'index.html', locals())

def login(request):
    if request.method == 'POST':
        login_form = forms.LoginForm(request.POST)
        if login_form.is_valid():
            login_name=request.POST['username'].strip()
            login_password=request.POST['password']
            user = authenticate(username=login_name, password=login_password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    print("success")
                    messages.add_message(request, messages.SUCCESS, '成功登录了')
                    return redirect('/')
                else:
                    messages.add_message(request, messages.WARNING, '账号尚未启用')
            else:
                messages.add_message(request, messages.WARNING, '登录失败')
        else:
            messages.add_message(request, messages.INFO,'请检查输入的字段内容')
    else:
        login_form = forms.LoginForm()
    return render(request, 'login.html', locals())



def logout(request):
    auth.logout(request)
    messages.add_message(request, messages.INFO, "成功注销了")
    return redirect('/')




def index(request, pid=None, del_pass=None):
    if request.user.is_authenticated:
        username = request.user.username
        useremail = request.user.email
        try:
            user = models.User.objects.get(username=username)
            diaries = models.Diary.objects.filter(user=user).order_by('-ddate')
        except:
            pass
    messages.get_messages(request)
    return render(request, 'index.html', locals())




@login_required(login_url='/login/')
def userinfo(request):
    if request.user.is_authenticated:
        username = request.user.username
        try:
            user = User.objects.get(username=username)
            userinfo = models.Profile.objects.get(user=user)
        except:
            fail = 'fail'
    return render(request, 'userinfo.html', locals())


# def index(request, pid=None, del_pass=None):
#     posts = models.Post.objects.filter(enabled = True).order_by('-pub_time')[:30]
#     moods = models.Mood.objects.all()
#     try:
#         user_id = request.GET['user_id']
#         user_pass = request.GET['user_pass']
#         user_post = request.GET['user_post']
#         user_mood = request.GET['mood']
#     except:
#         user_id = None
#         message = '如果要张贴信息，则每一个字段都要填...'

#     if del_pass and pid:
#         try:
#             post = models.Post.objects.get(id=pid)
#         except:
#             post = None
#         if post:
#             if post.del_pass == del_pass:
#                 post.delete()
#                 message = "数据删除成功"
#             else:
#                 message = "密码错误"
#     elif user_id != None:
#         mood = models.Mood.objects.get(status=user_mood)
#         post = models.Post.objects.create(mood=mood, nickname=user_id, del_pass=user_pass, message=user_post)
#         post.save()
#         message='成功保存！请记得你的编辑密码[{}]!，信息需经审查后才会显示。'.format(user_pass)

#     return render(request, 'index.html', locals())


def listing(request):
    posts = models.Post.objects.filter(enabled=True).order_by('-pub_time')[:150]
    moods = models.Mood.objects.all()
    return render(request, 'listing.html', locals())


@login_required(login_url='/login/')
def posting(request):
    if request.user.is_authenticated:
        username = request.user.username
        useremail = request.user.email
    messages.get_messages(request)
        
    if request.method == 'POST':
        user = User.objects.get(username=username)
        diary = models.Diary(user=user)
        post_form = forms.DiaryForm(request.POST, instance=diary)
        if post_form.is_valid():
            messages.add_message(request, messages.INFO, "日记已保存")
            post_form.save()  
            return HttpResponseRedirect('/')
        else:
            messages.add_message(request, messages.INFO, '如果要张贴日记，每一个字段都要填...')
    else:
        post_form = forms.DiaryForm()
        messages.add_message(request, messages.INFO, '如果要张贴日记，每一个字段都要填...')
    return render(request, 'posting.html', locals())



def contact(request):
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            message = "感谢您的来信。"
            user_name = form.cleaned_data['user_name']
            user_city = form.cleaned_data['user_city']
            user_school = form.cleaned_data['user_school']
            user_email  = form.cleaned_data['user_email']
            user_message = form.cleaned_data['user_message']
            mail_body = u'''
网友姓名：{}
居住城市：{}
是否在学：{}
反应意见：如下
{}'''.format(user_name, user_city, user_school, user_message)
            send_mail(
    '不吐不快',
    mail_body,
    'a6898208@gmail.com',
    [user_email],
    fail_silently=False,
)

        else:
            message = "请检查您输入的信息是否正确！"
    else:
        form = forms.ContactForm()
    return render(request, 'contact.html', locals())



def post2db(request):
    if request.method == 'POST':
        post_form = forms.PostForm(request.POST)
        if post_form.is_valid():
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req =  urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            ''' End reCAPTCHA validation '''
            if result['success']:
                message = "您的信息已保存，要等管理员启用后才看得到。"
                post_form.save()
                return HttpResponseRedirect('/list/')
            else:
                message = "Invalid reCAPTCHA. Please try again."
        else:
            message = '如果要张贴信息，则每一个字段都要填...'
    else:
        post_form = forms.PostForm()
        message = '如果要张贴信息，则每一个字段都要填...'          

    return render(request, 'post2db.html', locals())