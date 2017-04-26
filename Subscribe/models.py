from __future__ import unicode_literals

from django.db import models

class Subscriber(models.Model):

    name = models.CharField(max_length = 50)
    email_address = models.EmailField(unique=True)

    def __unicode__(self):

        return self.name
