#!/usr/bin/env python3
# coding=utf-8
# 例如log文件中，日期格式为'yyyy-mm-dd'
# 想修改为美国日期格式'mm/dd/yyyy'

# re.sub(pattern, repl, string, count=0, flags=0)
# 参数：
#
# pattern : 正则中的模式字符串。
# repl : 替换的字符串，也可为一个函数。
# string : 要被查找替换的原始字符串。
# count : 模式匹配后替换的最大次数，默认 0 表示替换所有的匹配。
# flags : 编译时用的匹配模式，数字形式。

import re
# 正则表达式分组，后面的\1,\2,\3表示正则表达式匹配到的三个分组，1，2，3表示位置
f = open('file_test').read()
print('old file content is:\n', f)
new_f = re.sub(r'(\d{4})-(\d{2})-(\d{2})', r'\2/\3/\1', f)
print('new content is:\n', new_f)
# 方法二： 正则表达式分组起名字，注意下面的格式，都是用?P<>
new_f = re.sub(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})', r'\g<month>/\g<day>/\g<year>', f)
# print(new_f)
# 把修改后的文本内容写进新的文件
with open('new_file_test.txt', 'w') as f:
    f.write(new_f)


