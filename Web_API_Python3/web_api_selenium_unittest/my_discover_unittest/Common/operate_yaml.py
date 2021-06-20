# https://www.cnblogs.com/keyou1/p/11510975.html
import yaml
import os

project_path = os.path.split(os.path.realpath(__file__))[0].split('Common')[0]    # D:\xiaozhan_git\python3_auto\
print(project_path)    # tuple ('D:\\xiaozhan_git\\python3_auto\\tools', 'get_project_path.py')
# log path
config_path = os.path.join(project_path, 'Test_Data', 'config_yaml')

f = open(config_path)
y = yaml.load_all(f, Loader=yaml.FullLoader)          # return a generator
# print(next(y))
for data in y:
    print(data)
f.close()
# {'name': 'James', 'age': 20}
# {'name': 'Lily', 'age': 19}

###
config_path = os.path.join(project_path, 'Test_Data', 'config_email')
f = open(config_path)
y = yaml.load(f, Loader=yaml.FullLoader)          # return a generator
# for data in y:
#     # print(data)              # only return key value: EMAIL DB
#     print(y[data])          # smtp_server:qq.smtp.com smtp_sender:123@qq.com msg_tile:this is a testB
print(y)
print(y['DB']['host'])
f.close()