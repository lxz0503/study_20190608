#!/usr/bin/python3
import os

path_test = r'D:\xiaozhan_git\study_20190608\day22\day22-time.py'
print(os.path.basename('/root/runoob.txt'))         # 返回文件名 runoob.txt
print(os.path.dirname('/root/abc/runoob.txt'))          # 返回目录路径 /root/abc
print(os.path.split('/root/runoob.txt'))             # 分割文件名与路径 ('/root', 'runoob.txt')
print(os.path.join('root', 'test', 'runoob.txt'))    # 将目录和文件名合成一个路径root\test\runoob.txt
print(os.path.isfile(path_test))    # True

print(os.getcwd())     # D:\xiaozhan_git\study_20190608\day22

# os.chdir()   os.system()   os.popen().read()
# os.mkdir()    os.remove()    