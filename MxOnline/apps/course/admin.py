from django.contrib import admin
from course.models import Course, Lesson, Video, CourseResource

# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    '''课程'''
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    # search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    # list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']


class LessonAdmin(admin.ModelAdmin):
    '''章节'''
    list_display = ['course', 'name', 'add_time']
    # search_fields = ['course', 'name']
    # # 这里course__name是根据课程名称过滤
    # list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(admin.ModelAdmin):
    '''视频'''
    list_display = ['lesson', 'name', 'add_time']
    # search_fields = ['lesson', 'name']
    # list_filter = ['lesson', 'name', 'add_time']


class CourseResourceAdmin(admin.ModelAdmin):
    '''课程资源'''
    list_display = ['course', 'name', 'download', 'add_time']
    # search_fields = ['course', 'name', 'download']
    # list_filter = ['course__name', 'name', 'download', 'add_time']


# 将管理器与model进行注册关联
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(CourseResource, CourseResourceAdmin)
