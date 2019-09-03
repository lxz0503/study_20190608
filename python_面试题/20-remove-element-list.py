def removeElement(l, val):
    while val in l:
        l.remove(val)
    print(l)
    # for i in l:                # for循环却不行，原因，删除一个2后，后面的元素就往前移动一位，但是删除是根据原有list的下表来进行的，所以会漏掉
    #     print(i,end=" ")
    #     if i == val:
    #         l.remove(i)

    return l                  # 因为list是可变对象，所以在函数内部修改，也等于在外部修改

# for loop is not suitable. please refer to the answer:
# When using a for loop,
# if you remove the item from the array you'll be messing up the indexes of an array.
# So when iterating through the array the indexes of the array will be changing because you're removing values from it.
# In my approach, as long as the target value exists in the array remove the target value.
# My solution doesn't depend on any index to read values from the array

nums = [0,1,2,2,3,0,4,2]
val = 2
res = removeElement(nums, val)     # 在函数内部修改了nums这个列表的内容
print(res)
# print(nums)                      # 在函数内部已经修改了列表内容

# [2, 2]
# [2, 2]

# 如果要用for循环来删除元素，就不要对这个原有序列做迭代，方法如下：
nums = [0, 1, 2, 2, 3, 0, 4, 2]
l_remove = []    # 存放要删除的元素
for i in nums:
    # print(i,end="#")      #   0#1#2#3#0#4#2#
    if i == 2 or i == 3:
        l_remove.append(i)
print(l_remove)

for i in l_remove:        # 对新的序列做迭代
    nums.remove(i)         # 原有序列直接删除元素，不做迭代操作
print('the new list is', nums)

# method 3: 使用字典函数，此种方法将不会改变列表内元素顺序
# 键必须是唯一的，但值则不必。
# 值可以取任何数据类型，但键必须是不可变的，如字符串，数字或元组
nums = [0, 1, 2, 2, 3, 0, 4, 2]
d = {}
d = d.fromkeys(nums)     # 设置了字典的键
l = list(d.keys())
print(l)

# method 4: 用for loop来删除，append
def del_duplicate_list(L):
    L1 = []              # 用新的列表存储不重复的元素
    for i in L:          # 对原来的序列进行迭代
        if i not in L1:  # 判断元素是否在不重复那个列表里
            L1.append(i)  # 如果不在，那就是不重复的，添加到新的不重复列表
    return L1

nums = [0, 1, 2, 2, 3, 0, 4, 2]
L = del_duplicate_list(nums)
print(L)

# method 5: 使用filter，lambda,用于去除列表中所有某个特定的元素
nums = [0, 1, 2, 2, 3, 0, 4, 2]
f = filter(lambda n: n != 2, L)
L = list(f)
print(L)


# 原文链接：https://blog.csdn.net/qq_41551919/article/details/83060738

