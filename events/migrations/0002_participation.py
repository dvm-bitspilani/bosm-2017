# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-02 21:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0004_teamcaptain_is_single'),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmed', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
                ('g_l', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registrations.GroupLeader')),
            ],
        ),
    ]
