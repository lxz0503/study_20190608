# 可以把下面的设置成全局的，记录系统输出log
import sys
import os
f = open("a.log", "w")
sys.stdout = f
sys.stderr = f
# 下面是具体的需要记录的信息
print("aaaa")
print(os.system("dir"))   # log里面只会保存返回值0或者1，具体信息不会存到log，因为是和系统的交互
f.close()