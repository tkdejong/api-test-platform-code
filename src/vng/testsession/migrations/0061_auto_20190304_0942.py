# Generated by Django 2.2a1 on 2019-03-04 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testsession', '0060_auto_20190304_0930'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='error_message',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='status',
            field=models.CharField(choices=[('starting', 'starting'), ('running', 'running'), ('shutting down', 'shutting down'), ('stopped', 'stopped'), ('Error deployment', 'error deploy')], default='starting', max_length=20),
        ),
    ]
