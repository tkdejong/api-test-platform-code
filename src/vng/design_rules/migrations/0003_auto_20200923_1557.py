# Generated by Django 2.2.13 on 2020-09-23 13:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('design_rules', '0002_auto_20200923_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='DesignRuleSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('test_result', models.FileField(blank=True, default=None, help_text='The HTML log generated by Newman', null=True, upload_to='', verbose_name='/files/log')),
                ('json_result', models.TextField(blank=True, default=None, help_text='The JSON log generated by Newman', null=True)),
                ('design_rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='design_rules.DesignRule')),
            ],
        ),
        migrations.AddField(
            model_name='designruleresult',
            name='errors',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='designruleresult',
            name='success',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='designruleresult',
            name='design_rule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='design_rules.DesignRuleSession'),
        ),
    ]
