# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-19 06:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0018_teamcaptain_captain'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teamcaptain',
            old_name='captain',
            new_name='coach',
        ),
    ]
