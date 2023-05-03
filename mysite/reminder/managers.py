from django.db.models import Count, Manager
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import UserManager


class UserManager(UserManager, BaseUserManager):
    def with_no_tasks(self):
        return self.annotate(tasks=Count('task')).filter(tasks=0)


class TaskManager(Manager):
    def get_user_tasks(self, slug):
        return self.filter(user__slug=slug)

    def get_passed_tasks(self):
        return self.filter(due_date__lte=timezone.now().date())

    def get_done_tasks(self):
        return self.filter(done=True)

    def get_not_done_tasks(self):
        return self.filter(done=False)
