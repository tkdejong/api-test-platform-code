# Generated by Django 2.2.4 on 2019-11-08 11:55

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('servervalidation', '0092_auto_20191108_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='postmantest',
            name='validation_file',
            field=models.FileField(blank=True, default=None, help_text='The actual file containing the Postman collection', null=True, upload_to=''),
        ),
    ]
