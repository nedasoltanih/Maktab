from django.urls import path, include
from . import views

extra_patterns = [
    path('', views.users_view),
    path('tasks-<slug:slug>/', views.one_user_tasks, name="user_tasks"),
    path('notask/', views.user_with_notasks, name="notask"),
    path('<slug:slug>/', views.one_user),
    # path('<int:id>/', views.one_user)
]

urlpatterns =[
    path('tasks/', views.tasks_view, {'num': 'all'}),
    path('new_task/', views.new_task),
    path('task-<slug:id>/', views.task_detail, name='task_detail'),
    path('recent_tasks/', views.tasks_view, {'num': 2}),
    path('users/', include(extra_patterns)),
]