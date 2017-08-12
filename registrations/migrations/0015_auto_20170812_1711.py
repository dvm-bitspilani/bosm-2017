# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-12 11:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0014_auto_20170811_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupleader',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
    ]