# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-14 14:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0016_teamcaptain_pcr_email_sent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teamcaptain',
            name='pcr_email_sent',
        ),
    ]