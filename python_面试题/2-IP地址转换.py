# 编写一个函数实现将十进制IP地址转换成点分二进制形式
# str.zfill(width)   原字符串右对齐，前面填充0
def ipint_change_bin(ip):
    ip_list = ip.split(".")
    ip_list_bin = []
    for i in ip_list:
        # print(format(int(i), 'b'))    # format()函数返回一个字符串，第一个参数必须是整数，而不能是字符串
        ip_list_bin.append((format(int(i), 'b')).zfill(8))
    new_str = ".".join(ip_list_bin)
    return new_str

def bin_to_ipint(ip):
    ip_list = ip.split(".")
    ip_list_int = []
    for i in ip_list:
        # print(type(int(i, 2)))    # 此时已经转换为整型int
        ip_list_int.append(str(int(i, 2)))   # append()函数参数必须是字符串等可迭代对象
    new_str = ".".join(ip_list_int)
    return new_str


if __name__ == "__main__":
    ip_int = "10.3.9.12"
    ip_bin = "00001010.00000011.00001001.00001100"

    # 调用函数ipint_change_bin
    res_bin = ipint_change_bin(ip_int)
    print("二进制形式的ip地址是", res_bin)  # 二进制形式的ip地址是 00001010.00000011.00001001.00001100

    # 调用函数bin_to_ipint
    res_int = bin_to_ipint(ip_bin)
    print("十进制形式的ip地址是", res_int)  # 二进制形式的ip地址是 10.3.9.12
