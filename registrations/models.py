from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from events.models import *
from regsoft.models import *

class TeamCaptain(models.Model):

	GENDERS = (

			('M', 'MALE'),
			('F', 'FEMALE'),
		)
	
	name = models.CharField(max_length=200)
	college = models.CharField(max_length=200)
	city = models.CharField(max_length=100)
	state = models.CharField(max_length=50)
	phone = models.BigIntegerField()
	email = models.EmailField(unique=True)
	email_verified = models.BooleanField(default=False)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	controlz_paid = models.BooleanField(default=False)
	coach = models.CharField(max_length=200)
	
	def __unicode__(self):

		return self.name + ' ' + self.college

	class Meta:

		verbose_name_plural = 'Team Captains'

class Participant(models.Model):

	name = models.CharField(max_length=200)
	captain = models.ForeignKey(TeamCaptain, on_delete=models.CASCADE)
	acco = models.NullBooleanField('passed recnacc', null=True, blank=True)
	room = models.ForeignKey(Room, null=True, blank=True)

	def __unicode__(self):

		return self.name