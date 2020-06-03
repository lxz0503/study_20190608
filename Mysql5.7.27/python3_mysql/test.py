import pymysql


# 在数据库中插入数据
def insertData(db, cursor):
    # 插入数据
    sql = """INSERT INTO student (id, name, age) VALUES
                       (1, '小明', 18),
                       (2, '小兰', 18);"""
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()

        print("successfully insert data")
    except :
        # 发生错误时回滚
        db.rollback()


# 创建mysql表
def createTable(cursor):
    # 创建students 数据库, 如果存在则删除students 数据库
    cursor.execute("drop database if exists students")
    cursor.execute("create database students")
    # 选择 students 这个数据库
    cursor.execute("use students")

    # sql中的内容为创建一个名为student的表
    sql = """CREATE TABLE IF NOT EXISTS `student` (
              `id` BIGINT,
              `name` VARCHAR (20),
              `age` INT DEFAULT 1
              )"""
    # 如果存在student这个表则删除
    cursor.execute("drop table if exists student")
    # 创建表
    cursor.execute(sql)

    print("successfully create table")


# 显示
def readTable(cursor):
    # 选择全部
    cursor.execute("select * from student")
    # 获得返回值，返回多条记录，若没有结果则返回()
    results = cursor.fetchall()

    # 遍历打印
    for row in results:
        id = row[0]
        name = row[1]
        age = row[2]
        print("id =", id, " name =", name, " age =", age, '\n')

    print("successfully show table")


# 查找
def findRecord(cursor, key, value):
    # 要执行的sql语句
    sql = "select * from student where " + key + "=" + value
    cursor.execute(sql)
    result = cursor.fetchall()

    print(result, "successfully find")


# 删除
def deleteRecord(db, cursor, key, value):
    # 要执行的sql语句
    sql = "delete from student where " + key + "=" + value
    cursor.execute(sql)
    db.commit()

    print("successfully delete")


if __name__ == '__main__':
    # 链接mysql数据库
    db = pymysql.Connect("localhost", "root", "123win", charset="utf8")
    # 创建指针
    cursor = db.cursor()

    # 创建数据库和表
    createTable(cursor)

    # 插入数据
    insertData(db, cursor)

    # 显示表格
    readTable(cursor)

    # 查找
    findRecord(cursor, "name", "'小明'")

    # 删除
    deleteRecord(db, cursor, "name", "'小明'")

    # 更改
    sql = "update student set age=20 where id=2"
    cursor.execute(sql)
    db.commit()

    readTable(cursor)

    # 关闭游标链接
    cursor.close()
    # 关闭数据库服务器连接，释放内存
    db.close()
