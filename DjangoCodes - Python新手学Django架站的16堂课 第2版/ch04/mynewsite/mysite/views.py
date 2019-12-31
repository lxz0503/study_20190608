# _*_ coding: utf-8 _*_
from django.shortcuts import render
from django.http import HttpResponse, Http404
import random
from mysite.models import Product


def index(request):
    quotes = ['今日事，今日毕',
            '要怎么收获，先那么栽',
            '知识就是力量',
            '一个人的个性就是他的命运']
    quote = random.choice(quotes)
    return render(request, 'index.html', locals())


def about(request):
    return render(request, 'about.html', locals())


def listing(request):
    products = Product.objects.all()	
    return render(request, 'list.html', locals())


def disp_detail(request, sku):
    try:
        p = Product.objects.get(sku=sku)
    except Product.DoesNotExist:
        raise Http404('找不到指定的产品编号')
    return render(request, 'disp.html', locals())