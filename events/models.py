from __future__ import unicode_literals

from django.db import models
from registrations.models import *

class Event(models.Model):

	name = models.CharField(max_length=50)
	max_limit = models.IntegerField()
	min_limit = models.IntegerField()
	about = models.CharField(max_length=150, blank=True, null=True)
	start_date = models.CharField(max_length=10,default='TBA')
	end_date = models.CharField(max_length=10,default='TBA')
	venue = models.CharField(max_length=40, default='TBA')

	def __unicode__(self):

		return self.name

class ClubDepartment(models.Model):

	name = models.CharField(max_length=50)

	def __unicode__(self):

		return self.name


class ExtraEvent(models.Model):

	name = models.CharField(max_length=100, unique=True)
	content = models.CharField(max_length=2000)
	start_date = models.CharField(max_length=10,default='TBA')
	end_date = models.CharField(max_length=10,default='TBA')
	venue = models.CharField(max_length=40, default='TBA')
	clubdept = models.ForeignKey(ClubDepartment, default='none')

	def __unicode__(self):

		return self.name

class Participation(models.Model):

	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	g_l = models.ForeignKey('registrations.GroupLeader', on_delete=models.CASCADE)
	confirmed = models.BooleanField(default=False)

	def __unicode__(self):

		return str(self.event.name)+'-'+str(self.g_l.name)