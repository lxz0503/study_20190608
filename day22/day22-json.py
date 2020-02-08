import json
# a里面的内容就是所谓的json文件格式，其实就是字典
# JSON 对象在大括号{}中书写
# JSON 数组在中括号中书写,例如下面的
# 对象 "sites" 是包含三个对象的数组。每个对象代表一条关于某个网站（name、url）的记录

record_json = {
    "sites": [                                         # 列表里每个都是字典
    { "name":"菜鸟教程" , "url":"www.runoob.com" },     # 字典
    { "name":"google" , "url":"www.google.com" },
    { "name":"微博" , "url":"www.weibo.com" }
             ]
 }

# print(type(record_json))      # <class 'dict'>
for k in record_json:
    print("%s----%s" % (k,record_json[k]))

for k, v in record_json.items():
    print("%s--%s" % (k, v))
print(v)

# 通过 JavaScript，您可以创建一个对象数组，并像这样进行赋值：
# var sites = [
#     { "name":"runoob" , "url":"www.runoob.com" },
#     { "name":"google" , "url":"www.google.com" },
#     { "name":"微博" , "url":"www.weibo.com" }
# ];

# 可以像这样访问 JavaScript 对象数组中的第一项（索引从 0 开始）：
# sites[0].name;
# python3 和 json数据之间的转换
# json.dumps(): 对数据进行编码。把元组,字典，列表  进行序列化 转化为json格式的字符串，类型为str.   serialization,
# json.loads(): 对数据进行解码。把json格式字符串  转化为   python的列表或者字典格式     anti-serialization
# Python 字典类型转换为 JSON 对象
data1 = {
    'no': 1,
    'name': 'Runoob',
    'url': 'http://www.runoob.com'
}
print(type(data1))        # 这时候数据类型是字典格式
json_str = json.dumps(data1)    # 用dumps后字典就转化为json格式的字符串，虽然看起来一样
t = json.dumps(data1, sort_keys=True)
print('按照key排序', t)
print(type(json_str))      # 就是字符串
print("Python 原始数据：", repr(data1))
print("JSON 对象：", json_str)

#
# 将 JSON 对象转换为 Python 字典
data2 = json.loads(json_str)
print(type(data2))      # <class 'dict'>
print("data2['name']: ", data2['name'])
print("data2['url']: ", data2['url'])

# 如果你要处理的是文件而不是字符串，你可以使用 json.dump() 和 json.load() 来编码和解码JSON数据
# 写入 JSON 数据
data = {        # 定义一个字典
    'no': 1,
    'name': 'Runoob',
    'url': 'http://www.runoob.com'
}
with open('data.json', 'w') as f:
    json.dump(data, f)      # 把data的内容写到一个json文件里面

# 从json格式文件中读取数据,用python的字典来处理数据
with open('data.json', 'r') as f:
    data = json.load(f)
print(type(data))           # <class 'dict'>
for k in data:
    print("字典数据%s--%s" % (k, data[k]))


# json.loads()解码python json格式,参数是json格式的字符串
# json.load()加载python json格式文件,参数是一个文件句柄
# dump()有两个参数，第一个是python数据，第二个是文件句柄
# dumps()的参数只有一个，python数据，例如元组，列表，字典


