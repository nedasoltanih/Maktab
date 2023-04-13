from django.contrib import admin

from .models import Task, User, GoldUser, HWTask

admin.site.register(Task)
admin.site.register(User)
admin.site.register(GoldUser)
admin.site.register(HWTask)

