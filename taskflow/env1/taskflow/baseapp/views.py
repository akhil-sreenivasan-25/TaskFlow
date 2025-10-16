from django.shortcuts import render,HttpResponse,redirect,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from .models import CustomUser,Employee,Project,Task,client,ProjectCommentMedia,projectMedia,taskCommentMedia,tasktMedia
from .models import taskFinalCode,tasktFinalMedia
from datetime import date,timedelta
from datetime import datetime
from django.db.models import Count,ExpressionWrapper,IntegerField,Value,FloatField,Q,Prefetch,F

# Create your views here.
def test(request):
    return HttpResponse("test page")

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
         tl_count={"p_count":project_count,"t_count":task_count,'dl_count':deadline_count,'user_det':emp_obj.role }

         #team management
         # Select distinct employees who are assigned to tasks in any of the projects led by the current team lead (tl_projects)
         tl_projects=emp_obj.led_projects.exclude(status='completed').values('projectid')
         #for find task count foe each employee under specific tl. not completed
         #task_det=Employee.objects.filter(e_tasks__project__in=tl_projects).annotate(t_count=Count('e_task'))#.distinct()
         #team_members=Employee.objects.distinct().exclude(empid=emp_obj.empid)
         
         team_members=Employee.objects.filter(e_tasks__project__in=tl_projects).distinct().exclude(empid=emp_obj.empid).annotate(member_task_count=Count('e_tasks'))
         #member_task_count=Task

         #task tracking
         tl_all_tasks=Task.objects.filter(project__in=tl_projects).order_by('due_date')[:8]

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
         tl_projects_det=emp_obj.led_projects.exclude(status='completed').order_by('end_date').values('projectid','project_name','end_date')[:10]

        # project progress
         test=Task.objects.filter(project__in=tl_projects).values('project','project__project_name','project__projectid').\
            annotate(total=Count('taskid'),taskcompleted=Count('taskid', filter=Q(status='completed')))\
                     .annotate(percent_completed=ExpressionWrapper(100.0 * F('taskcompleted') / F('total'),output_field=IntegerField()))\
                        .order_by('project__end_date') 
        #  test=test.annotate((pro_prec= 'test.taskcompleted' / 'test.total') * 100 )

         task_det=0
         return  render(request,"tl_dashboard.html",{"count":tl_count,"emp_manage":team_members,"pro_tasks":tl_all_tasks,"test_data":test,"emp_det":tot_emp,"emp_obj":emp_obj,"pro_details":test})
    else:
        return  HttpResponse("invalid user")
    

def member_home(request):
    if request.user.is_authenticated:
        u_id = int(request.user.id)        
        id=CustomUser.objects.get(id=u_id).empid        
        emp_obj=Employee.objects.get(empid=id)
        # return HttpResponse(str(emp_obj.empid))
        if(emp_obj.projects.count()==0):
            project_count=0
            task_count=0
            deadline_count=0          
            return HttpResponse(str(project_count) + str(task_count) + str(deadline_count))
        else:
            project_count= emp_obj.projects.exclude(status='completed').count()
            member_projects=emp_obj.projects.exclude(status='completed').values('projectid')
            task_count=Task.objects.filter(project__in=member_projects).exclude(status='completed').count()

            #deadline count project + task
            # tasks with due date within next 5 days and not completed
            day_differnce=date.today() + timedelta(days=5) 
            task_deadline_count=Task.objects.filter(project__in=member_projects,due_date__lte=day_differnce).exclude(status='completed').count()
            pro_deadline_count=emp_obj.projects.filter(end_date__lte=day_differnce).exclude(status='completed').count()
            deadline_count=task_deadline_count + pro_deadline_count
        tl_count={"p_count":project_count,"t_count":task_count,'dl_count':deadline_count,'user_det':emp_obj.role }

        mem_all_tasks=Task.objects.filter(assigned_to=emp_obj).order_by('due_date')[:11]

        member_projects=emp_obj.projects.exclude(status='completed').values('projectid')
        test=Task.objects.filter(project__in=member_projects).values('project','project__project_name','project__projectid').\
            annotate(total=Count('taskid'),taskcompleted=Count('taskid', filter=Q(status='completed')))\
                     .annotate(percent_completed=ExpressionWrapper(100.0 * F('taskcompleted') / F('total'),output_field=IntegerField()))\
                        .order_by('project__end_date')
     
        return  render(request,"tl_dashboard.html",{"count":tl_count,"pro_tasks":mem_all_tasks,"pro_details":test,"test_data":test,"emp_obj":emp_obj,"pro_details":test})
        return HttpResponse( "i am"+str(project_count) + "hy" + str(member_projects)  + "you"+ str(task_count))
    else:
        return render(request,"log_page.html")
    
