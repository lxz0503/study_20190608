# 封装ssh类, 用paramiko模块来实现ssh操作
#!/usr/bin/env python
import configparser
import paramiko

class ParamikoClient(object):
    def __init__(self,ini_file):    # 只需要从外界传进来一个参数
        self.config=configparser.ConfigParser()
        self.config.read(ini_file)
        self.host = self.config.get('ssh', 'host')
        self.port = self.config.get('ssh', 'port')
        self.user = self.config.get('ssh', 'user')
        self.pwd = self.config.get('ssh', 'pwd')
        self.timeout = self.config.get('ssh', 'timeout')
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.host,
                            port=self.port,
                            username=self.user,
                            password=self.pwd,
                            timeout=float(self.timeout))

    def run_ssh(self, cmd_command):
        # 执行命令，输出结果在stdout中，如果是错误则放在stderr中
        stdin, stdout, stderr = self.client.exec_command(cmd_command)
        result = stdout.read()       # read方法读取输出结果
        if len(result) == 0:         # 判断如果输出结果长度等于0,表示为错误输出
            print(stderr.read().decode())
        else:
            print(str(result, 'utf-8'))      # 将二进制机器码码流转化为字符串

    def close(self):
        self.client.close()

if __name__ == '__main__':
    client_cmd = ParamikoClient('config.ini')
    while True:
        cmd_input = input('>>>:')
        if cmd_input == 'quit':
            client_cmd.close()
        client_cmd.run_ssh(cmd_input)

