#!/usr/bin/env python3
# coding=utf-8
# this is to backup files with shutil

import os
import fnmatch
import shutil
import datetime


def archive_tgz():
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    filename = 'all_images_{0}'.format(now)
    os.chdir('send_email')
    shutil.make_archive(filename, 'gztar')    # generate backup.tar.gz


def unarchive_tgz():
    os.chdir('send_email')
    shutil.unpack_archive('backup.tar.gz')    # unpack files to send_email dir


if __name__ == '__main__':
    archive_tgz()


