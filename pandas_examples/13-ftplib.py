import logging
from ftplib import FTP


class MyFtp():
    def __init__(self):
        self.ftp_client = FTP()

    # 些函数实现ftp登录
    def ftp_login(self,host_ip,username,password):
        try:
            self.ftp_client.connect(host_ip,port=21,timeout=10)
        except Exception as e:
            logging.warning('network connect time out')
            return 1001
        try:
            self.ftp_client.login(user=username, passwd=password)
        except Exception as e:
            logging.warning('username or password error')
            return 1002
        return 1000

    # 此函数执行ftp命令，并打印命令执行结果
    def execute_some_command(self):
        # 通运sendcmd方法形式执行pwd命令，为使用形式统一起见不推荐使用此种形式，而且其实大多数命令都是支持这种形式的
        command_result = self.ftp_client.sendcmd('pwd')
        logging.warning('command_result:%s'% command_result)
        # 通过直接使用pwd方法执行pwd命令，推荐统一使用此种形式
        command_result = self.ftp_client.pwd()
        logging.warning('command_result:%s' % command_result)
        # 上传文件；'stor ftp_client.py'告诉服务端将上传的文件保存为ftp_client.py，open()是以二进制读方式打开本地要上传的文件
        command_result = self.ftp_client.storbinary('stor ftp_client.py',open("ftp_client.py",'rb'))
        logging.warning('command_result:%s' % command_result)
        # 下载文件；'retr .bash_profile'告诉服务端要下载服务端当前目录下的.bash_profile文件，open()是以二进制写方式打开本地要存成的文件
        command_result = self.ftp_client.retrbinary('retr .bash_profile', open('local_bash_profile', 'wb').write)
        logging.warning('command_result:%s' % command_result)

    # 此函数实现退出ftp会话
    def ftp_logout(self):
        logging.warning('now will disconnect with server')
        self.ftp_client.close()

if __name__ == '__main__':
    # 要连接的主机ip
    host_ip = '192.68.220.128'
    # 用户名
    username = 'ls'
    # 密码
    password = 'abcd1234'
    # 实例化
    my_ftp = MyFtp()
    # 如果登录成功则执行命令，然后退出
    if my_ftp.ftp_login(host_ip,username,password) == 1000:
        logging.warning('login success , now will execute some command')
        my_ftp.execute_some_command()
        my_ftp.ftp_logout()