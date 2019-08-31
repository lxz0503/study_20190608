# 判断一个整数是否是回文数
# Determine whether an integer is a palindrome. An integer is a palindrome when it reads the same backward as forward.
#
# Example 1:
#
# Input: 121
# Output: true
# Example 2:
#
# Input: -121
# Output: false
# Explanation: From left to right, it reads -121. From right to left, it becomes 121-. Therefore it is not a palindrome.
# Example 3:
#
# Input: 10
# Output: false
# Explanation: Reads 01 from right to left. Therefore it is not a palindrome.

def isPalindrome(x):
    if x >= 0:
        int_str = str(x)
        if int_str == int_str[::-1]:  # 逆序输出
            print('%s is a palindrome number' % x)
            return True
        else:
            print('%s is not a palindrome number' % x)
            return False
    else:
        print('%s is not a palindrome number' % x)
        return False

isPalindrome(121)
isPalindrome(10)
isPalindrome(-99)
