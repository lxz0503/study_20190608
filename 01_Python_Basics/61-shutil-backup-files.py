#!/usr/bin/env python3
# coding=utf-8
# this is to backup files with shutil
# https://www.cnblogs.com/xiaolang666/p/12608703.html    shutil copy,move,remove,tar,untar,gzip

import os
import fnmatch
import shutil
import datetime


def archive_tgz():
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    filename = 'all_images_{0}'.format(now)   # backup file name with tar.gz
    os.chdir('send_email')  # backup all files under this dir
    shutil.make_archive(filename, 'gztar')    # generate backup.tar.gz


def unarchive_tgz():
    os.chdir('send_email')
    shutil.unpack_archive('backup.tar.gz')    # unpack files to send_email dir

def archive_file():
    shutil.make_archive("./send_email/data_bak", 'gztar', root_dir='./send_email')    # data_bak.gztar
    # base_name： 压缩包的文件名，也可以是压缩包的路径。只是文件名时，则保存至当前目录，否则保存至指定路径，
    # format： 压缩包种类，“zip”, “tar”, “bztar”，“gztar”
    #
    # root_dir： 要压缩的文件夹路径（默认当前目录）
    # ret = shutil.make_archive("data_bak", 'gztar', root_dir='/data')
    # # 将 /data下的文件打包放置 /tmp/目录
    # ret = shutil.make_archive("/tmp/data_bak", 'gztar', root_dir='/data')
    # shutil
    # 对压缩包的处理是调用ZipFile
    # 和
    # TarFile
    # 两个模块来进行的，详细：
    #
    # zipfile压缩 & 解压缩
    #
    # import zipfile
    # # 压缩
    # z = zipfile.ZipFile('laxi.zip', 'w')
    # z.write('a.log')
    # z.write('data.data')
    # z.close()
    # # 解压
    # z = zipfile.ZipFile('laxi.zip', 'r')
    # z.extractall(path='.')
    # z.close()
    # tarfile压缩 & 解压缩
    #
    # import tarfile
    # # 压缩
    # >> > t = tarfile.open('/tmp/egon.tar', 'w')
    # >> > t.add('/test1/a.py', arcname='a.bak')
    # >> > t.add('/test1/b.py', arcname='b.bak')
    # >> > t.close()
    # # 解压
    # >> > t = tarfile.open('/tmp/egon.tar', 'r')
    # >> > t.extractall('/egon')
    # >> > t.close()


if __name__ == '__main__':
    archive_file()


