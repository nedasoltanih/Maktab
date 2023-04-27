from django.urls import path, include, re_path
from . import views

extra_patterns = [
    path('', views.UserList.as_view(), name="users"),
    path('all/', views.users_view),
    path('tasks-<slug:slug>/', views.one_user_tasks, name="user_tasks"),
    path('notask/', views.UsersNoTask.as_view(), name="notask"),
    path('<slug:slug>/', views.one_user),
    # path('<int:id>/', views.one_user)
]

urlpatterns = [
    path("", views.BaseView.as_view(), name="index"),
    path("home/",views.RedirView.as_view()),
    path("login/",views.LoginView.as_view(), name='login'),
    path('tasks/', views.TaskList.as_view(), name='tasks'),
    path('tasks/all/', views.tasks_view, {'num': 'all'}, name="all_tasks"),
    path('tasks-<slug:slug>', views.UserTasks.as_view()),
    path('new_task/', views.NewTask.as_view(), name="new_task"),
    path('task-<int:pk>/', views.TaskDetail.as_view(), name='task_detail'),
    path('recent_tasks/', views.tasks_view, {'num': 2}),
    path('users/', include(extra_patterns)),
    re_path(r'user*', views.UsersRedir.as_view()),
]