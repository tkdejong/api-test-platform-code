# Generated by Django 2.2.13 on 2020-11-11 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('design_rules', '0015_auto_20201106_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='designruletestversion',
            name='url',
            field=models.URLField(null=True),
        ),
        migrations.AlterField(
            model_name='designruletestoption',
            name='rule_type',
            field=models.CharField(blank=True, choices=[('api_03', 'API-03: Only apply default HTTP operations'), ('api_09', 'API-09: Implement custom representation if supported'), ('api_16', 'API-16: Use OAS 3.0 for documentation'), ('api_20', 'API-20: Include the major version number only in ihe URI'), ('api_48', 'API-48: Leave off trailing slashes from API endpoints'), ('api_51', 'API-51: Publish OAS at the base-URI in JSON-format')], default='', max_length=50),
        ),
    ]
