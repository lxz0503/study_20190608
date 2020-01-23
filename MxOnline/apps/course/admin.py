from django.contrib import admin
from course.models import Course, Lesson, Video, CourseResource

# Register your models here.自己定义admin，一般用类来实现，参考下面的模板
# 要显示的字段放在一个列表或者元组里面，名字固定叫做list_display
class CourseAdmin(admin.ModelAdmin):
    '''课程'''
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']  # 显示的字段
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']  # 搜索条件
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']   # 过滤条件
    list_per_page = 2  # 每页显示两条记录


class LessonAdmin(admin.ModelAdmin):
    '''章节'''
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    # # 这里course__name是根据课程名称过滤, 注意格式双下划线，表示lesson里面有个course外键
    list_filter = ['course__name', 'name', 'add_time']
    list_per_page = 2

class VideoAdmin(admin.ModelAdmin):
    '''视频'''
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']
    list_per_page = 2

class CourseResourceAdmin(admin.ModelAdmin):
    '''课程资源'''
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course__name', 'name', 'download', 'add_time']
    list_per_page = 2

# 将管理器与model进行注册关联
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(CourseResource, CourseResourceAdmin)
