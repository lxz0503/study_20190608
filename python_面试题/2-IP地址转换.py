# 编写一个函数实现将十进制IP地址转换成点分二进制形式
# str.zfill(width)   原字符串右对齐，前面填充0
def ip_change_bin(ip):
    ip_list = ip.split(".")
    ip_list_bin = []
    for i in ip_list:
        # print(format(int(i), 'b'))    # format()函数第一个参数必须是整数，而不能是字符串
        ip_list_bin.append((format(int(i), 'b')).zfill(8))
    new_str = ".".join(ip_list_bin)
    return new_str


if __name__ == "__main__":
    ip = "10.3.9.12"
    res = ip_change_bin(ip)
    print("二进制形式的ip地址是", res)  # 二进制形式的ip地址是 00001010.00000011.00001001.00001100

