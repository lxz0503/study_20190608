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
    """search student information"""
    filename = 'students.txt'
    mark = True
    student_query = []
    student_id = ''
    student_name = ''
    while mark:
        mode = input('按ID查询输入1；按姓名查询输入2：')
        if mode == '1':
            student_id = input('请输入要搜索的学生ID：')
        elif mode == '2':
            student_name = input('请输入要查询的学生名字：')
        else:
            print('输入有误，重新输入')
            search()

        with open(filename, 'r') as r:
            all_info = r.readlines()
            for student in all_info:
                d = eval(student)  # change string to dict
                if d['id'] == student_id:
                    student_query.append(d)
                    break
                elif d['name'] == student_name:
                    student_query.append(d)
                    break
            else:   # this is paired with for loop
                print('not find this ID %s or name %s' % (student_id, student_name))
            # show query info
            print('search list is:')
            for i in student_query:
                print(i)
            # show query info with format
            show_student(student_query)
            student_query.clear()
            input_mark = input('是否继续搜索？（y/n):')
            if input_mark == 'y':
                mark = True
            else:
                mark = False
                break

def show_student(student_query):
    format_title = '{:^6}{:^12}\t{:^8}\t{:^10}\t{:^10}\t{:^10}'
    print(format_title.format('ID', 'name', 'english', 'python', 'c', 'sum'))
    format_data = '{:^6}{:^12}\t{:^12}\t{:<8}\t{:<8}\t{:^8}'
    for info in student_query:
        print(format_data.format(info.get('id'), info.get('name'),
                                 str(info.get('english')), str(info.get('python')), str(info.get('c')),
                                 str(info.get('english') + info.get('python') + info.get('c')).center(12)
                                 ))

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

            if len(student_old) >= 1:
                with open(filename, 'w') as w:
                    for student in student_old:
                        d = eval(student)  # change string to dict
                        if d['id'] != student_id:  # record students that do not need to delete
                            w.write(student)
                        else:
                            print('ID %s is deleted successfully' % student_id)
                            break
                    else:
                        print('not find this ID %s' % student_id)
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
    """modify student information"""
    filename = 'students.txt'
    mark = True
    id_list = []
    while mark:
        with open(filename, 'r') as r:
            student_old = r.readlines()  # read student information into a list
            for student in student_old:
                id_list.append(eval(student).get('id'))
            print('id list is %s' % id_list)

        student_id = input('请输入要修改的学生ID：')  # 如果输错了，不知道怎么处理，目前代码仅支持正确输入
        with open(filename, 'w') as w:
            for student in student_old:
                d = eval(student)  # change string to dict
                if d['id'] == student_id:
                    print('find this ID and modify it')
                    try:
                        d['name'] = input('输入新的名字：')
                        d['english'] = input('输入english成绩:')
                        d['python'] = input('输入python成绩：')
                        d['c'] = input('输入c语言成绩:')
                    except:
                        print('输入有误，重新输入')
                    # write modified information
                    student = str(d)
                    w.write(student + '\n')       # 写入字符串，要有换行符\n
                    print('ID %s is already modified' % student_id)
                else:
                    w.write(student)      # 原来的字符串里面包含了换行符，所以不用再加\n
        # show()
        input_mark = input('是否继续修改？（y/n):')
        if input_mark == 'y':
            mark = True
        else:
            mark = False
            break


def sort():
    """sort"""
    filename = 'students.txt'
    new_list = []
    with open(filename, 'r') as r:
        all_info = r.readlines()    # read into a list
    for student in all_info:
        new_list.append(eval(student))
    print(new_list)
    mode = input('请选择排序方式:(1 按英语成绩；2 按python成绩; 3 按C语言成绩；0 按总成绩)：')
    if mode == '1':
        new_list.sort(key=lambda x: x['english'], reverse=False)
    elif mode == '2':
        new_list.sort(key=lambda x: x['python'], reverse=True)
    elif mode == '3':
        new_list.sort(key=lambda x: x['c'], reverse=True)
    elif mode == '0':
        new_list.sort(key=lambda x: x['english'] + x['python'] + x['c'], reverse=True)
    else:
        print('输入有误，重新输入')
        sort()
    # after sorted
    print('after sorted by mode %s,result is:' % mode)
    show_student(new_list)


def total():
    """total student number"""
    filename = 'students.txt'
    with open(filename, 'r') as r:
        all_info = r.readlines()
    print('total student number is %s' % len(all_info))


def show():
    filename = 'students.txt'
    with open(filename, 'r') as r:
        for student in r:
            print(eval(student))
