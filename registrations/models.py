from __future__ import unicode_literals
from datetime import datetime
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
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user')
	gender = models.CharField(max_length=10, choices=GENDERS)
	events = models.ManyToManyField(Event, through=Participation, blank=True, null=True) #events.models
	email_verified = models.BooleanField(default=False)
	email_token = models.CharField(max_length=32, null=True, blank=True)
	pcr_approved = models.BooleanField(default=False)
	barcode = models.CharField(max_length=50, null=True)
	
	def __unicode__(self):

		return self.name + ' ' + self.college

	class Meta:

		verbose_name_plural = 'Group Leaders'


class TeamCaptain(models.Model):

	GENDERS = (

			('M', 'MALE'),
			('F', 'FEMALE'),
	)

	name = models.CharField(max_length=200)
	email = models.EmailField(blank=True, null=True)
	phone = models.BigIntegerField(default=0)
	event = models.ForeignKey(Event, on_delete=models.CASCADE, default=None)
	g_l = models.ForeignKey(GroupLeader, on_delete=models.CASCADE, default=None)
	firewallz_passed = models.NullBooleanField('passed firewallz_o', null=True, blank=True)
	acco = models.NullBooleanField('passed recnacc', null=True, blank=True)
	coach = models.CharField(max_length=200, null=True, default='')
	room = models.ForeignKey(Room, null=True, blank=True)
	paid = models.BooleanField(default=False)
	is_single = models.NullBooleanField()
	total_players = models.IntegerField(default=1)
	gender = models.CharField(max_length=10, choices=GENDERS, null=True)	
	payment_token = models.CharField(max_length=32, null=True, blank=True)
	order_id = models.CharField(max_length=10, null=True, blank=True)
	if_payment = models.BooleanField(default=True)
	payment = models.IntegerField(default=0)
	is_extra = models.BooleanField(default=False)
	extra_id = models.IntegerField(default=0)

	def __unicode__(self):

		return self.name + '-' + str(self.g_l.college)

	class Meta:

		verbose_name_plural = 'Team Captains'

class Participant(models.Model):

	name = models.CharField(max_length=200)
	captain = models.ForeignKey(TeamCaptain, on_delete=models.CASCADE)
	firewallz_passed = models.BooleanField('passed firewallz_o', default=False)
	acco = models.BooleanField('passed recnacc', default=False)
	room = models.ForeignKey(Room, null=True, blank=True)
	controlz = models.BooleanField('controlz passed', default=False)
	def __unicode__(self):

		return self.name

class Transport(models.Model):

	g_l = models.ForeignKey('GroupLeader', on_delete=models.CASCADE)
	no_of_passengers = models.IntegerField()
	departure = models.CharField(max_length=50)
	date = models.DateTimeField(max_length=50, auto_now=False, null=True)

	def __unicode__(self):

		return str(self.g_l.name)

# class Coach(models.Model):

# 	name = models.CharField(max_length=100)
# 	captain = models.OneToOneField(TeamCaptain, on_delete=models.CASCADE)