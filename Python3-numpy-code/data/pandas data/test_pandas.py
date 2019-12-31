#! /user/bin/env python3

import pandas as pd
import os

f_dir = os.path.dirname(__file__) + '/taobao_data.csv'
<<<<<<< HEAD
df = pd.read_csv(f_dir, delimiter=',', encoding='gb2312', header=0)
=======
df = pd.read_csv(f_dir, delimiter=',', encoding='utf-8', header=0)
print(df)
>>>>>>> 5c672ea05de38640d5bd3b5a45746d347729d946

# 以上代码在公司win10英文版系统平台运行不能通过，由于编码问题，暂时没解决
# 在家里win7中文版系统，顺利运行通过