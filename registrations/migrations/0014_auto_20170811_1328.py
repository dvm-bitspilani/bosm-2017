# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-11 07:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0013_auto_20170811_1309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transport',
            name='date',
            field=models.DateTimeField(max_length=50, null=True),
        ),
    ]
