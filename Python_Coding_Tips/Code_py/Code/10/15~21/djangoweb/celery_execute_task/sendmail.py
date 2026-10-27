import time

from django.core.mail import send_mail
from django.conf import settings
from celery import Celery


# 初始化django环境
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoweb.settings')
django.setup()

# 创建实例对象
# 第一个parameter：可随意命名，但一般为本文件所在路径
# broker：指定中间人，斜杠后指定第几个数据库
app = Celery('celery_execute_task.sendmail', broker='redis://localhost:6379/3')


# 定义任务函数
@app.task
def send_activate_email(to_email, username, token):
    """发送激活邮件"""

    # 组织邮件信息
    subject = '明日科技欢迎您'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>%s, 欢迎您注册明日科技会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/mail/activate/%s">http://127.0.0.1:8000/mail/activate/%s</a>' % (username, token, token)

    send_mail(subject, message, sender, receiver, html_message=html_message)
    time.sleep(5)
