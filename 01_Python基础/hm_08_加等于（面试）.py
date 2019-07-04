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


gl_list = [1, 2, 3]
demo(gl_list)
print(gl_list)