from django.db import models
from django.utils.text import slugify
import datetime
from django.core.validators import URLValidator, validate_email
from .managers import UserManager, TaskManager


def email_list(value):
    emails = value.split(',')
    for email in emails:
        validate_email(email)


class User(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='User Name')
    image = models.ImageField(null=True, upload_to="profile_img")
    slug = models.SlugField(max_length=200, null=True, blank=True, editable=False)
    # email = models.EmailField(max_length=200, null=True)
    email = models.CharField(max_length=500, null=True, validators=[email_list])
    website = models.CharField(max_length=300, null=True, validators=[URLValidator(schemes=['http','https'])])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    objects = UserManager()


class GoldUser(User):
    score = models.IntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(score__gte=5), name='score_gte_5'),
        ]


class Task(models.Model):
    categories = [
        ('p', 'Personal'),
        ('w', 'Work'),
        ('s', 'Sport'),
        ('h', 'Hobby')
    ]

    title = models.CharField(max_length=100, help_text='Must be unique')
    due_date = models.DateField(null=True)
    hour = models.TimeField(default="12:00:00")
    category = models.CharField(choices=categories, max_length=1, null=True)
    done = models.BooleanField(null=True)
    user = models.ForeignKey(User, to_field="name", null=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.title.lower() == "gym":
            self.category = 's'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title + " " + str(self.due_date)

    def is_due_date_passed(self):
        now = datetime.date.today()
        return self.due_date < now

    class Meta:
        db_table = 'deeds'
        ordering = ['title']

    @property
    def full_title(self):
        return f"{self.category} {self.title}"

    objects = TaskManager()


class HWTask(Task):
    class Meta:
        proxy = True
        verbose_name = 'Home Work'

    def save(self, *args, **kwargs):
        self.title = self.title + ",Home work"
        super().save(*args, **kwargs)
