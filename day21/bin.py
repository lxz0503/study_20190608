# bin.py通常是执行文件，即执行函数入口
# 在运行当前py文件的时候，系统会以当前的路径作为扫描路径的基础
from my_module import main
import sys
main.run()
print(sys.path)  # 'D:\\xiaozhan_git\\study_20190608\\day21'