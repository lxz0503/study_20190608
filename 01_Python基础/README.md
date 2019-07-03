# study_python
1. 创建出来的 对象 叫做 类 的 实例

2. 创建对象的 动作 叫做 实例化

3. 对象的属性 叫做 实例属性

4. 对象调用的方法 叫做 实例方法

class Git(object):


def CommitInfo(self, commitId):

    
def GetAuthors(self, oldCommitId, newCommitId):
        """ return a list of (author, authorEmail) between 2 commits 
        ISSUE: git log old..new --format=xx Has problem when there is a Merge between old and new commits
        """
        if oldCommitId == newCommitId:
            (_, author, email, _, _, _) = self.CommitInfo(newCommitId)
#上面两个函数都属于一个类，下面的GetAuthors函数里面调用了上面的CommitInfo函数，
#在类里面的函数调用，前面要加上self表示同属于一个类
#MySQL命令终止符为分号;
# 类属性就是在类名下面定义个变量，记录类相关的特性，不是定义在init函数里面
# 在外部访问类属性就用 类名.类属性的方式，类名.类方法（）
# 在类的实例方法内部访问类属性，用self.类属性 即可
# 类方法的定义：
@classmethod
def fun(cls, a):
    在类方法内部，只需要访问类属性
# 在外部，依然可以通过 对象.类方法() 来访问类方法
在类内部，可以通过cls.fun()来调用类方法，也可以用cls.类属性访问类属性
# 由哪一个类调用的方法，方法内的cls就是哪一个类的引用，这个参数和实例方法的self参数类似

#如果需要在类中封装一个方法，这个方法及不需要访问实例属性或者调用实例方法
#也不需要访问类属性或者条用类方法,此方法不需要传递self参数
#这个时候，可以把这个方法封装成一个静态方法,在类的外部通过类名.静态方法（）来调用静态方法
@staticmethod
def fun():
    pass
#实例属性应该在init方法内部定义
#如果方法内部既需要访问实例属性，又需要访问类属性，应该定义成实例方法
#类只有一个，在实例方法内部，可以使用类名.类属性来访问类属性
# Python3默认就是UTF-8编码，和python2不一样
