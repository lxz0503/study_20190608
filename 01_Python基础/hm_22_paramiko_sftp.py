# 用paramiko模块实现sftp上传下载文件功能
#!/usr/bin/env python
# coding:utf8

import paramiko

def func_sftp(put, get, local_path, remote_path):
    # 实例化transport对象，并建立连接
    transport = paramiko.Transport(('172.16.32.129', 22))
    transport.connect(username='root', password='123.com')
    # 实例化sftp对象，指定连接对象
    sftp = paramiko.SFTPClient.from_transport(transport)
    # 上传文件
    if put is not None:
        sftp.put(localpath=local_path, remotepath=remote_path)
    # 下载文件
    if get is not None:
        sftp.get(remotepath=remote_path, localpath=local_path)
    # 关闭连接
    transport.close()

if __name__ == '__main__':
    local_path = input("the local path is:").strip()
    remote_path = input("the remote path is:").strip()
    put = 1     # if you want to put, just set is as 1
    get = None  # if you want to get, just set is as 1
    func_sftp(put, get, local_path, remote_path)