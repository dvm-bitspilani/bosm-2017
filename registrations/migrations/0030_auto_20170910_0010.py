# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-09 18:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0029_merge_20170907_1422'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='barcode',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='teamcaptain',
            name='barcode',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
