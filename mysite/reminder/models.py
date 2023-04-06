from django.db import models
from django.utils.text import slugify
import datetime


class User(models.Model):
    name = models.CharField(max_length=200, unique=True)
    image = models.ImageField(null=True, upload_to="profile_img")
    slug = models.SlugField(max_length=200, null=True, blank=True, editable=False)
    email = models.EmailField(max_length=200, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Task(models.Model):
    title = models.CharField(max_length=100, primary_key=True, help_text='Must be unique')
    due_date = models.DateField(null=True)
    hour = models.TimeField(default="12:00:00")
    category = models.CharField(choices=[
        ('p', 'Personal'),
        ('w', 'Work'),
        ('s', 'Sport'),
        ('h', 'Hobby')
    ], max_length=1, null=True)
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