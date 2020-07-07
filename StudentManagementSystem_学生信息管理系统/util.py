#!/usr/bin/env python3
# coding=utf-8
import os

def menu():
    print(''' 
         ------------------学生信息管理系统---------------
         |   ===========功能菜单===========             a
         |     1 录入学生信息                           a                          
         |     2 查找学生信息                           a
         |     3 删除学生信息                           |
         |     4 修改学生信息                           |
         |     5 排序                                  |
         |     6 统计学生总人数                         |
         |     7 显示所有学生信息                       a   
         |     0 退出系统                              |
         ----------------------------------------------
    ''')


def record(students_list, filename):
    """Record students' information"""
    try:
        f = open(filename, 'a')
    except Exception as e:
        f = open(filename, 'w')
    for line in students_list:
        f.write(str(line) + '\n')     # dict must be changed to string
    f.close()


def insert():
    """Insert students' information"""
    students_list = []
    record_file = 'students.txt'
    mark = True    # 是否继续添加
    while mark:
        id = input('请输入ID（like 1001）:')
        if not id:
            break
        name = input('请输入名字：')
        if not name:
            break
        try:
            english = int(input('请输入英语成绩：'))
            python = int(input('请输入python成绩：'))
            c = int(input('请输入c语言成绩：'))
        except:
            print('输入无效，不是整形数值，请重新输入')
            continue
        #
        student = {'id': id, 'name': name, 'english': english, 'python': python, 'c': c}
        students_list.append(student)
        #
        input_mark = input('是否继续添加学生信息？（y/n）:')
        if input_mark == 'y':
            mark = True
        else:
            mark = False
    record(students_list, record_file)
    print('学生信息录入完毕！')


def search():
    pass

def delete():
    """delete student information"""
    filename = 'students.txt'
    mark = True
    while mark:
        student_id = input('请输入要删除的学生ID：')
        if student_id is not '':
            try:
                with open(filename, 'r') as r:
                    student_old = r.readlines()   # read into a list
            except:
                return

            ifdel = False
            if len(student_old) >= 1:
                with open(filename, 'w') as w:
                    d = {}
                    for line in student_old:
                        d = eval(line)  # change string to dict
                        if d['id'] != student_id:  # record students that do not need to delete
                            w.write(str(d) + '\n')
                        else:
                            ifdel = True
                    if ifdel:
                        print('ID %s is already deleted' % student_id)
                    else:
                        print('can not find ID %s' % student_id)
            else:
                print('no record for this id %s' % student_id)
            # show()
            input_mark = input('是否继续删除？（y/n):')
            if input_mark == 'y':
                mark = True
            else:
                mark = False
                break
        else:
            print('重新输入有效的ID：')

def modify():
    # show()
    filename = 'students.txt'
    if os.path.exists(filename):
        with open(filename, 'r') as r:
            student_old = r.readlines()
    else:
        return
    student_id = input('请输入要修改的学生ID：')
    with open(filename, 'w') as w:
        for student in student_old:
            d = eval(student)
            if d['id'] == student_id:
                print('find this ID and modify it')
                try:
                    d['name'] = input('输入新的名字：')
                    d['english'] = input('输入english成绩:')
                    d['python'] = input('输入python成绩：')
                    d['c'] = input('输入c语言成绩:')
                except:
                    print('输入有误，重新输入')

                student = str(d)
                w.write(student + '\n')     # 写入修改后的信息, 注意必须有换行符
                print('modify successful')
            else:
                w.write(student)    # 原始文件里面包含了换行符，所以此处不用加\n
    mark = input('是否继续修改？（y/n）:')
    if mark == 'y':
        modify()

def sort():
    pass

def total():
    pass

def show():
    pass