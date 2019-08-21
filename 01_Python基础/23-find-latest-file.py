#
import os
def find_newest_file(path_file):
    lists = os.listdir(path_file)
    # lists.sort(key=lambda fn: os.path.getmtime(path_file + '\\' + fn))  # this is for windows
    lists.sort(key=lambda fn: os.path.getmtime(path_file + '/' + fn))     # this is for linux
    print('the list of all files', lists)
    file_newest = os.path.join(path_file, lists[-1])
    return file_newest

if __name__  == '__main__':
    # file_newest = find_newest_file(r'F:\xiaozhan_git\study_20190608\API_Python')
    file_newest = find_newest_file(r'/home/windriver')
    print('the latest file is', file_newest)