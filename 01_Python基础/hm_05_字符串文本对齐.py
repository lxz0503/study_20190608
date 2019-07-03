s = "hello hello beijing "
print("子串llo出现了%d次" % (s.count("llo")))
if s.startswith("h"):
    print("yes")
if s.endswith("o"):
    print("end with o")
print(s.find("e"))
new_s = s.replace("he", "aaa")
print(new_s)
print(s.partition("o"))  # 把字符串拆分成一个3元素的元祖
print(s.split(" "))    # 以空格拆分成为一个列表
l = ["aa", "bb", "cc"]
print("*".join(l))
print(s[0::2])  # 获取0，2，4，6，8
# 通过切片获取到字符串的逆序,把步长指定为-1即可,-1下标代表最后一个元素
# Sequence[start:end:step] python 的序列切片中，
# 第一个:隔离了 起始索引 和 结束索引，第二个:隔离了 结束索引 和 步长

# step为正，则从左到右切片，如果 start > end，则为空
# step为负，则从右到左切片，如果 start < end，则为空
# start 和 end 填空，前者表示最开始，后者表示最后一个, 同时为空的时候，表示取所有。至于方向，取决于step
# 可以总结一句规律，step 为正表示从左到右切片，反之为右到左。然后根据index 依次切片
num_str = "0123456789"
print(num_str[::-1])
