import datetime

from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, Http404
from django.utils import timezone
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.base import View, TemplateView, RedirectView
from django.core.paginator import Paginator
from django.contrib.auth.models import User as DjangoUser

from mysite import settings
from .forms import TaskForm, TaskModelForm, UserForm
from .models import Task, Profile
from django.db.models import Count
from django.contrib import messages
import logging

logger = logging.getLogger("django")


def tasks_view(request, num):
    if request.user.is_authenticated:
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
    else:
        return redirect("login")


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    template_name = "reminder/tasks.html"
    context_object_name = "tasks"
    paginate_by = 4
    login_url = "/reminder/login/"

    def get(self, request):
        last_login = request.COOKIES.get("last_login")
        user = Profile.objects.get(username=request.user)
        tasks = Task.objects.filter(user=user)
        paginator = Paginator(tasks, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        response = render(request, 'reminder/tasks.html',
                          {'page_obj': page_obj, 'tasks': tasks, 'last_login': last_login})
        response.set_cookie("last_login", datetime.datetime.now())
        return response

    def post(self, request):
        request.session['color'] = request.POST["color"]
        if request.POST.get("delete", ""):
            for task in Task.objects.all():
                if str(task.pk) in request.POST.keys():
                    Task.objects.get(pk=task.pk).delete()
                    messages.success(request, "Task %s deleted successfully" % task.slug, extra_tags="delete")
            return HttpResponseRedirect("/reminder/success/")


@login_required(login_url='/reminder/login/')
def task_detail(request, id):
    task = Task.objects.get(pk=id)
    return render(request, 'reminder/task_detail.html', {'task': task})


class TaskDetail(DetailView):
    model = Task

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except:
            logger.error("task not found")
            raise Http404("task not found")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(name=context['task'].user.name)
        if context['task'].due_date > timezone.now().date():
            context['days_left'] = context['task'].due_date - timezone.now().date()
        return context

    def post(self, request, pk):
        task = Task.objects.get(pk=pk)
        task.delete()
        return HttpResponse("Success!")


def one_user_tasks(request, slug):
    # name = Profile.objects.get(slug=slug)
    # tasks = Task.objects.filter(user=name)
    tasks = Task.objects.get_user_tasks(slug)
    return render(request, 'reminder/user_tasks.html', {'tasks': tasks})


def users_view(request):
    users = Profile.objects.all()
    last_login = request.COOKIES.get("last_login")
    return render(request, 'reminder/users.html', {'users': users, 'last_login': last_login})


class UserList(ListView):
    model = Profile
    context_object_name = "users"
    template_name = "reminder/users.html"

    def get_queryset(self):
        users = Profile.objects.all()
        for user in users:
            user.undone_tasks = len(Task.objects.filter(user=user, done=False))
        return users

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data()
    #     context['num_users'] = len(context['users'])
    #     for user in context['users']:
    #         context[user.name] = len(Task.objects.filter(user=user).filter(done=False))
    #     return context


@login_required(login_url="/reminder/login/")
def one_user(request, slug):
    user = Profile.objects.filter(slug=slug)
    if not user:
        return HttpResponseNotFound('<h1>Profile not found</h1>')
    return HttpResponse(user[0].name)


def user_with_notasks(request):
    # users = Profile.objects.all()
    # fusers = []
    # for user in users:
    #     if not Task.objects.filter(user=user.name):
    #         fusers.append(user)

    fusers = Profile.objects.annotate(tasks=Count('task')).filter(tasks=0)

    # fusers = []
    # tasks = Task.objects.all().values('user')
    # users = Profile.objects.all()
    # for user in users:
    #     if user.name not in  tasks:
    #         fusers.append(user)

    return render(request, 'reminder/users.html', {'users': fusers})


@permission_required('reminder.add_task', login_url='/reminder/login/', raise_exception=True)
def new_task(request):
    if request.method == "GET":
        users = Profile.objects.all()
        return render(request, "reminder/new_task.html", context={'users': users, 'categories': Task.categories})
    elif request.method == "POST":
        user = Profile.objects.get(name=request.POST["user"])
        done = True if "done" in request.POST.keys() else False
        print(request.POST)
        task = Task(title=request.POST["title"], due_date=request.POST["due_date"]
                    , category=request.POST["category"], done=done, hour=request.POST["hour"], user=user)
        task.save()
        return HttpResponse("Saved!")


class NewTask(PermissionRequiredMixin, View):
    permission_required = 'reminder.add_task'
    login_url = '/reminder/login/'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        users = Profile.objects.all()
        if "id" in request.GET.keys():
            task = Task.objects.get(pk=request.GET["id"])
            return render(request, "reminder/new_task.html", context={'users': users,
                                                                      'categories': Task.categories,
                                                                      'task': task})
        else:
            return render(request, "reminder/new_task.html", context={'users': users, 'categories': Task.categories})

    def post(self, request, *args, **kwargs):
        # if request.user.has_perm('reminder.add_task'):
        user = Profile.objects.get(name=request.POST["user"])
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
    # else:
    #     return HttpResponse("You dont have permission to do that!")


class UsersNoTask(View):
    def get(self, request, *args, **kwargs):
        # fusers = Profile.objects.annotate(tasks=Count('task')).filter(tasks=0)
        fusers = Profile.objects.with_no_tasks()
        return render(request, 'reminder/users.html', {'users': fusers})


class BaseView(TemplateView):
    template_name = "reminder/base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['objects'] = Task.objects.filter(due_date__gte=timezone.now().date()).order_by('due_date')[:3]
        return context


# class RedirView(RedirectView):
#     pattern_name = "index"


class UserTasks(LoginRequiredMixin, ListView):
    login_url = '/reminder/login/'
    redirect_field_name = 'next'
    context_object_name = "tasks"
    template_name = "reminder/tasks.html"

    def get_queryset(self):
        self.user = get_object_or_404(Profile, slug=self.kwargs['slug'])
        return Task.objects.filter(user=self.user)


class UsersRedir(RedirectView):
    pattern_name = 'users'


class LoginView(View):

    def get(self, request):
        return render(request, "reminder/login.html")

    def post(self, request):
        next_url = request.GET.get("next", "tasks")
        if request.POST.get("logout"):
            logout(request)
            return redirect("login")
        user = authenticate(username=request.POST["username"], password=request.POST["password"])
        if user:
            if user.is_active:
                login(request, user)
                return redirect(next_url)
            else:
                return HttpResponse("Profile is not active!")
        else:
            return HttpResponse("Username or password is wrong!")


class Register(View):
    def get(self, request):
        return render(request, "reminder/register.html")

    def post(self, request):
        dj_user = DjangoUser.objects.create_user(request.POST["username"],
                                                 request.POST["email"],
                                                 request.POST["password"],
                                                 first_name=request.POST["name"],
                                                 last_name=request.POST["lname"], )
        dj_user.save()
        user = Profile(username=request.POST["name"], website=request.POST["website"])
        user.save()
        return HttpResponse("Success!")


class NewTaskForm(View):
    def get(self, request):
        form = TaskForm()
        return render(request, "reminder/new_task_2.html", {'form': form})

    def post(self, request):
        form = TaskForm(request.POST)
        if form.is_valid():
            task = Task(title=form.cleaned_data.get("title"), due_date=form.cleaned_data.get("due_date"),
                        hour=form.cleaned_data.get("time"))
            task.save()
            return HttpResponse("Success!")
        else:
            return render(request, "reminder/new_task_2.html", {'form': form})


class NewTaskModelForm(View):
    def get(self, request):
        form = TaskModelForm()
        return render(request, "reminder/new_task_2.html", {'form': form})

    def post(self, request):
        form = TaskModelForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/reminder/success/")
        else:
            return render(request, "reminder/new_task_2.html", {'form': form})


class TaskFormView(FormView):
    form_class = TaskForm
    template_name = "reminder/new_task_2.html"
    success_url = "/reminder/success/"

    def post(self, request):
        form = TaskForm(request.POST)
        if form.is_valid():
            task = Task(title=form.cleaned_data.get("title"), due_date=form.cleaned_data.get("due_date"),
                        hour=form.cleaned_data.get("time"))
            task.save()

            try:
                send_mail(subject="Task created",
                          message="a task is created with id %d" % task.id,
                          from_email=settings.EMAIL_HOST_USER,
                          recipient_list=[settings.RECIPIENT_ADDRESS])
            except:
                pass

            messages.success(request, "Task created successfully")
            return HttpResponseRedirect("/reminder/success/")
        else:
            return render(request, "reminder/new_task_2.html", {'form': form})


class SuccessView(TemplateView):
    template_name = "reminder/success.html"


class UserRegisterView(FormView):
    form_class = UserForm
    template_name = "reminder/signup.html"
    success_url = "/reminder/success/"
    console_logger = logging.getLogger("console_logger")

    def post(self, request, *args, **kwargs):
        # messages.set_level(request, messages.WARNING)
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully", extra_tags="add")
            # m = messages.get_messages(request)
            # for message in m:
            #     print(message)
            # m.used = False
            return HttpResponseRedirect("/reminder/success/")
        else:
            self.console_logger.warning("some errors in form")
            return render(request, "reminder/signup.html", {'form': form})
