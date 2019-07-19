# bin.py通常是执行文件，即执行函数入口
# 在运行当前py文件的时候，系统会以当前的路径作为扫描路径的基础
# 如果是有多个层级目录，每一级目录都是一个package（即每一级下面都有__init__.py文件）
# 要导入最里面一层package的里面的函数(web3是最里面一层package,cal.py是里面的文件)
# from web.web1.web2.web3 import cal
from my_module import main
import sys
main.run()
print(sys.path)  # 'D:\\xiaozhan_git\\study_20190608\\day21'