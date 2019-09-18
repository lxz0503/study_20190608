# https://www.cnblogs.com/ailiailan/p/8729544.html
# json.loads()解码python json格式,参数是json格式的字符串
# json.load()加载python json格式文件,参数是一个文件句柄

import json
class OperateJson(object):
    def __init__(self, file_path=None):
        if file_path == None:
            self.file_path = 'data.json'
        else:
            self.file_path = file_path
        self.data = self.read_data()

    # 读取json文件
    def read_data(self):
        with open(self.file_path) as fp:
            res = json.load(fp)
            return res

    # 根据关键字获取数据
    def get_data(self, index):
        # print(type(self.data))
        return self.data[index]

    # 写json
    def write_data(self, data):
        with open('xiaozhan.json', 'w') as fp:
            fp.write(json.dumps(data))


if __name__ == '__main__':
    data = {                     # 定义一个字典
        'no': 1,
        'name': 'Runoob',
        'url': 'http://www.runoob.com'
         }
    op_json = OperateJson()
    op_json.write_data(data)
    print(op_json.get_data('name'))