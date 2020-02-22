# *_* coding : UTF-8 *_*
# 开发团队   ：明日科技
# 开发人员   ：Administrator
# 开发时间   ：2019/7/1  15:34
# 文件名称   ：demo01.py
# 开发工具   ：PyCharm

language_dict = {'01':'希腊文输入', '02':'俄文输入', '03':'德文输入', '04':'丹麦文输入', '05':'西班牙文输入',
       '06':'法文输入', '07': '荷兰文输入', '08':'葡萄牙文输入', '09': '意大利文输入'}
for key, value in language_dict.items():      #  遍历字典
    print(key, value)                #  输出语言菜单

