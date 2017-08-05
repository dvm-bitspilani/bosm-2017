from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from events.models import *
from regsoft.models import *

class GroupLeader(models.Model):

	GENDERS = (

			('M', 'MALE'),
			('F', 'FEMALE'),
		)
	
	name = models.CharField(max_length=200)
	college = models.CharField(max_length=100)
	city = models.CharField(max_length=100)
	state = models.CharField(max_length=50)
	phone = models.BigIntegerField()
	email = models.EmailField(unique=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	gender = models.CharField(max_length=10, choices=GENDERS)
	events = models.ManyToManyField(Event, through=Participation, blank=True, null=True) #events.models

	def __unicode__(self):

		return self.name + ' ' + self.college

	class Meta:

		verbose_name_plural = 'Group Leaders'


class TeamCaptain(models.Model):

	name = models.CharField(max_length=200)
	email = models.EmailField(blank=True, null=True)
	email_verified = models.BooleanField(default=False)
	phone = models.BigIntegerField(default=0)
	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	g_l = models.ForeignKey(GroupLeader, on_delete=models.CASCADE, default=None)
	firewallz_passed = models.NullBooleanField('passed firewallz_o', null=True, blank=True)
	acco = models.NullBooleanField('passed recnacc', null=True, blank=True)
	room = models.ForeignKey(Room, null=True, blank=True)
	controlz_paid = models.BooleanField(default=False)
	is_single = models.NullBooleanField()

	def __unicode__(self):

		return self.name + '-' + str(self.g_l.college)

	class Meta:

		verbose_name_plural = 'Team Captains'

class Participant(models.Model):

	name = models.CharField(max_length=200)
	captain = models.ForeignKey(TeamCaptain, on_delete=models.CASCADE)
	firewallz_passed = models.NullBooleanField('passed firewallz_o', null=True, blank=True)
	acco = models.NullBooleanField('passed recnacc', null=True, blank=True)
	room = models.ForeignKey(Room, null=True, blank=True)

	def __unicode__(self):

		return self.name

class Transport(models.Model):

	g_l = models.ForeignKey('GroupLeader', on_delete=models.CASCADE)
	no_of_passengers = models.IntegerField()
	departure = models.CharField(max_length=50)
	arrival = models.CharField(max_length=50)

	def __unicode__(self):

		return str(self.g_l.name)