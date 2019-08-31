# 找到数组中两个数之和等于目标值对应的元素，放到集合中,或者输出下标
def two_sum(numbers, target):
    res = []
    for i in range(len(numbers) - 1):          # 循环到倒数第二位
        for j in range(i + 1, len(numbers)):     # 从i往后开始循环
            if (numbers[i] + numbers[j]) == target:
                res.append((numbers[i], numbers[j]))    # [(1, 4), (2, 3)]，返回的元素值
                # res.append((i, j))        # [(0, 3), (1, 2)] 返回的是下标
    return res

# function call
res = two_sum([1,2,3,4], 5)
print(res)