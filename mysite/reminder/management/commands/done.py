from django.core.management.base import BaseCommand, CommandError

from reminder.models import Task


class Command(BaseCommand):
    help = "Marks tasks as done"
    missing_args_message = 'You must include task slugs'

    def create_parser(self, prog_name, subcommand, **kwargs):
        parser = super().create_parser(prog_name, subcommand, **kwargs)
        parser.epilog = 'Call this command for your tasks!'
        return parser

    def add_arguments(self, parser):
        parser.add_argument("task_slugs", nargs="+", type=str, help='Add task slugs separated by space')
        parser.add_argument("-a", "--all", action='store_true')
        parser.add_argument("-s", "--suppress", action='store_false')
        parser.add_argument("-u", "--undone", action='store_true')

    def handle(self, *args, **options):
        if options["all"]:
            for task in Task.objects.all():
                task.done = False if options['undone'] else True
                task.save()
                self.stdout.write(self.style.SUCCESS('Successfully marked task %s done as %s' % (task.slug, task.done)))

        else:
            for task_slug in options["task_slugs"]:
                try:
                    task = Task.objects.get(slug=task_slug)
                    task.done = False if options['undone'] else True
                    task.save()
                    self.stdout.write(self.style.SUCCESS('Successfully marked task %s done as %s' % (task_slug, task.done)))

                except Task.DoesNotExist:
                    if options["suppress"]:
                        self.stderr.write(self.style.ERROR('Task %s does not exist'% task_slug))
                    # raise CommandError('Task %s does not exist'% task_slug)




