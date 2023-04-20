from django.db.models import Count, Manager


class UserManager(Manager):
    def with_no_tasks(self):
        return self.annotate(tasks=Count('task')).filter(tasks=0)


class TaskManager(Manager):
    def get_user_tasks(self, slug):
        return self.filter(user__slug=slug)

