# Generated by Django 3.1.1 on 2023-04-06 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reminder', '0011_delete_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]
