# Generated by Django 2.2.1 on 2019-07-03 10:47

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('servervalidation', '0065_merge_20190621_0817'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='testscenario',
            options={'ordering': ('name',)},
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='server_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servervalidation.ServerRun'),
        ),
        migrations.AlterField(
            model_name='postmantestresult',
            name='server_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servervalidation.ServerRun'),
        ),
        migrations.AlterField(
            model_name='serverheader',
            name='server_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servervalidation.ServerRun'),
        ),
        migrations.AlterField(
            model_name='serverrun',
            name='last_exec',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last run'),
        ),
        migrations.AlterField(
            model_name='serverrun',
            name='started',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Started at'),
        ),
        migrations.AlterField(
            model_name='serverrun',
            name='stopped',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Stopped at'),
        ),
        migrations.AlterField(
            model_name='testscenario',
            name='authorization',
            field=models.CharField(choices=[('JWT', 'jwt'), ('Authorization header', 'header'), ('No Authorization', 'no auth')], default='JWT', max_length=20, verbose_name='Authorization'),
        ),
        migrations.AlterField(
            model_name='testscenario',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='testscenariourl',
            name='name',
            field=models.CharField(max_length=200, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='testscenariourl',
            name='url',
            field=models.BooleanField(default=True, help_text='When enabled a single-line field is shown to the user\n    when starting a session. When disabled a multi-line field is shown.'),
        ),
    ]
