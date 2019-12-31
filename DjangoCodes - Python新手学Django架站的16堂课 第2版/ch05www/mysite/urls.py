from django.urls import path, re_path
from . import views

urlpatterns = [
    path('post/<int:yr>/', views.postNum2),
]