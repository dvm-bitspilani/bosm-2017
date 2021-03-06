# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-02 19:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regsoft', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('registrations', '0002_auto_20170802_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupLeader',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('college', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=50)),
                ('phone', models.BigIntegerField()),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('gender', models.CharField(choices=[('M', 'MALE'), ('F', 'FEMALE')], max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Group Leaders',
            },
        ),
        migrations.RemoveField(
            model_name='teamcaptain',
            name='city',
        ),
        migrations.RemoveField(
            model_name='teamcaptain',
            name='coach',
        ),
        migrations.RemoveField(
            model_name='teamcaptain',
            name='college',
        ),
        migrations.RemoveField(
            model_name='teamcaptain',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='teamcaptain',
            name='state',
        ),
        migrations.RemoveField(
            model_name='teamcaptain',
            name='user',
        ),
        migrations.AddField(
            model_name='participant',
            name='firewallz_passed',
            field=models.NullBooleanField(verbose_name='passed firewallz_o'),
        ),
        migrations.AddField(
            model_name='teamcaptain',
            name='acco',
            field=models.NullBooleanField(verbose_name='passed recnacc'),
        ),
        migrations.AddField(
            model_name='teamcaptain',
            name='firewallz_passed',
            field=models.NullBooleanField(verbose_name='passed firewallz_o'),
        ),
        migrations.AddField(
            model_name='teamcaptain',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='regsoft.Room'),
        ),
        migrations.AlterField(
            model_name='teamcaptain',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='teamcaptain',
            name='g_l',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='registrations.GroupLeader'),
        ),
    ]
