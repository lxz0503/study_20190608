from django.db import models
from datetime import datetime
from users.models import UserProfile
from course.models import Course

# Create your models here.
# operation 用户操作
# user咨询
class UserAsk(models.Model):
    name = models.CharField('姓名', max_length=20)
    mobile = models.CharField('手机', max_length=11)
    course_name = models.CharField('课程名', max_length=50)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        verbose_name = '用户咨询'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

# user message ？？？？作用是什么？
# user字段，默认0代表消息是发给所有用户，而不是某个单独的用户；可以通过user.id发给特定用户消息
class UserMessage(models.Model):
    user = models.IntegerField('接受用户', default=0)
    message = models.CharField('消息内容', max_length=500)
    has_read = models.BooleanField('是否已读', default=False)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        verbose_name = '用户消息'
        verbose_name_plural = verbose_name

# CourseComments 课程评论
class CourseComments(models.Model):   # 谁评论的？哪门课程？所以关联了其他两个表  UserProfile  Course
    user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE)
    comments = models.CharField('评论', max_length=200)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        verbose_name = '课程评论'
        verbose_name_plural = verbose_name

# UserCourse 用户学习的课程
class UserCourse(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name='用户',on_delete=models.CASCADE)
    course = models.ForeignKey(Course, verbose_name='课程',on_delete=models.CASCADE)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        verbose_name = '用户课程'
        verbose_name_plural = verbose_name


# 用户收藏的课程
class UserFavorite(models.Model):
    FAV_TYPE = (
        (1, '课程'),
        (2, '课程机构'),
        (3, '讲师')
    )

    user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    fav_id = models.IntegerField('数据id', default=0)
    fav_type = models.IntegerField(verbose_name='收藏类型', choices=FAV_TYPE,default=1)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name