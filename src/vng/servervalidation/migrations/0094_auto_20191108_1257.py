# Generated by Django 2.2.4 on 2019-11-08 11:57

from django.db import migrations
from filer.models import File


def migrate_postmantest_validation_files(apps, schema_editor):
    PostmanTest = apps.get_model('servervalidation', 'PostmanTest')
    for postmantest in PostmanTest.objects.all():
        postmantest.validation_file = postmantest._validation_file.file
        postmantest.save()

class Migration(migrations.Migration):

    dependencies = [
        ('servervalidation', '0093_auto_20191108_1255'),
    ]

    operations = [
        migrations.RunPython(migrate_postmantest_validation_files, migrations.RunPython.noop)
    ]
