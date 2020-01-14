from django.shortcuts import render, redirect
from datetime import datetime
from .models import Post

# Create your views here.
def homepage(request):
    posts = Post.objects.all()
    now = datetime.now()
    return render(request, 'index.html', locals())


def showpost(request, slug):
    try:
        post = Post.objects.get(slug = slug)
        if post != None:
            return render(request, 'post.html', locals())
    except:
        return redirect('/')

def news(request):
    info = {'name': 'xiaozhan', 'addr': 'beijing', 'age': 30}
    return render(request, 'news.html', locals())