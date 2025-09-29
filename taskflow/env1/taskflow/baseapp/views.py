from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from .models import CustomUser,Employee,Project,Task
from datetime import date,timedelta
from datetime import datetime
from django.db.models import Count,ExpressionWrapper,IntegerField,Value,FloatField,Q

# Create your views here.
def test(request):
    return render(request,"project_tab.html")

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
    
def logout_page(request):
    if request.method=="POST":
        if request.user.is_authenticated:
            logout(request)
            response = redirect('login')
            response.delete_cookie('sessionid')  # Optional: depends on your setup
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response
        else:
            return HttpResponse("invalid user")
    else:
        return HttpResponse("invalid access")
    
    
@never_cache
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
         
         team_members=Employee.objects.filter(e_tasks__project__in=tl_projects).distinct().exclude(empid=emp_obj.empid).annotate(member_task_count=Count('e_tasks'))
         #member_task_count=Task

         #task tracking
         tl_all_tasks=Task.objects.filter(project__in=tl_projects).values('title','due_date','priority','status').order_by('due_date')

         #project progress
         tl_projects=emp_obj.led_projects.exclude(status='completed').values_list('projectid', flat=True)
         tl_tasks=Task.objects.filter(project__in=tl_projects).count()
         # active task count group by project and status in in_progress and pending
         tl_tasks_progress=Task.objects.filter(project__in=tl_projects,status__in=('in_progress','pending'))\
            .values('project').annotate(t_count=ExpressionWrapper((Count('taskid') / Value(tl_tasks)) , output_field=FloatField()))\
                .values('project','project__project_name','t_count')
         
         #employee details for add new project
         tot_emp=Employee.objects.exclude(Q(empid=emp_obj.empid) | Q(is_active=False))

        #project details for add new task
         tl_projects_det=emp_obj.led_projects.exclude(status='completed').values('projectid','project_name')

         task_det=0
         return  render(request,"tl_dashboard.html",{"count":tl_count,"emp_manage":team_members,"pro_tasks":tl_all_tasks,"test_data":tl_projects,"emp_det":tot_emp,"emp_obj":emp_obj,"pro_details":tl_projects_det})
    else:
        return  HttpResponse("invalid user")
    
def add_project(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            p_name=request.POST.get("p_name")
            p_desc=request.POST.get("p_desc")
            p_end=request.POST.get("p_end")
            p_end=datetime.strptime(p_end , '%Y-%m-%d').date()
            #p_end = datetime.strptime(p_end, '%d-%m-%Y').strftime('%Y-%m-%d')

            p_members=request.POST.getlist("p_members") # Get list of selected team members
            # return HttpResponse("list is"+str(p_members))
            u_id = int(request.user.id)
            id=CustomUser.objects.get(id=u_id).empid
            tl_emp=Employee.objects.get(empid=id) 
            new_project=Project(project_name=p_name,description=p_desc,end_date=p_end,team_lead=tl_emp)
            new_project.save()

            # Add selected team members to the project
            for member_id in p_members:
                try:
                    member_emp = Employee.objects.get(empid=member_id)
                    new_project.team_members.add(member_emp)
                except Employee.DoesNotExist:
                    continue  # Skip if the employee does not exist

            new_project.save()
            return redirect('tl_home')
        else:
            return HttpResponse("invalid access")
    else:
        return render(request,"log_page.html")
    
def add_task(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            t_title=request.POST.get("t_name")
            t_desc=request.POST.get("t_desc")
            t_due=request.POST.get("t_end")
            t_due=datetime.strptime(t_due , '%Y-%m-%d').date()
            t_priority=request.POST.get("t_priority")
            t_assigned=request.POST.get("assign_to")
            t_project=request.POST.get("p_id")

            u_id = int(request.user.id)
            id=CustomUser.objects.get(id=u_id).empid
            tl_emp=Employee.objects.get(empid=id) 
            try:
                assigned_emp=Employee.objects.get(empid=t_assigned)
                project_obj=Project.objects.get(projectid=t_project)
                new_task=Task(title=t_title,description=t_desc,due_date=t_due,priority=t_priority,assigned_to=assigned_emp,project=project_obj)
                new_task.save()
                return redirect('tl_home')
            except Employee.DoesNotExist:
                return HttpResponse("Assigned employee does not exist")
            except Project.DoesNotExist:
                return HttpResponse("Project does not exist")
        else:
            return HttpResponse("invalid access")
    else:
        return render(request,"log_page.html")
    

#for collect the employee details of the specific project    
def team_member(request,projectid):
    if request.method=="GET" :
        if request.user.is_authenticated :
            projects_id=Project.objects.get(projectid=projectid)
            employees = projects_id.team_members.all()
            data = [{'id': emp.empid, 'name': emp.name} for emp in employees]
            return JsonResponse(data, safe=False)
        else :
            return render(request,"log_page.html")


def member_home(request):
    if request.user.is_authenticated:
        return  render(request,"project_det.html")
    else:
        return HttpResponse("invalid user")