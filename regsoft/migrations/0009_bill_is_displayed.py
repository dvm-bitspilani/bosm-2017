# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-18 13:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regsoft', '0008_room_capacity'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='is_displayed',
            field=models.BooleanField(default=True),
        ),
    ]
