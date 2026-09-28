from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),

    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('create_project/', views.create_project, name='create_project'),
    path('update_project/<int:pk>/', views.update_project, name='update_project'),
    path('delete_project/<int:pk>/', views.delete_project, name='delete_project'),

    path('project_detail/<int:pk>/', views.project_detail, name='project_detail'),
    path('create_task/<int:pk>/', views.create_task, name='create_task'),
    path('update_task/<int:pk>/', views.update_task, name='update_task'),
    path('delete_task/<int:pk>/', views.delete_task, name='delete_task'),

]