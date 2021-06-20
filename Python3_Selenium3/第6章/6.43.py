# coding=utf-8
from pywinauto.application import Application
import time

app = Application()
# ��λ������
app = app.connect(title_re="��", class_name="#32770")
# �����ļ�·��
app['��']["EDit1"].SetEditText("D:\soft\ip.txt ")
time.sleep(2)
# ������ť
app["��"]["Button1"].click()
print("end")
