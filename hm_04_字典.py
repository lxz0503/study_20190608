xiaoming_dict = {"name": "小明",
                 "qq": "123456",
                 "phone": "10086"}
for k in xiaoming_dict:
    print("%s - %s" % (k, xiaoming_dict[k]))
""" 将多个字典放在一个列表，遍历"""
card_list = [
    {"name": "小明",
     "qq": "123456",
     "phone": "10086"},
    {"name": "张三",
     "qq": "12345",
     "phone": "23086"}
]

for card_info in card_list:
    print(card_info)

s = "hello hello"
print("子串llo出现了%d次" % (s.count("llo")))
if s.startswith("h"):
    print("yes")
if s.endswith("o"):
    print("end with o")
print(s.find("e"))
new_s = s.replace("he", "aaa")
print(new_s)
# for循环在实际当中的使用，for 结束后，在下面增加一个  else，提示遍历后的结果
find_name = "张"
for stu_dict in card_list:
    if stu_dict["name"] == find_name:
        print("I found %s" % find_name)
        # 找到后就退出循环，不再遍历
        break
else:
    print("没有找到%s" % find_name)

print("循环结束")
