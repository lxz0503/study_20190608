"""
wget?linux???????????
????:
windriver@PEK-QCAO1-D2:~/get_resutl_html_send_email$ python3 test_wget.py
cmd %s wget -O test.html https://www.centos.bz/2016/10/download-compile-install-nginx/
std_out : b"--2019-08-21 16:13:08--  https://www.centos.bz/2016/10/download-compile-install-nginx/\nResolving www.centos.bz (www.c             entos.bz)... 112.74.125.108\nConnecting to www.centos.bz (www.centos.bz)|112.74.125.108|:443... connected.\nHTTP request sent, awa             iting response... 200 OK\nLength: unspecified [text/html]\nSaving to: `test.html'\n\n     0K .......... .......... ......                                         140M=0s\n\n2019-08-21 16:13:09 (140 MB/s) - `test.html' saved [27123]\n\n"

"""

import os
import subprocess

def run_shell_cmd(cmd):
    print('cmd %s', cmd)
    p = subprocess.Popen(cmd,bufsize=1,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    std_out, std_err = p.communicate()
    print('std_out : %s' % std_out)
    return (p.returncode, std_out)

def get_test_result_from_html(saved_result_html_link, result_html_link):
    cmd = 'wget -O %s %s' % (saved_result_html_link, result_html_link)
    run_shell_cmd(cmd)
    f = open(saved_result_html_link, 'r')
    content = f.readlines()
    for line in content:
        print(line)
    f.close()

if __name__ == '__main__':
    index = 'download-compile-install-nginx'
    result_html_link = 'https://www.centos.bz/2016/10/%s/' % index
    saved_result_html_link = 'test.html'
    get_test_result_from_html(saved_result_html_link, result_html_link)
