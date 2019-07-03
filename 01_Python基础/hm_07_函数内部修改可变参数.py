# 如果传递的参数是可变类型，在函数内部通过方法修改了数据内容，同样会影响到外部数据


def test(num_list):
    num_list.append(9)
    print(num_list)


gl_list = [1, 2, 3]
test(gl_list)
print("调用后列表内容是%s" % gl_list)