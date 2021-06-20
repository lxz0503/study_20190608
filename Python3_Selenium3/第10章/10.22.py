import os #操作文件夹需要导入'os'模块
print(os.getcwd()) # 打印出当前执行脚本所在目录
print(os.path.exists('/PycharmProjects/Sstone/tt.png')) #如果当前路径存在则返回"True"，如果不存在则返回"False"
print(os.path.isfile('/PycharmProjects/Sstone/tt.png')) #判断当前路径是否是一个文件，如果是，则返回"True"
#os.remove('/PycharmProjects/Sstone/tt.png') #删除一个文件
os.removedirs('/PycharmProjects/Sstone/')  #可以删除多级目录
os.mkdir("test1221") #在当前目录下创建'test1221' 单个文件夹
os.makedirs('/PycharmProjects/Sstone/1/2/3') #可以创建多级目录
