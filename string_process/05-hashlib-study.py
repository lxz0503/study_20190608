# hashlib主要提供字符加密功能，将md5和sha模块整合到了一起，支持md5,sha1, sha224, sha256, sha384, sha512等算法
# 向对象中传入字符串时，必须为编码类型。可以使用字符串前b' '的方法或使用.encode('UTF-8')的方法，使字符串变为bytes类型
# 字符可以拆分多次update,结果是一样的
#!/usr/bin/env python3

import hashlib
import time
# ######## md5 ########
string = "beyongjie"

md5 = hashlib.md5()    # 创建hashlib的md5对象
md5.update(string.encode('utf-8'))     # 注意转码
res = md5.hexdigest()    # 通过hexdigest()方法，获得md5对象的16进制md5显示
print("md5加密结果:", res)    # md5加密结果: 0e725e477851ff4076f774dc312d4748, 32位的16进制数，总共128bit

# 简单一点的写法
new_md5 = hashlib.new('md5', b'beyongjie').hexdigest()
print(new_md5)   # 0e725e477851ff4076f774dc312d4748
# 或者
new_md5 = hashlib.md5(string.encode('utf-8')).hexdigest()
print(new_md5)   # 0e725e477851ff4076f774dc312d4748
new_md5 = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()
print(new_md5)    # 每次这个值都变化


# 普通数据库存储用户信息
# +------+--------+
# |user  |password|
# +------+--------+
# |z3    | 81dc9bdb52d04dc20036dbd8313ed055|
# |l4    | 674f3c2c1a8a6f90461e8a66fb5550ba|
# |w5    | 81b073de9370ea873f548e31b8adc081|

# 上面这样做看似没问题,其实还有一个问题:有些用户太懒了,使用手机号或123456或生肖作为密码
# 这样出现什么问题呢,一些人闲着没事干,想出来了很多的常见密码进行哈希运算,
# 这样就得到了一大批的哈希值,然后将数据库的哈希值进行匹配(暴力破解),
# 这样也是能推出一部分用户的账号密码的,那这样怎么解决呢?
# 加盐(很多框架也是这么干的)
# 在程序中设置一个盐值(一般是base64随机生成的字符,连开发者自己都记不住的字符串),
# 程序拿到用户输入密码之后拼接上这个盐值再进行哈希运算,用户的密码就会很复杂,
# 那些闲着没事干的人只要拿不到盐值基本就很难推演数据库里面存储的哈希结果.实现用户登陆口令存储
#
# 作者：陆_志东
# 链接：https://www.jianshu.com/p/648fb09fb91e
# 来源：简书
# 简书著作权归作者所有，任何形式的转载都请联系作者获得授权并注明出处。
import os
password = "123456".encode("utf-8")
salt = os.urandom(32)   # 返回一个有n=32个byte那么长的一个string，然后很适合用于加密
print(salt)
# >>b'h\x02b$\xff\xea\xe7\xed\x88\xe4\xff\x8a\x11 \xf4US\xec\xb1\xc3S\xb5H[\x94\x0f\x85\x0b\xc5\x91\xd7 '
md5 = hashlib.md5()
md5.update(password+salt)   # 拼接密码和盐值
print(md5.hexdigest())    # 每次都是变化的