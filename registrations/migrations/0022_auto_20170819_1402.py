# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-19 08:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0021_auto_20170819_1352'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coach',
            name='captain',
        ),
        migrations.AddField(
            model_name='teamcaptain',
            name='coach',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.DeleteModel(
            name='Coach',
        ),
    ]