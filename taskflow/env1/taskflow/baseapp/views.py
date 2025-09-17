from django.shortcuts import render,HttpResponse
from django.contrib.auth import authenticate,login,logout

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
                return render(request,"tl_dashboard.html")
            elif catogry=="TM":
                login(request,user)
                return render(request,"member_dashboard.html")
            else:
                return HttpResponse("Unauthorized user")
        else:
            return HttpResponse("No user found")
    else:
        return render(request,"log_page.html")
    
    

def tl_home(request):
    return  render(request,"tl_dashboard.html")

def member_home(request):
    return  render(request,"member_dashboard.html")