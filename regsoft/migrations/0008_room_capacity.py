# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-15 12:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regsoft', '0007_bill_coaches_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='capacity',
            field=models.IntegerField(default=0),
        ),
    ]
