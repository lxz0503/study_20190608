# 列表进行+=操作相当于调用了列表的extend方法


def demo(num_list):
    """

    :param num_list:
    """
    print("start")
    # num_list += num_list
    num_list.extend(num_list)
    print(num_list)
    print("end")

# test case
gl_list = [1, 2, 3]
demo(gl_list)
print(gl_list)

l = [1, 2, 3]
n = [4, 5, 6]
l.extend(n)   # extend()只有一个参数
print('new list is:\n', l)

# 不同类型的列表也可以相加，拼接在一起
l = [1, 2, 3]
n = ['a', 'b', 6]
new_list = l + n
print('new_list is:\n', new_list)

