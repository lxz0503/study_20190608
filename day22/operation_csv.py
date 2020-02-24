#!/usr/bin/env python3
# coding=utf-8
import csv
class OperaCsv(object):
    def __init__(self):
        # self.csv_name = csv_name
        pass

    def read_csv(self, csv_name):
        with open(csv_name, "r", encoding='utf-8') as f:  # 此处必须加上encoding参数
            # reader是一个迭代器
            reader = csv.reader(f)
            next(reader)  # 输出结果会去掉行头标题
            for row in reader:
                name = row[0]
                address = row[-1]
                print({"name": name, "addr": address})

    def write_csv(self, csv_name, headers, values):
        with open(csv_name, "w", encoding="utf-8", newline='') as f:    # newline换行符为空，默认为\n,
            writer = csv.writer(f)
            writer.writerow(headers)  # 写入行首标题
            writer.writerows(values)


if __name__ == '__main__':
    csv_name = 'name.csv'
    headers = ["username", "age", "addr"]
    values = {
        ("张三", 23, "满城"),
        ("李四", 24, "保定"),
        ("王五", 25, "衡水"),
        ("赵六", 26, "邯郸")
    }
    # write csv
    w = OperaCsv()
    w.write_csv(csv_name, headers, values)
    # read csv
    r = OperaCsv()
    r.read_csv(csv_name)
