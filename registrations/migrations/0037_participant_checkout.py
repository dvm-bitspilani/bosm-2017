# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-16 13:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0036_merge_20170910_2329'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='checkout',
            field=models.BooleanField(default=False),
        ),
    ]
