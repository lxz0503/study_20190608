#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:2/21/2024 5:37 PM
@file:xiaozhan.py
"""
import yaml


def readYaml(yamlFile, key=''):
    with open(yamlFile) as fd:
        cfg = yaml.safe_load(fd)
    if key == '':
        return cfg
    else:
        return cfg[key]


def verify_buf_does_not_exist():
    ret = 5
    if 1 == 1:
        assert False
    return ret


def get_ip():
    ip = '192.168.123.10/24'  # a.b.c.d/24  self.config['ip']
    ip6 = '2000::10/64'  # 2000::a/64  self.config['ip6']
    return ip.split('/')[0], ip6.split('/')[0]


class NetworkInterface(object):
    def __init__(self, session, name):
        self.session = session
        self.name = name
        self.vr = 0

    def test(self):
        print(self.session, self.name)


class Ethernet(NetworkInterface):
    # def __init__(self, session, name):
    #     super().__init__(session, name)
    pass

def basic(a,b):
    a = 10
    b = 20
    def int2(a, b):
        print(a)



if __name__ == "__main__":
    basic(10, 20)
    a = None
    if not a:
        print('none')

    rulesetlist = [[['pass', 'out', 'quick', 'on', 'n.rifs.ifname', 'all'], ['block', 'out', 'on', 'n.rifs.ifname', 'all']]]
    for rule in rulesetlist:
        print(rule[1])
    print(len(rulesetlist))
    #
    parent_eth = Ethernet('a', 'b')
    parent_eth.test()

    for vr in range(2, -1, -1):
        print('vr is', vr)

    ret = [('abc', 'pass'), ('bcd', 'fail')]
    # for i in ret:
    #     if i[1] == 'fail':
    #         log.error(f'===={i[0]}====fail\n')
    # for i in ret:
    #     assert i[1] == 'pass'

    b = 10
    a = 10 if b > 20 else 5
    print(a)

    v6 = ''
    if v6:
        print('a')

    [print(x) for x in ret]

    # debug
    test_case = 'aaa'
    commands = [
        f"./runKong.sh -m SSH -g /net/pek-vx-release6//buildarea2/Jekins/GitRepo/vx7/vx20240305221023_vx_2409 -c {test_case} testOnly",
        f"cp -r /workspace/jsong3/SSH/cvs/iptestengine/src/log/ /net/pek-vx-release7//buildarea1/user/jsong3/KONG/{test_case}/",
        f"cd /net/pek-vx-release7//buildarea1/user/jsong3/KONG/{test_case}/",
        "pwd",
        "ls -1t | head -n 1"  # 获取最新的文件名
    ]

    for i in commands:
        print(i)

    # vipCreateCmd = ''
    # cfg = readYaml('vxBuildConfigFTP.yaml', key='FTP')
    # print(cfg)
    # if 'vxparam' in cfg['vip']:
    #     for c in cfg['vip']['vxparam']:
    #         vipCreateCmd += ' -p ' + c
    # print(vipCreateCmd)
    # vxprj = 'vxprj parameter setstring LOGIN_BANNER_TEXT "Login Banner #1"'

    # def record_result_expect(result, ret, case_name):
    #     if ret == 'PASS':
    #         result.append((case_name, 'PASS'))
    #     else:
    #         result.append((case_name, 'FAIL'))
    #         assert False

    result = [
        ('a', 'FAIL'),
        ('socktest.tcp.c0010socket.socket_invalid_domain-IPv4', 'PASS'),
        ('socktest.tcp.c0010socket.socket_unspecified_domain-IPv4', 'PASS'),
        ('socktest', 'PASS'),
        ('a', 'PASS')
    ]
    pass_num = fail_num = 0
    for i in range(len(result)):
        if result[i][1] == 'PASS':
            pass_num += 1
        elif result[i][1] == 'FAIL':  # result[i][0]
            print('------', result[i][0])
            res = []
            res += result[i + 1:]
            # print(res)
            for j in range(len(res)):
                print(res[j][0])
                if result[i][0] == res[j][0]:
                    fail_num += 1
    print(pass_num + fail_num, pass_num, fail_num)


    #
    def cmd_transfer(passive, extended, v6=False):
        if v6 and extended == 0:
            print('return')


    v6 = True
    for p in (0, 1):
        for e in (0, 2):
            cmd_transfer(p, e, v6)

    #
    import re

    line = '227 Entering passive mode (192,168,123,20,240,253)'
    portobj = re.match(r'227 Entering passive mode \([0-9]+,[0-9]+,[0-9]+,[0-9]+,([0-9]+),([0-9]+)\)', line)
    portno = 256 * int(portobj.groups()[0]) + int(portobj.groups()[1])  # portobj.groups()表示匹配所有字符，返回一个列表
    print(portobj.groups()[0])
    print(portobj.groups()[1])
    print(portno)

    # ftp suite ---正则匹配FTP 测试--替换原来的代码
    with open('ftp.txt', 'r') as f1, open('ftp1.txt', 'w') as f2:
        for line in f1:
            if 'sendAndReturnAll' not in line:
                f2.write(line)
            else:
                # lines = ftpc.sendAndReturnAll('quote XFTP creat fil_1 ' + str(size))
                ret = re.findall(r'ftpc.sendAndReturnAll\((.*)\)', line)
                # print('lines = ftpc.sendAndReturnAll(' + ret[0] + ', prompt)')
                f2.write('lines = ftpc.sendAndReturnAll(' + ret[0] + ', prompt)\n')

    #
    lines = ['Current client directory is ""']
    pos = lines[0].find('Current client directory is "')
    print(pos)

    # try:
    #     # 1/0
    #     # assert 1 == 2
    #     assert False
    # except:
    #     print('assert False')
    # else:
    #     print('True')
    # finally:
    #     print('finally')

    # res = verify_buf_does_not_exist()
    # print('return value', res)

print(get_ip())
ntpc2_ip = '1.1.1.1'
cmd = f'sysvar set -co ipntp.config.param "server {ntpc2_ip}; disable auth;logfile ntp.log"'
print(cmd)
