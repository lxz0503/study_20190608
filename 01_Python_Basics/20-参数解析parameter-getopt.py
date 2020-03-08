# https://www.cnblogs.com/ytc6/p/9081913.html
import getopt
import sys

def parser(argv):
    try:
        options, args = getopt.getopt(argv, "hp:i:", ["help", "ip=", "port="])
    except getopt.GetoptError:
        sys.exit()
    print("options:", options)    # options 是个包含元组的列表，每个元组是分析出来的格式信息
    print("args:", args)    # args 是个列表，包含那些没有‘-’或‘--’的参数

    para_dict = {}        # 把解析出来的参数存储在字典里,后续用的话直接从字典里提取
    for name, value in options:
        if name in ("-h", "--help"):
            print("help:正确的使用方法是.......")
        if name in ("-i", "--ip"):
            print('ip 是:', value)
            # para_dict["ip"] = para_dict.get("ip", value)     # 给字典元素赋值
            para_dict["ip"] = para_dict.setdefault("ip", value)     # 给字典元素赋值
        if name in ("-p", "--port"):
            print('port 端口是:', value)
            para_dict["port"] = para_dict.get("port", value)
    print("所有解析出来的参数", para_dict)     # 所有解析出来的参数 {'ip': '10.0.0.1', 'port': '80'}
    return para_dict

if __name__ == "__main__":
    # run_cmd = "20-参数解析parameter-getopt.py -h --ip=10.0.0.1 --port=80"
    argv = sys.argv[1:]
    print(argv)        # ['-h', '-i', '10.0.0.1', '-p', '80']
    res = parser(argv)
    print(res)

# 输入参数  -h -i 10.0.0.1 -p 80,运行结果：
# options: [('-h', ''), ('-i', '10.0.0.1'), ('-p', '80')]
# args: []
# help:正确的使用方法是.......
# ip 是: 10.0.0.1
# port 端口是: 80
#######下面也是一种执行方式，用长参数格式
# D:\Python\python.exe D:/xiaozhan_git/study_20190608/01_Python_Basics/20-参数解析parameter-getopt.py -h --ip=10.0.0.1 --port=80
# options: [('-h', ''), ('--ip', '10.0.0.1'), ('--port', '80')]
# args: []
# help:正确的使用方法是.......
# ip 是: 10.0.0.1
# port 端口是: 80
# {'ip': '10.0.0.1', 'port': '80'}
