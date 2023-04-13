from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from .models import Task, User
from django.db.models import Count

def tasks_view(request, num):
    tasks = Task.objects.all()
    if num == 'all':
        # return HttpResponse(tasks)
        return render(request, 'reminder/tasks.html', {'tasks': tasks})
    else:
        return HttpResponse(tasks[:num])


def task_detail(request, id):
    task = Task.objects.get(pk=id)
    return render(request, 'reminder/task_detail.html', {'task': task})


def one_user_tasks(request, slug):
    name = User.objects.get(slug=slug)
    tasks = Task.objects.filter(user=name)
    return render(request, 'reminder/user_tasks.html', {'tasks': tasks})


def users_view(request):
    users = User.objects.all()
    return render(request, 'reminder/users.html', {'users': users})


def one_user(request, slug):
    user = User.objects.filter(slug=slug)
    if not user:
        return HttpResponseNotFound('<h1>User not found</h1>')
    return HttpResponse(user[0].name)


def user_with_notasks(request):
    # users = User.objects.all()
    # fusers = []
    # for user in users:
    #     if not Task.objects.filter(user=user.name):
    #         fusers.append(user)

    fusers = User.objects.annotate(tasks=Count('task')).filter(tasks=0)

    # fusers = []
    # tasks = Task.objects.all().values('user')
    # users = User.objects.all()
    # for user in users:
    #     if user.name not in  tasks:
    #         fusers.append(user)

    return render(request, 'reminder/users.html', {'users': fusers})


def new_task(request):
    if request.method == "GET":
        return render(request, "reminder/new_task.html")
    elif request.method == "POST":
        task = Task(title=request.POST["title"], due_date=request.POST["due_date"])
        task.save()
        return HttpResponse("Saved!")