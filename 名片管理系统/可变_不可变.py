a = []
print(id(a))
a.append("22")
print(id(a))
a.clear()
print(id(a))
d = {"name ": "xiaoming", "age": 18}
print(id(d))
d.pop("age")
print(id(d))
d.clear()
print(id(d))
d = {"name ": "xiaoming", "age": 18}
print(id(d))
print(hash("s"))

# 如果通过方法来修改可变类型，内存地址不会发生改变
# 如果通过赋值语句来修改可变类型，内存地址就会发生改变
