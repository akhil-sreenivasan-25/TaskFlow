from django.contrib import admin
from .models import Employee,Project,Task,CustomUser,client,ProjectCommentMedia,projectMedia,taskCommentMedia,tasktMedia
from .models import taskFinalCode,tasktFinalMedia,taskNotification

# Register your models here.
admin.site.register(Employee)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(CustomUser)
admin.site.register(client)
admin.site.register(ProjectCommentMedia)
admin.site.register(projectMedia)
admin.site.register(taskCommentMedia)
admin.site.register(tasktMedia)
admin.site.register(tasktFinalMedia)
admin.site.register(taskFinalCode)
admin.site.register(taskNotification)