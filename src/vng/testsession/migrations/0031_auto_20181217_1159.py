# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-17 10:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testsession', '0030_auto_20181217_1136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scenario',
            name='created',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='performed',
        ),
    ]
