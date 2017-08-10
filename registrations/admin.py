from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(GroupLeader)
admin.site.register(TeamCaptain)
admin.site.register(Participant)