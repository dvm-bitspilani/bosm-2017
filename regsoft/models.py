from __future__ import unicode_literals

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
