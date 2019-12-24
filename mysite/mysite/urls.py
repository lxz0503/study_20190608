"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from apitest.views import *
from product.views import *

urlpatterns = [
    path('admin/', admin.site.urls),  # ???admin????????????
    # path('test/', views.test),  # ?????????
    path('apitest/', apitest),  # ?????????
    path('login/', login),  # ?????????
    path('home/', home),  # ?????????
    path('logout/', logout),  # ?????????
    path('product_manage/', product_manage),  # ?????????

    # path('', views.index),    # ?????admin????????????????        # the path is ''
]
