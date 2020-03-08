from hm_23_log_record import *
import os

sys.stdout = Logger("a.log", sys.stdout)     # 初始化类的实例对象
sys.stderr = Logger("a.log_file", sys.stderr)     # redirect std err, if necessary
# now it works
print('print something')
print("执行dir命令后系统返回值:", os.system("dir"))          # 执行成功返回0

