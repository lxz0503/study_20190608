from django.contrib import admin
from users.models import EmailVerifyRecord, Banner, UserProfile


# Register your models here.

# email register
class EmailVerifyRecordAdmin(admin.ModelAdmin):
    # 显示的列
    list_display = ['code', 'email', 'send_type', 'send_time']
    # 搜索的字段，不要添加时间搜索
    # search_fields = ['code', 'email', 'send_type']
    # 过滤
    # list_filter = ['code', 'email', 'send_type', 'send_time']

# banner register
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'image', 'url','index', 'add_time']
    # search_fields = ['title', 'image', 'url','index']
    # list_filter = ['title', 'image', 'url','index', 'add_time']

# user management
class UserProfileAdmin(admin.ModelAdmin):
    pass

# 将管理器与model进行注册关联
admin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(UserProfile, UserProfileAdmin)


