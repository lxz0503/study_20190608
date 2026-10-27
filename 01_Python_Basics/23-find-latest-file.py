#!/usr/bin/env python3
# coding=utf-8
import os


def find_newest_file(file_dir):
    """
    :param file_dir: the dir which you need to search
    :return: the newest file name
    """
    lists = os.listdir(file_dir)
    # lists.sort(key=lambda fn: os.path.getmtime(path_file + '\\' + fn))  # this is for windows
    lists.sort(key=lambda fn: os.path.getmtime(file_dir + '/' + fn))     # this is for linux, fn就是取自于可迭代对象lists
    print('the list of all files', lists)
    file_newest = os.path.join(file_dir, lists[-1])
    return file_newest

def find_all_files(file_dir):
    for dirpath, dirnames, filenames in os.walk(file_dir):
        for filename in filenames:
            file_name = os.path.join(dirpath, filename)
            print(os.path.split(file_name)[-1])
            # print(file_name)

if __name__ == '__main__':
    # file_newest = find_newest_file(r'F:\xiaozhan_git\study_20190608\Web_API_Python3')
    # file_newest = find_newest_file(r'/home/windriver')
    # print('the latest file is', file_newest)
    find_all_files('D:\\sql_data')