#!usr/bin/env python3
# coding=utf-8
import os
import fnmatch
import hashlib
CHUNK_SIZE = 1024

def is_file_match(filename, patterns):
    for pattern in patterns:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False


def find_specific_files(root, patterns=['*'], exclude_dirs=[]):
    for root, dirnames, filenames in os.walk(root):
        for d in exclude_dirs:
            if d in dirnames:
                dirnames.remove(d)

        for filename in filenames:
            if is_file_match(filename, patterns):
                yield os.path.join(root, filename)


def get_chunk(filename):
    with open(filename) as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            else:
                yield chunk


def get_file_checksum(filename):
    h = hashlib.md5()
    for chunk in get_chunk(filename):
        h.update(str(chunk).encode('utf-8'))
    return h.hexdigest()


if __name__ == '__main__':
    # find all files under current dir
    # for item in find_specific_files('.'):
        # print(item)
    # find all pictures
    # patterns = ['*.jpg', '*.jpeg', '*.png', '*.tif']
    # for item in find_specific_files('.', patterns):
    #     print(item)

    # exclude dirs
    patterns = ['*.jpg', '*.jpeg', '*.png', '*.tif']
    exclude_dirs = ['send_email']
    for item in find_specific_files('.', patterns, exclude_dirs):
        print(item)
    # find the top 10 files, or getmtime()
    print('find the top 10 most biggest size files')
    files = {name: os.path.getsize(name) for name in find_specific_files('.', patterns=['*.py'])}
    result = sorted(files.items(), key=lambda d: d[1], reverse=True)[:10]
    for i, t in enumerate(result, 1):
        print(i, t[0], t[1])

    # find duplicate file with hashlib md5
    # you must copy test to subdir sub/test12,otherwise they are different files
    print('This is to find duplicate files')
    record = {}
    for item in find_specific_files('./ssh_pexpect_pxssh'):
        checksum = get_file_checksum(item)
        if checksum in record:
            print('find duplicate file:{0} vs {1}'.format(record[checksum], item))
        else:
            record[checksum] = item

    # get_file_checksum('./send_email/ltaf_email.html')





