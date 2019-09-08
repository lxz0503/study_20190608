
import yaml
f = open(r'D:\xiaozhan_git\study_20190608\API_Python\web_api_selenium_unittest\my_discover_unittest\Test_Data\config_yaml')
y = yaml.load_all(f, Loader=yaml.FullLoader)          # return a generator
# print(next(y))
for data in y:
    print(data)
f.close()
# {'name': 'James', 'age': 20}
# {'name': 'Lily', 'age': 19}

###
f = open(r'D:\xiaozhan_git\study_20190608\API_Python\web_api_selenium_unittest\my_discover_unittest\Test_Data\config_email')
y = yaml.load(f, Loader=yaml.FullLoader)          # return a generator
# for data in y:
#     # print(data)              # only return key value: EMAIL DB
#     print(y[data])          # smtp_server:qq.smtp.com smtp_sender:123@qq.com msg_tile:this is a testB
print(y)
print(y['DB']['host'])
f.close()