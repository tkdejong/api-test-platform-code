# Generated by Django 2.2.13 on 2020-11-04 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('design_rules', '0010_remove_designruletestsuite_api'),
    ]

    operations = [
        migrations.CreateModel(
            name='DesignRuleTestOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
                ('rule_type', models.CharField(choices=[('api_03', 'API-03: Only apply default HTTP operations'), ('api_09', 'API-09: Implement custom representation if supported'), ('api_16', 'API-16: Use OAS 3.0 for documentation'), ('api_20', 'API-20: Include the major version number only in ihe URI'), ('api_48', 'API-48: Leave off trailing slashes from API endpoints'), ('api_51', 'API-51: Publish OAS at the base-URI in JSON-format')], default='', max_length=50)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DesignRuleTestVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(default='', max_length=200)),
                ('name', models.CharField(default='', max_length=200)),
            ],
        ),
    ]