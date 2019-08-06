# https://www.cnblogs.com/ytc6/p/9081913.html
#!/usr/bin/env python
import getopt
import sys

def parser(argv):
    try:
        options, args = getopt.getopt(argv, "hp:i:", ["help", "ip=", "port="])
    except getopt.GetoptError:
        sys.exit()
    print("options:", options)    # 
    print("args:", args)    # 

    para_dict = {}        #
    for name, value in options:
        if name in ("-h", "--help"):
            print("help:.......")
        if name in ("-i", "--ip"):
            print('ip :', value)
            # para_dict["ip"] = para_dict.get("ip", value)     # 
            para_dict["ip"] = para_dict.setdefault("ip", value)     # 
        if name in ("-p", "--port"):
            print('port :', value)
            para_dict["port"] = para_dict.get("port", value)
    print("all parameters are", para_dict)     
    return para_dict

if __name__ == "__main__":
    argv = sys.argv[1:]
    print(argv)        # ['-h', '-i', '10.0.0.1', '-p', '80']
    res = parser(argv)
    print(res)

