from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate,login,logout
from .models import CustomUser,Employee,Project,Task
from datetime import date,timedelta

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
             task_count=emp_obj.tasks.exclude(status='completed').count()
             day_differnce=date.today() + timedelta(days=5)
             #deadline count project + task
             task_deadline_count=emp_obj.tasks.filter(due_date__lte=day_differnce).exclude(status='completed').count()
             pro_deadline_count=emp_obj.led_projects.filter(end_date__lte=day_differnce).exclude(status='completed').count()
             deadline_count=task_deadline_count + pro_deadline_count

         tl_count={"p_count":project_count,"t_count":task_count,'dl_count':deadline_count}

         return  render(request,"tl_dashboard.html",{"count":tl_count})
    else:
        return  HttpResponse("invalid user")

def member_home(request):
    return  render(request,"member_dashboard.html")