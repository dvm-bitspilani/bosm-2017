# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-11 07:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0012_auto_20170811_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transport',
            name='date',
            field=models.DateTimeField(null=True, max_length=50),
        ),
    ]
