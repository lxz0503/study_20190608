
# 字节转化为字符串用下面的两种都可以
import sys
print('目前系统的编码为：', sys.getdefaultencoding())

print(str(b'example', encoding='utf-8'))    # example
print(bytes.decode(b'example'))

# 字符串转化为字节,用下面两种方法都可以
print(bytes('example', encoding='utf-8'))     # b'example'
print(str.encode('example'))                  # b'example'

import subprocess

# 最常见的用法如下,获取某个系统命令的输出
ret = subprocess.getoutput('ls -l')
print(ret)

retcode, output = subprocess.getstatusoutput('ls -l /test')
print(retcode)       # 2
print(output)        # ls: 无法访问/test: 没有那个文件或目录


# 复杂用法，执行复杂命令
def run_cmd(command):
    # ret = subprocess.Popen(bytes(command, encoding='utf-8').decode('utf-8'),   # 转化为字符串参数
    # ret = subprocess.Popen(str.encode(command).decode('utf-8'),   # 转化为字符串参数
    ret = subprocess.Popen(command,   # command是字符串类型参数
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    output = ret.stdout.read() + ret.stdout.read()
    return str(output, encoding='GBK')    # 家里win7系统执行结果


result = run_cmd("dir")     # 传入的参数是一个字符串,shell 命令可以分号分割传入 uname -a;echo 'hello'
print("命令执行结果是",  result)

# result = run_cmd("uname -a;echo 'hello'")