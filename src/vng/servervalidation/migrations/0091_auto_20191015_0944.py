# Generated by Django 2.2.4 on 2019-10-15 07:44

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('servervalidation', '0090_auto_20191010_1039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serverrun',
            name='last_exec',
        ),
    ]