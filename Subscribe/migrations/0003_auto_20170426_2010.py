# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-26 20:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Subscribe', '0002_auto_20170426_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='email_address',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
