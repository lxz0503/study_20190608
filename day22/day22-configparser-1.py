# ConfigParser 是用来读取配置文件的包。
# 配置文件的格式如下：中括号“[ ]”内包含的为section。section 下面为类似于key-value 的配置内容。
# [db]
# db_host = 127.0.0.1
# db_port = 69
# db_user = root
# db_pass = root
# host_port = 69
#
# [concurrent]
# thread = 10
# processor = 20

import configparser

config = configparser.ConfigParser()
config.read("test.ini")
# 获取所用的section节点
sections = config.sections()
print(sections)    # 列表['db', 'concurrent', 'test_result']

#　获取指定section 的options。即将配置文件某个section 内key 读取到列表中

r = config.options("db")
print(r)    # 列表['db_host', 'db_port', 'db_user', 'db_pass', 'host_port']

#
r = config.get("db", "db_host")
# r1 = config.getint("db", "k1")    #将获取到值转换为int型
# r2 = config.getboolean("db", "k2" )    #将获取到值转换为bool型
# r3 = config.getfloat("db", "k3" )    #将获取到值转换为浮点型
print(r)     # 127.0.0.1

# 获取某个section下面的配置信息，每个元素都是键值对，放在列表里
# [('db_host', '127.0.0.1'), ('db_port', '69'), ('db_user', 'root'), ('db_pass', 'root'), ('host_port', '69')]
r = config.items("db")
print(r)    # [('db_host', '127.0.0.1'), ('db_port', '69'), ('db_user', 'root'), ('db_pass', 'root'), ('host_port', '69')]

# 修改某个option的值，如果不存在则会出创建
config.set("db", "db_port", "69")  # 修改db_port的值为69,也可以提前设置一个变量
config.write(open("test.ini", "w"))

# 检查section或option是否存在，bool值

config.has_section("section") # 是否存在该section
config.has_option("section", "option")  # 是否存在该option

# 添加section 和 option
if not config.has_section("default"):  # 检查是否存在section
    config.add_section("default")
if not config.has_option("default", "db_host"):  # 检查是否存在该option
    config.set("default", "db_host", "1.1.1.1")
config.write(open("test.ini", "w"))

#
config.remove_section("default")  # 整个section下的所有内容都将删除
config.write(open("test.ini", "w"))