# 如果传递的参数是可变类型，在函数内部通过方法修改了数据内容，同样会影响到外部数据
# 可变数据类型：列表list和字典dict；
# 不可变数据类型：整型int、浮点型float、字符串型string和元组tuple


def test(num_list, dict_test):
    num_list.append(9)
    dict_test.setdefault("province", "hebei")
    # dict_test["province"] = dict_test.get("province", "hebei")
    # print(num_list)


gl_list = [1, 2, 3]
dict_test = {"beijing": 1000, "age": 20, "district": "shunyi"}
test(gl_list, dict_test)
print("调用后列表内容是%s" % gl_list)   # 调用后列表内容是[1, 2, 3, 9]
print("调用后字典内容是%s" % dict_test)   # {'beijing': 1000, 'age': 20, 'district': 'shunyi', 'province': 'hebei'}

