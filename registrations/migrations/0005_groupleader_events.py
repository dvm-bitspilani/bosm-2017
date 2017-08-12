# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-02 21:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_participation'),
        ('registrations', '0004_teamcaptain_is_single'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupleader',
            name='events',
            field=models.ManyToManyField(blank=True, null=True, through='events.Participation', to='events.Event'),
        ),
    ]