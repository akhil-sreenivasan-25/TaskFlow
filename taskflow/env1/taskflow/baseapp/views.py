from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate,login,logout
from .models import CustomUser,Employee,Project,Task
from datetime import date,timedelta
from django.db.models import Count

# Create your views here.
def test(request):
    return render(request,"member_dashboard.html")

#user authentication and login
def login_page(request):
    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        user=authenticate(request,username=username,password=password)
        if user is not None:
            catogry=user.desig_prefix
            if catogry=="TL":
                login(request,user)
                return redirect('tl_home')
            elif catogry=="TM":
                login(request,user)
                return redirect('member_home')
            else:
                return HttpResponse("Unauthorized user")
        else:
            return HttpResponse("No user found")
    else:
        return render(request,"log_page.html")
    
    

def tl_home(request):
    if request.user.is_authenticated:
         u_id = int(request.user.id)
         id=CustomUser.objects.get(id=u_id).empid
         emp_obj=Employee.objects.get(empid=id)          
         # find count - project task deadline
         if(emp_obj.led_projects.count()==0):
             project_count=0
             task_count=0
             deadline_count=0
         else:
             project_count= emp_obj.led_projects.exclude(status='completed').count()
             tl_projects=emp_obj.led_projects.exclude(status='completed').values('projectid')
             task_count=Task.objects.filter(project__in=tl_projects).exclude(status='completed').count()
             #deadline count project + task
             # tasks with due date within next 5 days and not completed
             day_differnce=date.today() + timedelta(days=5) 
             task_deadline_count=Task.objects.filter(project__in=tl_projects,due_date__lte=day_differnce).exclude(status='completed').count()
             pro_deadline_count=emp_obj.led_projects.filter(end_date__lte=day_differnce).exclude(status='completed').count()
             deadline_count=task_deadline_count + pro_deadline_count
         tl_count={"p_count":project_count,"t_count":task_count,'dl_count':deadline_count}

         #team management
         # Select distinct employees who are assigned to tasks in any of the projects led by the current team lead (tl_projects)
         tl_projects=emp_obj.led_projects.exclude(status='completed').values('projectid')
         #for find task count foe each employee under specific tl. not completed
         #task_det=Employee.objects.filter(e_tasks__project__in=tl_projects).annotate(t_count=Count('e_task'))#.distinct()
         #team_members=Employee.objects.distinct().exclude(empid=emp_obj.empid)
         task_det=0
         team_members=Employee.objects.filter(e_tasks__project__in=tl_projects).distinct().exclude(empid=emp_obj.empid)

         #task tracking
         tl_all_projects=emp_obj.led_projects.exclude(status='completed').values('projectid')
         tl_all_tasks=Task.objects.filter(project__in=tl_all_projects).values('title','due_date','priority','status')

         return  render(request,"tl_dashboard.html",{"count":tl_count,"emp_manage":team_members,"pro_tasks":tl_all_tasks,"test_data":tl_all_tasks})
    else:
        return  HttpResponse("invalid user")

def member_home(request):
    return  render(request,"member_dashboard.html")