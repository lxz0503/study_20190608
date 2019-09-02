def removeElement(l, val):
    while val in l:
            l.remove(val)
    # for i in l:                # for循环却不行，不知道原因
    #     if val == i:
    #         l.remove(val)
    return l                  # 因为list是可变对象，所以在函数内部修改，也等于在外部修改


nums = [0,1,2,2,3,0,4,2]
val = 2
res = removeElement(nums, val)     # 在函数内部修改了nums这个列表的内容
print(res)
# print(nums)                      # 在函数内部已经修改了列表内容

# [2, 2]
# [2, 2]