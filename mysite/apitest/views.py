from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth import authenticate,login

# Create your views here.


def apitest(request):
    return HttpResponse("this is api test")

def login(request):
    if request.POST:
        username = ''
        password = ''
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        city = 'beijing'
        if user is not None and user.is_active:
            auth.login(request, user)
            request.session['user'] = username
            response = HttpResponseRedirect('/home/')
            return response   # ???why
        else:
            return render(request, 'login.html', {'error': 'username or password error'})
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return render(request, 'login.html')

# define user and city and then they can be written into the html and shown in browser
# after login, it will run this function
def home(request):
    return render(request, 'home.html', {'user': 'admin', 'city': 'beijing'})



