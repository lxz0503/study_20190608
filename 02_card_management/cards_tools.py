card_list = []


def show_menu():
    print("*" * 20)
    print("欢迎使用名片管理系统 V1.0")
    print("")
    print("1.新增名片")
    print("2.显示名片")
    print("3.搜索名片")
    print("")
    print("0.退出系统")


def new_card():
    """新增名片"""
    print("-" * 20)
    print("新增名片")
    # 1.提示用户输入名片的详细信息
    name_str = input("请输入姓名: ")
    phone_str = input("请输入电话：")
    qq_str = input("请输入qq：")
    email_str = input("请输入邮箱：")
    # 2.使用用户输入的信息建立一个名片字典
    card_dict = {"name": name_str, "phone": phone_str, "qq": qq_str, "email": email_str}
    # 3.将名片字典添加到列表中
    card_list.append(card_dict)
    print(card_list)
    # 4.提示用户添加成功
    print("添加%s的名片成功!" % name_str)


def show_all():
    """显示所有名片"""
    print("-" * 20)
    print("显示所有名片")
    # 判断是否存在名片记录，如果没有，提示用户并且返回
    if len(card_list) == 0:
        print("没有用户,请添加用户")
        # return可以返回一个函数的执行结果
        # 后面的代码就不会被执行
        # 如果return后面没有任何的内容，表示会返回到调用函数的位置
        # 并且不会返回任何的结果
        return
    # 打印表头
    for name in ["姓名", "电话", "qq", "邮箱"]:
        print(name, end="\t\t")
    print("")
    # 变量名片列表,依次输出字典信息
    for card_dict in card_list:
        print("%s\t\t%s\t\t%s\t\t%s\t\t" % (card_dict["name"],
                                            card_dict["phone"],
                                            card_dict["qq"],
                                            card_dict["email"]))


def search_card():
    """搜索名片"""
    print("-" * 20)
    print("搜索名片")
    # 1.提示用户要输入搜索的姓名
    find_name = input("请输入要搜索的姓名：")
    # 2.遍历名片列表，查询要搜索的姓名，如果没有找到，需要提示用户
    for card_dict in card_list:
        if card_dict["name"] == find_name:
            print("姓名\t\t电话\t\tQQ\t\t邮箱")
            print("=" * 30)
            print("%s\t\t%s\t\t%s\t\t%s\t\t" % (card_dict["name"],
                                                card_dict["phone"],
                                                card_dict["qq"],
                                                card_dict["email"]))
            print("找到了%s" % find_name)
            # 针对找到的名片记录执行修改和删除操作
            deal_card(card_dict)
            break
    else:
        print("没有找到%s" % find_name)


def deal_card(find_dict):    # 传递的参数是字典。是可变类型，所以在deal_card函数内部修改这个字典参数后，
    # 实际上也修改了原始的字典,参考hm_07函数内部修改可变参数
    """处理查找到的名片

    :param find_dict: 查找到的名片
    """
    print(find_dict)
    action_str = input("请选择要执行的操作 "
                       "[1] 修改 [2] 删除 [0] 返回上级菜单")
    if action_str == "1":
        # find_dict["name"] = input("姓名:")
        # find_dict["phone"] = input("电话:")
        # find_dict["qq"] = input("QQ:")
        # find_dict["email"] = input("邮箱:")
        find_dict["name"] = input_card_info(find_dict["name"], "姓名:")
        find_dict["phone"] = input_card_info(find_dict["phone"], "电话:")
        find_dict["qq"] = input_card_info(find_dict["qq"], "QQ:")
        find_dict["email"] = input_card_info(find_dict["email"], "邮箱:")
        print("修改名片成功")
    elif action_str == "2":
        card_list.remove(find_dict)
        print("删除名片")


def input_card_info(dict_value, tip_message):
    """输入名片信息
    :param dict_value: 字典中原有值
    :param tip_message:输入的提示文字
    :return:如果用户输入了内容，就返回结果
            如果没有输入内容，就返回字典中原有值
    """
    # 1.提示用户输入内容
    result_str = input(tip_message)
    # 2.针对用户的输入进行判断，如果输入了内容，直接返回结果
    if len(result_str) > 0:
        return result_str
    else:
        return dict_value
    # 3.如果用户没有输入内容，返回字典中原有的值
