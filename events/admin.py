from django.contrib import admin
from events.models import *

admin.site.register(Event)
admin.site.register(Participation)
admin.site.register(ExtraEvent)
admin.site.register(ClubDepartment)