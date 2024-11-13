from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    register,
    login_view,
    logout_view,
    my_profile,
    create_project,
    get_projects,
    create_task,
    get_tasks,
    task_detail,
    get_workers,
    create_worker,
    worker_detail,
)
 
urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('myprofile/', my_profile, name='my_profile'),
    path('projects/', get_projects, name='get_projects'),
    path('projects/create/', create_project, name='create_project'),
    path('tasks/', get_tasks, name='get_tasks'),
    path('tasks/create/', create_task, name='create_task'),
    path('tasks/<int:pk>/', task_detail, name='task_detail'),
    path('workers/', get_workers, name='get_workers'),
    path('workers/create/', create_worker, name='create_worker'),
    path('workers/<int:pk>/', worker_detail, name='worker_detail'),
    path('resources/', views.get_resources, name='get_resources'),
    path('resources/create/', views.create_resource, name='create_resource'),
    path('resources/<int:pk>/', views.resource_detail, name='resource_detail'),
]




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
