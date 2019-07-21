# 一般使用如下方式,把文件内容读取到列表，然后逐行处理
# eval() 函数用来执行一个字符串表达式，并返回表达式的值
# readline() 每次只能读取一行内容或者几个字符
file_name = "file_test"
with open(file_name, "r") as f:
    f_list = f.readlines()    # ['aaaaa\n', 'bbbbb\n', 'ccccc']
for line in f_list:
    print(line.strip("\n"))    # 去掉字符串头部和尾部的\n,然后逐行打印
print(f_list)
# 如果文件内容少，可以一次性读取
print("another kind of file operation")
file_name = "file_test"
with open(file_name, "r") as f:
    content = f.read()
print(content)   # 此时需要处理字符串文本

#
with open("test_file.txt", "r") as f:
    # content = f.read()
    for i in f:      # i 是str类型,要想处理里面的字典字符串，要用eval函数提取
        # print(type(i))
        # print(i)     # {"username": "alex4", "passwd": "123"}
        # print(eval(i))  # eval() 函数用来执行一个字符串表达式，并返回表达式的值
        print(eval(i)["username"])  # eval(i)就已经是字典类型了

