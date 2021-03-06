# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-19 08:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0020_merge_20170819_1214'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coach',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='teamcaptain',
            name='coach',
        ),
        migrations.AddField(
            model_name='coach',
            name='captain',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='registrations.TeamCaptain'),
        ),
    ]
