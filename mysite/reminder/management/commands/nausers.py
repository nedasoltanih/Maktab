from django.core.management.base import BaseCommand

from reminder.models import Profile


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in Profile.objects.filter(is_active=False):
            self.stdout.write(self.style.SUCCESS(user.username))
