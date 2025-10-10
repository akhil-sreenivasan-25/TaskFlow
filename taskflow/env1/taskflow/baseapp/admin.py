from django.contrib import admin
from .models import Employee,Project,Task,CustomUser,client,ProjectCommentMedia,projectMedia

# Register your models here.
admin.site.register(Employee)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(CustomUser)
admin.site.register(client)
admin.site.register(ProjectCommentMedia)
admin.site.register(projectMedia)