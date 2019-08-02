# 字节转化为字符串用下面的两种都可以

print(str(b'example', encoding='utf-8'))    # example
print(bytes.decode(b'example'))

# 字符串转化为字节,用下面两种方法都可以
print(bytes('example', encoding='utf-8'))     # b'example'
print(str.encode('example'))                  # b'example'

import subprocess

def run_cmd(command):
    # ret = subprocess.Popen(bytes(command, encoding='utf-8').decode('utf-8'),   # 字符串参数要转换为字节类型
    ret = subprocess.Popen(str.encode(command).decode('utf-8'),   # 字符串参数要转换为字节类型
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout = ret.stdout.read()
    stderr = ret.stderr.read()
    return str(stdout, encoding='utf-8')


result = run_cmd("dir")     # 传入的参数是一个字符串
print("命令执行结果是",  result)