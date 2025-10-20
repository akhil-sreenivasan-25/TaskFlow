from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


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
    
class client(models.Model):
    clientid=models.AutoField(primary_key=True)
    client_name=models.CharField(max_length=100)
    contact_email=models.EmailField(unique=True)
    contact_phone=models.CharField(max_length=15, null=True, blank=True)
    company_name=models.CharField(max_length=100, null=True, blank=True)
    address=models.TextField(null=True, blank=True)
    country=models.CharField(max_length=50, null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.client_name
    
#project details
class Project(models.Model):
    projectid=models.AutoField(primary_key=True)
    project_name=models.CharField(max_length=100)
    description=models.TextField()
    start_date=models.DateField(auto_now_add=True)
    end_date=models.DateField(null=True, blank=True)
    status=models.CharField(max_length=50, choices=[('pending', 'Pending'), ('in progress', 'In Progress'), ('completed', 'Completed')], default='In Progress')
    team_lead=models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='led_projects') # linked employee table. connect the employee whos the tl of the project
    team_members=models.ManyToManyField(Employee, related_name='projects', blank=True) #linked employee table. connect the employee who are the members of the project
    client_details=models.ForeignKey(client, on_delete=models.CASCADE, related_name='client_det', blank=True, null=True) #linked client table. connect the client details of the project

    def __str__(self):
        return self.project_name
    
class Task(models.Model):
    taskid=models.AutoField(primary_key=True)
    title=models.CharField(max_length=200)
    description=models.TextField()
    assigned_to=models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='e_tasks') #linked employee table based on task assigning
    project=models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks') #linked project table based on which project belong this task
    status=models.CharField(max_length=50, choices=[('pending', 'Pending'), ('in progress', 'In Progress'),('under review','Mark completed'), ('completed', 'Completed')], default='pending')
    priority=models.CharField(max_length=50, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    due_date=models.DateField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

def media_upload_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    if ext in ['jpg', 'jpeg', 'png']:
        folder = 'images'
    elif ext in ['mp4', 'mov']:
        folder = 'videos'
    elif ext in ['mp3', 'wav']:
        folder = 'audio'
    elif ext in ['pdf', 'docx', 'xlsx']:
        folder = 'documents'
    else:
        folder = 'others'
    # project_id = instance.comment.project.projectid if instance.comment and instance.comment.project else 'unknown'
    if hasattr(instance, 'comment'):
        if hasattr(instance.comment, 'project') and instance.comment.project:
            context_id = f'project_{instance.comment.project.projectid}'
        elif hasattr(instance.comment, 'task') and instance.comment.task:
            context_id = f'task_{instance.comment.task.taskid}'
        else:
            context_id = 'unknown'
    else:
        context_id = 'unknown'
    return f'project_media/{context_id}/{folder}/{filename}'
    # return f'project_media/project_{project_id}/{folder}/{filename}'

# porject comments and media
class ProjectCommentMedia(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    file = models.FileField( blank=True, null=True)
    uploaded_by = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"Comment by {self.uploaded_by} on {self.project.name}"

class projectMedia(models.Model):
    comment=models.ForeignKey(ProjectCommentMedia,on_delete=models.CASCADE,related_name='media_files')
    file=models.FileField(upload_to=media_upload_path, blank=True, null=True) 
    uploaded_at=models.DateTimeField(auto_now_add=True)


# porject comments and media
class taskCommentMedia(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_comments')
    comment = models.TextField()
    file = models.FileField( blank=True, null=True)
    uploaded_by = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"Comment by {self.uploaded_by} on {self.project.name}"

# task comment 
class tasktMedia(models.Model):
    comment=models.ForeignKey(taskCommentMedia,on_delete=models.CASCADE,related_name='task_media_files')
    file=models.FileField(upload_to=media_upload_path, blank=True, null=True) 
    uploaded_at=models.DateTimeField(auto_now_add=True)

# task final code
class taskFinalCode(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_code')
    code = models.TextField()
    file = models.FileField( blank=True, null=True)
    uploaded_by = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

# task final media
class tasktFinalMedia(models.Model):
    code=models.ForeignKey(taskFinalCode,on_delete=models.CASCADE,related_name='task_code_files')
    file=models.FileField(upload_to=media_upload_path, blank=True, null=True) 
    uploaded_at=models.DateTimeField(auto_now_add=True)

# task notification - upcoming
class taskNotification(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL ,on_delete=models.CASCADE)
    message=models.TextField()
    is_read=models.BooleanField(default=False)
    timestamp=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} : {self.message}"