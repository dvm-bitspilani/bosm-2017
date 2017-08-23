from __future__ import unicode_literals
from registrations.models import *
from django.db import models

class Bhavan(models.Model):

	name = models.CharField(max_length=30)

	def __unicode__(self):

		return self.name

class Room(models.Model):

	bhavan = models.ForeignKey(Bhavan, on_delete=models.CASCADE)
	room = models.CharField(max_length=30)
	vacancy = models.IntegerField()

	def __unicode__(self):

		return self.room + '-' + str(self.bhavan.name)

class Bill(models.Model):

	captain = models.ForeignKey('registrations.TeamCaptain', on_delete=models.CASCADE)
	amount = models.IntegerField()
	two_thousands = models.IntegerField(null=True, blank=True, default=0)
	five_hundreds = models.IntegerField(null=True, blank=True, default=0)
	hundreds = models.IntegerField(null=True, blank=True, default=0)
	fifties = models.IntegerField(null=True, blank=True, default=0)
	twenties = models.IntegerField(null=True, blank=True, default=0)
	tens = models.IntegerField(null=True, blank=True, default=0)
	draft_number = models.CharField(max_length=100, null=True, blank=True, default=None)
	draft_amount = models.IntegerField(null=True, blank=True, default=0)

	def __unicode__(self):
		return str(self.captain.g_l.college) + ' - ' + str(self.captain.name) + ' - ' + str(self.captain.event.name) + ' - ' + str(self.amount)