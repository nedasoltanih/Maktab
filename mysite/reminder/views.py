import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.base import View, TemplateView, RedirectView
from django.core.paginator import Paginator

from .models import Task, User
from django.db.models import Count


def tasks_view(request, num):
    if request.method == "POST":
        if request.POST.get("color", ""):
            request.session['color'] = request.POST["color"]
            return redirect("all_tasks")
        else:
            for task in Task.objects.all():
                if str(task.pk) in request.POST.keys():
                    Task.objects.get(pk=task.pk).delete()
            return HttpResponse("Success! Deleted tasks.")
    else:
        color = request.session.get('color', "black")
        tasks = Task.objects.all()
        if num == 'all':
            # return HttpResponse(tasks)
            paginator = Paginator(tasks, 2)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, 'reminder/tasks.html', {'page_obj': page_obj, 'color': color})
        else:
            return HttpResponse(tasks[:num])


class TaskList(ListView):
    model = Task
    template_name = "reminder/tasks.html"
    context_object_name = "tasks"
    paginate_by = 4

    def get(self, request):
        if request.session.get("username"):
            last_login = request.COOKIES.get("last_login")
            tasks = Task.objects.filter(user=request.session.get("username"))
            paginator = Paginator(tasks, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            response = render(request, 'reminder/tasks.html', {'page_obj': page_obj, 'tasks': tasks, 'last_login':last_login})
            response.set_cookie("last_login", datetime.datetime.now())
            return response
        return super().get(request)

    def post(self, request):
        if request.POST.get("color", ""):
            request.session['color'] = request.POST["color"]
            return redirect("tasks")
        else:
            for task in Task.objects.all():
                if str(task.pk) in request.POST.keys():
                    Task.objects.get(pk=task.pk).delete()
            return HttpResponse("Success! Deleted tasks.")


def task_detail(request, id):
    task = Task.objects.get(pk=id)
    return render(request, 'reminder/task_detail.html', {'task': task})


class TaskDetail(DetailView):
    model = Task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = User.objects.get(name=context['task'].user.name)
        if context['task'].due_date > timezone.now().date():
            context['days_left'] = context['task'].due_date - timezone.now().date()
        return context

    def post(self, request, pk):
        task = Task.objects.get(pk=pk)
        task.delete()
        return HttpResponse("Success!")


def one_user_tasks(request, slug):
    # name = User.objects.get(slug=slug)
    # tasks = Task.objects.filter(user=name)
    tasks = Task.objects.get_user_tasks(slug)
    return render(request, 'reminder/user_tasks.html', {'tasks': tasks})


def users_view(request):
    users = User.objects.all()
    last_login = request.COOKIES.get("last_login")
    return render(request, 'reminder/users.html', {'users': users, 'last_login':last_login})


class UserList(ListView):
    model = User
    context_object_name = "users"
    template_name = "reminder/users.html"

    def get_queryset(self):
        users = User.objects.all()
        for user in users:
            user.undone_tasks = len(Task.objects.filter(user=user, done=False))
        return users

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data()
    #     context['num_users'] = len(context['users'])
    #     for user in context['users']:
    #         context[user.name] = len(Task.objects.filter(user=user).filter(done=False))
    #     return context


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
        users = User.objects.all()
        return render(request, "reminder/new_task.html", context={'users': users, 'categories': Task.categories})
    elif request.method == "POST":
        user = User.objects.get(name=request.POST["user"])
        done = True if "done" in request.POST.keys() else False
        print(request.POST)
        task = Task(title=request.POST["title"], due_date=request.POST["due_date"]
                    , category=request.POST["category"], done=done, hour=request.POST["hour"], user=user)
        task.save()
        return HttpResponse("Saved!")


class NewTask(View):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        if "id" in request.GET.keys():
            task = Task.objects.get(pk=request.GET["id"])
            return render(request, "reminder/new_task.html", context={'users': users,
                                                                      'categories': Task.categories,
                                                                      'task': task})
        else:
            return render(request, "reminder/new_task.html", context={'users': users, 'categories': Task.categories})

    def post(self, request, *args, **kwargs):
        user = User.objects.get(name=request.POST["user"])
        done = True if "done" in request.POST.keys() else False
        if request.GET["id"]:
            task = Task.objects.get(pk=request.GET["id"])
            task.title = request.POST["title"]
            task.due_date = request.POST["due_date"]
            task.category = request.POST["category"]
            task.done = done
            task.hour = request.POST["hour"]
            task.user = user
        else:
            task = Task(title=request.POST["title"], due_date=request.POST["due_date"]
                        , category=request.POST["category"], done=done, hour=request.POST["hour"], user=user)
        task.save()
        return HttpResponse("Saved!")


class UsersNoTask(View):
    def get(self, request, *args, **kwargs):
        # fusers = User.objects.annotate(tasks=Count('task')).filter(tasks=0)
        fusers = User.objects.with_no_tasks()
        return render(request, 'reminder/users.html', {'users': fusers})


class BaseView(TemplateView):
    template_name = "reminder/base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['objects'] = Task.objects.filter(due_date__gte=timezone.now().date()).order_by('due_date')[:3]
        return context


class RedirView(RedirectView):
    pattern_name = "index"


class UserTasks(ListView):
    context_object_name = "tasks"
    template_name = "reminder/tasks.html"

    def get_queryset(self):
        self.user = get_object_or_404(User, slug=self.kwargs['slug'])
        return Task.objects.filter(user=self.user)


class UsersRedir(RedirectView):
    pattern_name = 'users'


class LoginView(View):

    def get(self, request):
        logged_in = True if request.session.get("username") else False
        return render(request, "reminder/login.html", {"logged_in": logged_in})

    def post(self, request):
        if request.POST.get("logout"):
            del request.session["username"]
            return redirect("login")
        try:
            user = User.objects.get(name=request.POST["name"])
            if user.password == request.POST["password"]:
                request.session["username"] = request.POST["name"]
                return redirect("tasks")
            else:
                return HttpResponse("Wrong password!")
        except:
            return HttpResponse("User not found!")