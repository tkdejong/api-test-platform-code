# Generated by Django 2.2.4 on 2019-09-26 14:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('servervalidation', '0085_auto_20190926_1201'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='environment',
            unique_together={('name', 'test_scenario', 'user')},
        ),
    ]
