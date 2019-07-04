# 一般使用如下方式,把文件内容读取到列表，然后逐行处理
file_name = "file_test"
with open(file_name, "r") as f:
    f_list = f.readlines()
for line in f_list:
    print(line.strip("\n"))
print(f_list)
# 如果文件内容少，可以一次性读取
print("another kind of file operation")
file_name = "file_test"
with open(file_name, "r") as f:
    content = f.read()
print(content)   # 此时需要处理字符串文本
