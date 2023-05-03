from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
import datetime
from django.core.validators import URLValidator, validate_email
from .managers import UserManager, TaskManager
from django.contrib.auth.models import User as DjangoUser, PermissionsMixin


def email_list(value):
    emails = value.split(',')
    for email in emails:
        validate_email(email)


class Profile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email address', unique=True)
    username = models.CharField('username', unique=True, max_length=100)
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    date_joined = models.DateTimeField('date joined', auto_now_add=True)
    is_active = models.BooleanField('active', default=True)
    is_staff = models.BooleanField('staff', default=True)

    image = models.ImageField(null=True, upload_to="profile_img")
    slug = models.SlugField(max_length=200, null=True, blank=True, editable=False)
    website = models.CharField(max_length=300, null=True, validators=[URLValidator(schemes=['http', 'https'])])

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name


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
    user = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)

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
