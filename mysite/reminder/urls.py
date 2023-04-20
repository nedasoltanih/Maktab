from django.urls import path, include
from . import views

extra_patterns = [
    path('', views.UserList.as_view()),
    path('all/', views.users_view),
    path('tasks-<slug:slug>/', views.one_user_tasks, name="user_tasks"),
    path('notask/', views.UsersNoTask.as_view(), name="notask"),
    path('<slug:slug>/', views.one_user),
    # path('<int:id>/', views.one_user)
]

urlpatterns =[
    path("", views.BaseView.as_view(), name="index"),
    path("home/",views.RedirView.as_view()),
    path('tasks/', views.TaskList.as_view(), {'num': 'all'}),
    path('tasks/all/', views.tasks_view, {'num': 'all'}),
    path('tasks-<slug:slug>', views.UserTasks.as_view()),
    path('new_task/', views.new_task),
    path('task-<int:pk>/', views.TaskDetail.as_view(), name='task_detail'),
    path('recent_tasks/', views.tasks_view, {'num': 2}),
    path('users/', include(extra_patterns)),
]