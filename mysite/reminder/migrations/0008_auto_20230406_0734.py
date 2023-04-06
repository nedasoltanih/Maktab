# Generated by Django 3.1.1 on 2023-04-06 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reminder', '0007_auto_20230406_0730'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='user',
        ),
        migrations.AddField(
            model_name='task',
            name='user',
            field=models.ManyToManyField(to='reminder.User'),
        ),
    ]