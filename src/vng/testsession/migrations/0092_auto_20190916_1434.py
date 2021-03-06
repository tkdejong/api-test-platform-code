# Generated by Django 2.2.4 on 2019-09-16 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testsession', '0091_merge_20190909_0921'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenariocasecollection',
            name='oas_link',
            field=models.URLField(blank=True, help_text='Optional field that takes a URL to an OAS3 schema, automatically generating the scenario cases from this schema. Only works if no scenario cases are set manually', null=True),
        ),
    ]
