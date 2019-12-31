from django.contrib import admin
from mysite import models

class PostAdmin(admin.ModelAdmin):
    list_display=('nickname', 'message', 'enabled', 'pub_time')
    ordering=('-pub_time',)
admin.site.register(models.Mood)
admin.site.register(models.Post, PostAdmin)
# admin.site.register(models.User)
admin.site.register(models.Profile)
admin.site.register(models.Diary)