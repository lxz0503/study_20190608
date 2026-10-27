#!/usr/bin/env python3
# coding=utf-8
# https://www.cnblogs.com/zhangxinqi/p/8372774.html
import configparser
import paramiko
import time


class ParamikoClient(object):
    def __init__(self, ini_file):
        self.config = configparser.ConfigParser()
        self.config.read(ini_file)
        self.host = self.config.get('ssh', 'host')
        self.port = self.config.get('ssh', 'port')
        self.user = self.config.get('ssh', 'user')
        self.pwd = self.config.get('ssh', 'pwd')
        self.timeout = self.config.get('ssh', 'timeout')
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.log_file = "ssh_record.Logs"

    def run_ssh(self, cmd_command):
        try:
            self.client.connect(hostname=self.host,
                                port=self.port,
                                username=self.user,
                                password=self.pwd,
                                timeout=float(self.timeout))
            stdin, stdout, stderr = self.client.exec_command(cmd_command)
        except paramiko.AuthenticationException:
            print("Authentication failed, please verify your credentials")
        except paramiko.SSHException as sshException:
            print("Unable to establish SSH connection: %s" % sshException)
        except paramiko.BadHostKeyException as badHostKeyException:
            print("Unable to verify server's host key: %s" % badHostKeyException)
        else:
            pass
            #result = stdout.read().decode('utf-8')
            #print('result is:', result)
            # with open(self.log_file, 'a+') as f:
            #     f.write('run cmd: %s\n' % cmd_command)
            #     f.write(result)

    def sftp_put(self):
        with self.client.open_sftp() as sftp:
            sftp.put('test.Logs', 'test.Logs')
            sftp.chmod('test.Logs', 755)

    def sftp_get(self):
        with self.client.open_sftp() as sftp:
            sftp.get('test.Logs', 'test.Logs')

    def close(self):
        self.client.close()


client_cmd_29075 = ParamikoClient('/home/xli3/pytestAuto/utils/config_29075.ini')
client_cmd_29076 = ParamikoClient('/home/xli3/pytestAuto/utils/config_29076.ini')

if __name__ == '__main__':
    #client_cmd = ParamikoClient('/home/wrsadmin/tsn01/utils/config_29076.ini')
    cmd_input = 'iperf3 -s -p 10000'
    client_cmd_29075.run_ssh(cmd_input)
    time.sleep(5)
    client_cmd_29075.run_ssh('pkill iperf')
    client_cmd_29075.close()
