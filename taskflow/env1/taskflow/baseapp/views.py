from django.shortcuts import render,HttpResponse

# Create your views here.
def test(request):
    return render(request,"member_dashboard.html")

def login(request):
    return render(request,"log_page.html")

def tl_home(request):
    return  render(request,"tl_dashboard.html")

def member_home(request):
    return  render(request,"member_dashboard.html")