def add_project(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            p_name=request.POST.get("p_name")
            p_desc=request.POST.get("p_desc")
            p_end=request.POST.get("p_end")
            p_end=datetime.strptime(p_end , '%Y-%m-%d').date()
            client_id=request.POST.get("client")
            client_obj=client.objects.get(clientid=client_id)            
            #p_end = datetime.strptime(p_end, '%d-%m-%Y').strftime('%Y-%m-%d')

            p_members=request.POST.getlist("p_members") # Get list of selected team members
            # return HttpResponse("list is"+str(p_members))
            u_id = int(request.user.id)
            id=CustomUser.objects.get(id=u_id).empid
            tl_emp=Employee.objects.get(empid=id) 
            new_project=Project(project_name=p_name,description=p_desc,end_date=p_end,team_lead=tl_emp,client_details=client_obj)
            new_project.save()

            # Add selected team members to the project
            for member_id in p_members:
                try:
                    member_emp = Employee.objects.get(empid=member_id)
                    new_project.team_members.add(member_emp)
                except Employee.DoesNotExist:
                    continue  # Skip if the employee does not exist

            new_project.save()
            projectid=new_project.projectid
            return JsonResponse({"success": True, "pro_id":projectid})

        else:
            return JsonResponse({"success": False, "pro_id":projectid})
    else:
        return render(request,"log_page.html")
    
def project_edit(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            project_id=request.POST.get("p_id")
            p_name=request.POST.get("p_name")
            p_desc=request.POST.get("p_desc")
            p_members=request.POST.getlist("p_members") # Get list of selected team members
            project_id=Project.objects.get(projectid=project_id)
            project_id.project_name=p_name
            project_id.description=p_desc
            project_id.save()
            if p_members:
                for member_id in p_members:
                    try:
                        member_emp = Employee.objects.get(empid=member_id)
                        project_id.team_members.add(member_emp)
                    except Employee.DoesNotExist:
                        continue  # Skip if the employee does not exist
            return HttpResponse("done")
            # return redirect('project_detailed_view',projectid=project_id.projectid)
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
            t_project=request.POST.get("pId")

            u_id = int(request.user.id)
            id=CustomUser.objects.get(id=u_id).empid
            tl_emp=Employee.objects.get(empid=id) 
            try:
                assigned_emp=Employee.objects.get(empid=t_assigned)
                project_obj=Project.objects.get(projectid=t_project)
                new_task=Task(title=t_title,description=t_desc,due_date=t_due,priority=t_priority,assigned_to=assigned_emp,project=project_obj)
                new_task.save()
                return JsonResponse({"success": True, "pro_id":t_project})
            except Employee.DoesNotExist:
                return JsonResponse("Assigned employee does not exist")
            except Project.DoesNotExist:
                return JsonResponse("Project does not exist")
        else:
            return JsonResponse("invalid access")
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
        
# fetch project details for task add 
def tl_projects(request):
    if request.method=="GET" :
        if request.user.is_authenticated :
            u_id = int(request.user.id)
            id=CustomUser.objects.get(id=u_id).empid
            tl_emp=Employee.objects.get(empid=id) 
            tl_pro=Project.objects.filter(team_lead=tl_emp)
            data = [{'id': pro.projectid, 'name': pro.project_name} for pro in tl_pro]
            return JsonResponse(data, safe=False)
        else :
            return render(request,"log_page.html")

def client_det(request):
    if request.user.is_authenticated:
        clients=client.objects.filter(is_active=True)
        data = [{'id': client.clientid, 'company': client.company_name} for client in clients]
        return JsonResponse(data, safe=False)
        
    else:
        return HttpResponse("invalid user")

def project_home(request):
    if request.user.is_authenticated:
        u_id = int(request.user.id)
        id=CustomUser.objects.get(id=u_id).empid
        emp_obj=Employee.objects.get(empid=id)
        if (emp_obj.role == 'team leader'):
            if(emp_obj.led_projects.count()==0):
                return HttpResponse ("No projects assigned")
            else :
                project_obj=Project.objects.filter(team_lead=emp_obj).order_by('end_date').select_related('client_details')
                count_obj=project_obj.annotate(t_count=Count('tasks')).annotate(pending_count=Count('tasks', filter=Q(tasks__status='completed')))
        elif(emp_obj.role == 'team member') : 
            if(emp_obj.projects.count()==0):
                return HttpResponse ("No projects assigned")
            else :           
                member_projects=emp_obj.projects.values_list('projectid',flat=True)
                # projects=emp_obj.projects.projectid
                project_obj=Project.objects.filter(projectid__in=member_projects).order_by('end_date').select_related('client_details')
                count_obj=project_obj.annotate(t_count=Count('tasks')).annotate(pending_count=Count('tasks', filter=Q(tasks__status='completed')))
        else:
            return HttpResponse("Invalid user")
        return  render(request,"project_det.html",{"pro_det":count_obj})
    else:
        return HttpResponse("invalid user")
    
    
# detailed view of the project with task, client details and attatcked documents with comments
def project_detailed_view(request,projectid):
    if request.user.is_authenticated:
        u_id =int(request.user.id)
        id=CustomUser.objects.get(id=u_id).empid
        emp_obj=Employee.objects.get(empid=id)
        project_det=Project.objects.get(projectid=projectid)
        client_det=project_det.client_details
        
        if(emp_obj.role == 'team leader'):
            tasks_det=Task.objects.filter(project=projectid).select_related('assigned_to').order_by('-status')
        else:
            tasks_det=Task.objects.filter(project=projectid,assigned_to=emp_obj).select_related('assigned_to').order_by('-status')
        team_member_id=list(project_det.team_members.values_list('empid', flat=True))
        tot_emp=Employee.objects.exclude(Q(empid=request.user.id) | Q(empid__in=team_member_id ) | Q(is_active=False))
        pro_comment=ProjectCommentMedia.objects.filter(project=project_det).select_related('uploaded_by')\
            .prefetch_related(Prefetch('media_files', queryset=projectMedia.objects.only('file'))).order_by('-uploaded_at')

        HttpResponse("project id is "+str(tasks_det))
        
        return render(request,"project_detailed_view.html",\
                      {"project":project_det,"client":client_det,"tasks":tasks_det,"role":emp_obj,"emp_det":tot_emp,"comments":pro_comment})
    else:
        return HttpResponse("invalid user")
    

# for editing project details - fetch employee details excluding tl and already assigned members
def project_edit_view(request,projectid):
    if request.user.is_authenticated:
        u_id = int(request.user.id)
        id=CustomUser.objects.get(id=u_id).empid
        project_det=Project.objects.get(projectid=projectid)
        team_member_id=list(project_det.team_members.values_list('empid', flat=True))
        tot_emp=Employee.objects.exclude(Q(empid=id) | Q(empid__in=team_member_id ) | Q(is_active=False)).values('empid','name')
        # data=tot_emp.values_list('empid','name')
        return JsonResponse(list(tot_emp),safe=False)
    else:
        return HttpResponse("invalid user")
    

# change project status by checking all tasks are completed or not
def project_status_change(request,projectid,pro_status):
    if request.user.is_authenticated:
        if request.method=="GET":
            try:
                project_obj=Project.objects.get(projectid=projectid)
                if project_obj.status == pro_status:
                    return HttpResponse("Status is already set to " + pro_status)
                elif pro_status == 'completed':
                    incomplete_tasks = Task.objects.filter(project=project_obj).exclude(status='completed')
                    if incomplete_tasks.exists():
                        return HttpResponse("Cannot mark project as completed. There are incomplete tasks.")
                    else :
                        project_obj.status=pro_status
                        project_obj.save()
                        return HttpResponse("Project marked as completed")
                else:
                    project_obj.status=pro_status
                    project_obj.save()
                    return HttpResponse("Project status updated to " + pro_status)
            except Project.DoesNotExist:
                return HttpResponse("Project does not exist")
        else:
            return HttpResponse("invalid access")
    else:
        return render(request,"log_page.html")
    

def project_comments(request,projectid):
    if request.user.is_authenticated:
        if request.method=="POST":
            comment=request.POST.get("comment")
            attachment=request.FILES.getlist("attachment")            
            user=request.user.id
            emp_id=CustomUser.objects.get(id=user).empid
            emp_id=Employee.objects.get(empid=emp_id)
            pro_obj=Project.objects.get(projectid=projectid)
            if pro_obj and emp_id:
                pro_comment=ProjectCommentMedia(project=pro_obj,uploaded_by=emp_id,comment=comment)
                pro_comment.save()
                for file in attachment:
                    media=projectMedia(comment=pro_comment,file=file)
                    media.save()
                # return redirect('project_detailed_view',projectid=projectid)
            else:
                return HttpResponse("Invalid project or User")

            # process and save the comment and attachment as needed
            return HttpResponse("Comment and attachment received" + str(projectid) +   str(emp_id) + " "+ str(emp_id.empid))
        else:
            return HttpResponse("invalid access")
    else:
        return HttpResponse("project comments page")
    
# view for specific task details
def pro_task_view(request,taskid):
    if request.user.is_authenticated:
        try:            
            u_id =int(request.user.id)
            id=CustomUser.objects.get(id=u_id).empid
            emp_obj=Employee.objects.get(empid=id)
            task_det=Task.objects.select_related('assigned_to','project__team_lead').get(taskid=taskid)
            task_comment=taskCommentMedia.objects.filter(task=task_det).select_related('uploaded_by')\
                .prefetch_related(Prefetch('task_media_files', queryset=tasktMedia.objects.only('file'))).order_by('-uploaded_at')
            task_code=None
            if task_det.status=='completed':
                task_code=taskFinalCode.objects.filter(task=task_det).prefetch_related('task_code_files').order_by('uploaded_at').first()
            return render(request,"pro_task_view.html",{"tasks":task_det,"role":emp_obj,"comments_task":task_comment,"task_code":task_code})
        except Task.DoesNotExist:
            return HttpResponse("Task does not exist")
    else:
        return render(request,"log_page.html")
    
#view for change task status
def change_task_status(request,task_id,new_status):
    if request.user.is_authenticated:
        if request.method=='GET':
            try:
                task_obj=Task.objects.get(taskid=task_id)
                if task_obj.status == new_status:
                    return HttpResponse("Status is already set to " + new_status)            
                else: 
                    task_obj.status=new_status
                    task_obj.save()
                    return HttpResponse("Task status updated to " + new_status)
                
            except Task.DoesNotExist:
                return HttpResponse("Task does not exist")
        elif request.method=='POST':
            try:
                task_obj=Task.objects.get(taskid=task_id)
                code=request.POST.get("code")
                attachment=request.FILES.getlist("taskCodeAttachment")            
                user=request.user.id
                emp_id=CustomUser.objects.get(id=user).empid
                emp_id=Employee.objects.get(empid=emp_id)
                if(new_status == 'completed' and task_obj):
                    task_obj.status=new_status
                    task_obj.save()
                    task_code=taskFinalCode(task=task_obj,uploaded_by=emp_id,code=code)
                    task_code.save()
                    for file in attachment:
                        media=tasktFinalMedia(code=task_code,file=file)
                        media.save()
                    return HttpResponse("Task status updated to " + new_status)
            except:
                return HttpResponse("Task does not exist")
        else:
            return HttpResponse("invalid access")
    else:
        return render(request,"log_page.html")
    
def task_comments(request,taskid):
    if request.user.is_authenticated:
        if request.method=="POST":
            comment=request.POST.get("comment")
            attachment=request.FILES.getlist("attachment")            
            user=request.user.id
            emp_id=CustomUser.objects.get(id=user).empid
            emp_id=Employee.objects.get(empid=emp_id)
            task_obj=Task.objects.get(taskid=taskid)
            if task_obj and emp_id:
                task_comment=taskCommentMedia(task=task_obj,uploaded_by=emp_id,comment=comment)
                task_comment.save()
                for file in attachment:
                    media=tasktMedia(comment=task_comment,file=file)
                    media.save()
                # return redirect('project_detailed_view',projectid=projectid)
            else:
                return HttpResponse("Invalid task or User")

            # process and save the comment and attachment as needed
            return HttpResponse("Comment and attachment received" + str(taskid) +   str(emp_id) + " "+ str(emp_id.empid))
        else:
            return HttpResponse("invalid access")
    else:
        return HttpResponse("task comments page")

def task_det(request):
    if request.user.is_authenticated:
        u_id =int(request.user.id)
        id=CustomUser.objects.get(id=u_id).empid
        emp_obj=Employee.objects.get(empid=id)
        if(emp_obj.role == 'team leader'):
            task_obj=Task.objects.filter(project__team_lead=emp_obj).select_related('assigned_to').order_by('-status','due_date')
        else :
            task_obj=Task.objects.filter(assigned_to=emp_obj).select_related('assigned_to').order_by('-status','due_date')
        return render(request,"task_det.html",{"task_det":task_obj})
    else:
        return render(request,"log_page.html")