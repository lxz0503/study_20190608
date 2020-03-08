# 一行代码实现删除列表中重复的值 ?
basket = ['apple', 'orange', 'apple', 'pear', 'orange', 'banana']   # 创建一个list
# new_set = set(basket)
# print(type(new_set))       # <class 'set'>
# new_list = list(new_set)
# print(new_list)     # change set to list    # ['apple', 'orange', 'pear', 'banana']
# print("集合是一个无序的不重复元素序列", basket)

print(list(set(basket)))