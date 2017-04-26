from __future__ import unicode_literals

from django.db import models

class Subscriber(models.Model):

    name = models.CharField(max_length = 50)
    email_address = models.EmailField(unique=True)
    mobile_number = models.CharField(default='' , blank = False, max_length=13)

    def __unicode__(self):

        return self.name
