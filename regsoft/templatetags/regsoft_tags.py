from django import template
from registrations.models import *
from events.models import *
from functools import reduce
register = template.Libarary()

@register.inclusion_tag('regsoft/show_tags.html')
def show_tags():
	participations = Participation.objects.filter(confirmed=True)
	pcr = 0
	controlz = 0
	for i in participations:
		tcs = TeamCaptain.objects.filter(g_l=i.g_l, event=i.event)
		pcr += reduce((lambda x,y :x+Participant.objects.filter(captain=y).count()), tcs, 0)
		tcs_paid = tcs.filter(paid=True)
		controlz += reduce((lambda x,y:Participant.objects.filter(captain=y).count()), tcs_paid, 0)
	recnacc = Participant.objects.filter(acco=True).count()
	firewallz = Participant.objects.filter(firewallz_passed=True).count()

	return {'pcr':pcr, 'controlz':controlz, 'firewallz':firewallz, 'recnacc':recnacc}

@register.simple_tag
def navbar_color():
	username = request.user.username
	if request.user.is_superuser:
		return 'black'
	if 'firewallz' in username:
		return 'blue'
	if 'controlz' in username:
		return 'green'
	if 'recnacc' in username:
		return 'orange'