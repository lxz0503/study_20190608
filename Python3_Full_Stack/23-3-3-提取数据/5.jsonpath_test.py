#coding:utf-8
import jsonpath


data = {"key1":{"key2":{"key3":{"key4":{"key5":{"key6":{"key7":{"key8":"python21"}}}}}}}}

print(data["key1"]["key2"]["key3"]["key4"]["key5"]["key6"]["key7"]["key8"])

# jsonpath的结果是一个列表
print(jsonpath.jsonpath(data, '$.key1.key2.key3.key4.key5.key6.key7.key8'))
print(jsonpath.jsonpath(data, '$..key8'))