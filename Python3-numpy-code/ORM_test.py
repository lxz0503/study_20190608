#!/usr/bin/env python3
# encoding=utf-8

from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# 创建对象的基类
Base = declarative_base()
# 定义Product对象
class Product(Base):
    # 数据库里表的名字
    __tablename__ = 'attraction'     # 要在数据库里先创建这个表
    # 表的结构
    ID = Column(String(20), primary_key=True)
    name = Column(String(20))
    type = Column(String(20))

# 定义Product对象
class Address(Base):
    # 数据库里表的名字
    __tablename__ = 'city'     # 要在数据库里先创建这个表
    # 表的结构
    ID = Column(String(20), primary_key=True)
    name = Column(String(20))
    type = Column(String(20))

# 初始化数据库连接
engine = create_engine('mysql+pymysql://root:123win@localhost:3306/tour')    # 先创建这个数据库
# 创建DBSession类型
DBSession = sessionmaker(bind=engine)
# 向数据库中添加记录
session = DBSession()
# 创建新Product对象，即创建新的数据库记录内容
# new_user = Product(ID='1', name='北京自由行', type='景+酒')
# 添加到session
# session.add(new_user)
user_list = [
    Product(ID='1', name='北京自由行', type='景+酒'),
    Product(ID='2', name='香山一日游', type='本地游'),
    Product(ID='3', name='门头沟一日游', type='本地游')
]
# session.add_all(user_list)
# # 数据库里另外一张表
# city_list = [
#     Address(ID='1', name='北京', type='首都'),
#     Address(ID='2', name='天津', type='直辖市'),
#     Address(ID='3', name='上海', type='魔都')
# ]
# session.add_all(city_list)
# session.commit()
# 查询数据
t_attr = session.query(Product).filter(Product.ID == '1').all()   # 取一个用one()
# 打印对象的name,type
for item in t_attr:
    print('name:', item.name)
    print('type:', item.type)
#
city_attr = session.query(Address).all()
# 打印对象的name,type
for item in city_attr:
    print('name:', item.name)
    print('type:', item.type)

# 更新数据
session.query(Product).filter(Product.ID == '1').update({Product.name:'顺义一日游'})
session.commit()
# 删除数据
# session.query(Product).filter(Product.ID == '1').delete()
# session.commit()
session.close()
