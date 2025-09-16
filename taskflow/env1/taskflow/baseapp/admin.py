from django.contrib import admin
from .models import Employee,Project,Task

# Register your models here.
admin.site.register(Employee)
admin.site.register(Project)
admin.site.register(Task)