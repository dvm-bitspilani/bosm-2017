# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-09 18:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0031_participant_bill'),
        ('regsoft', '0004_bill_time_paid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bill',
            name='captain',
        ),
        migrations.AddField(
            model_name='bill',
            name='g_leader',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='registrations.GroupLeader'),
        ),
    ]