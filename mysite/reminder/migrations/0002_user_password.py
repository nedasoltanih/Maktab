# Generated by Django 3.2.18 on 2023-04-27 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reminder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='password',
            field=models.CharField(default='123456', max_length=200),
        ),
    ]