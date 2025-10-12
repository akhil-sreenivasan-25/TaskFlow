"""
URL configuration for taskflow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('test/',views.test,name="test"),
    path('login/',views.login_page,name="login"),
    path('logout/',views.logout_page,name="logout"),
    path('tl_home/',views.tl_home,name="tl_home"),
    path('project_home/',views.project_home,name="project_home"),
    path('add_project/',views.add_project,name="add_project"),
    path('add_task/',views.add_task,name="add_task"),
    path('team_member/<int:projectid>/', views.team_member, name='team_member'),
    path('client_det/', views.client_det, name='client_det'),
    path('project_detailed_view/<int:projectid>/', views.project_detailed_view, name='project_detailed_view'),
    path('edit_project/', views.project_edit, name="edit_project"),
    path('project_edit/<int:projectid>/', views.project_edit_view, name='project_edit_view'),
    path('project_status_change/<int:projectid>/<str:pro_status>/', views.project_status_change, name='project_status_change'),
    path('project_comments/<int:projectid>/',views.project_comments,name='project_comments'),
    path('pro_task_view/<int:taskid>/',views.pro_task_view,name='pro_task_view'),
    path('change_task_status/<int:task_id>/<str:new_status>/', views.change_task_status, name='change_task_status'),
    path('task_comments/<int:taskid>/',views.task_comments,name='task_comments'),
    path('task_details/',views.task_det,name='task_details')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
