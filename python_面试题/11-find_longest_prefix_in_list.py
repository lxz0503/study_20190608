# Write a function to find the longest common prefix string amongst an array of strings.
#
# If there is no common prefix, return an empty string "".
#
# Example 1:
#
# Input: ["flower","flow","flight"]
# Output: "fl"
# Example 2:
#
# Input: ["dog","racecar","car"]
# Output: ""
# Explanation: There is no common prefix among the input strings.
# Note:
#
# All given inputs are in lowercase letters a-z.

def longestCommonPrefix(strs):
    if len(strs) == 0:
        return ''
    res = ''
    strs = sorted(strs)         # ['flight', 'flow', 'flower'] 默认是升序排序
    # strs.sort()                # ['flight', 'flow', 'flower']
    # 排序后，只需要比较第一个和最后一个列表元素即可
    for i in strs[0]:        # 排序后对第一个列表元素进行循环取值
        if strs[-1].startswith(res + i):     # 对列表最后一个元素取值,判断以什么字符开头
            res += i
        else:
            break
    return res


str_list = ["flower", "flow", "flight"]
res = longestCommonPrefix(str_list)
print(res)