# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-05 15:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0006_teamcaptain_phone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teamcaptain',
            name='email_verified',
        ),
        migrations.AddField(
            model_name='groupleader',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='groupleader',
            name='pcr_approved',
            field=models.BooleanField(default=False),
        ),
    ]
