# *_* coding : UTF-8 *_*
# 开发团队   ：明日科技
# 开发人员   ：Administrator
# 开发时间   ：2019/7/2  16:42
# 文件名称   ：demo.py
# 开发工具   ：PyCharm
num2 = "1314521"
print(max(x for x in range(10)))   # 取出0~9之间的最大值，输出结果为：9
print(max(num2, key=lambda x: abs(int(x))))  # 取出字符串num2中的最大数字，输出结果为：5
