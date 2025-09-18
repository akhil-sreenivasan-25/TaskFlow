from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
#extention for user
class CustomUser(AbstractUser):
    designation = models.CharField(max_length=50, blank=True, null=True)
    desig_prefix = models.CharField(max_length=2, blank=True, null=True)
    empid = models.CharField(max_length=20, unique=True, blank=True, null=True)
    


#emplloyee details
class Employee(models.Model):
    empid=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100)
    email=models.EmailField(unique=True)
    role=models.CharField(max_length=50)  # e.g., 'team_lead' or 'member'
    date_joined=models.DateField(auto_now_add=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

    
#project details
class Project(models.Model):
    projectid=models.AutoField(primary_key=True)
    project_name=models.CharField(max_length=100)
    description=models.TextField()
    start_date=models.DateField()
    end_date=models.DateField(null=True, blank=True)
    status=models.CharField(max_length=50, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='In Progress')
    team_lead=models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='led_projects')

    def __str__(self):
        return self.project_name
    
class Task(models.Model):
    taskid=models.AutoField(primary_key=True)
    title=models.CharField(max_length=200)
    description=models.TextField()
    assigned_to=models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='tasks')
    project=models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    status=models.CharField(max_length=50, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='pending')
    priority=models.CharField(max_length=50, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    due_date=models.DateField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title