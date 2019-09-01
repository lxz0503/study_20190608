# def removeDuplicates(nums):    # 最快捷，但是创建了新的序列，占用内存
#     tmp = set(nums)
#     tmp = list(tmp)
#     return len(tmp)

def removeDuplicates(nums):
    i = 0
    while i < len(nums) - 1:        # 从第一个元素开始循环到倒数第二个元素
        if nums[i] == nums[i + 1]:  # 当前元素和下一个元素比较
            # nums.pop(i)           # 每次删除一个第一个相同的元素，然后回到while循环，从第一个元素开始再次比较
            nums.remove(nums[i])    # 每次删除一个第一个相同的元素，然后回到while循环，从第一个元素开始再次比较
        else:
            i += 1
    return len(nums)               # 返回删除重复元素后的序列长度


nums = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
res = removeDuplicates(nums)
print(res)