# 统计一个字符串中大写字母，小写字母，数字，其他字符的个数，以字典形式返回

def statistic_string(ostr):
    """
    统计字符串中大写的字母、小写的字母、数字及其他字符的个数，以字典形式返回
    """
    uppers = 0
    lowers = 0
    digits = 0
    others = 0
    odict = {}

    for istr in ostr:
        if istr.isupper():
            uppers += 1
        elif istr.islower():
            lowers += 1
        elif istr.isdigit():
            digits += 1
        else:
            others += 1
    else:
        odict.setdefault('uppers', uppers)
        odict.setdefault('lowers', lowers)
        odict.setdefault('digits', digits)
        odict.setdefault('others', others)
    return odict


if __name__ == '__main__':
    astr = input(u'请输入一个字符串：')
    res = statistic_string(astr)
    print(res)
# 请输入一个字符串：abcdAHDJK1234*&^%
# {'uppers': 5, 'lowers': 4, 'digits': 4, 'others': 4}
