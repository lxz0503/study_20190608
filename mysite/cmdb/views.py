from django.shortcuts import render

# Create your views here.

from django.shortcuts import HttpResponse


def test(request):
    return HttpResponse("hello world")