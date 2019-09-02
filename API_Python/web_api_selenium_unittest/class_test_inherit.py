#!/usr/bin/env python
#encoding=UTF-8

class SchoolMember(object):
    def __init__(self,name,age,addr,hobby):
        self.name=name
        self.age=age
        self.addr=addr
        self.hobby=hobby
        print('your name is %s' % self.name)
    
    def tell(self):
        self.aaa = 10
        print('name is:%s,age is :%d,address is :%s,hobby is :%s' % (self.name,self.age,self.addr,self.hobby))
        self.d = self.aaa
        print('d is %s' % self.d)
    def tell2(self):
        self.c = self.aaa
        #return self.tell()
        print('c is %s' % self.c)
        print('aaa is %s' % self.aaa)

class Student(SchoolMember):
    def __init__(self,name,age,addr,hobby,marks):
        super(Student,self).__init__(name,age,addr,hobby)
        self.marks=marks
        print('SchoolMember is %s' % self.name)
    
    def tell(self):
        super(Student,self).tell()
        print('My mark is %d' % self.marks)

if __name__=='__main__':
    #s=Student('mxl',22,'shanghai','swim',90)
    #s.tell()
    #print('s.marks is %d' %s.marks)
    s = SchoolMember('mxl',22,'shanghai','swim')
    s.tell()
    s.tell2()
