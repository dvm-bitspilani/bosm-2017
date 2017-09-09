from django import template
from registrations.models import *
from events.models import *
from functools import reduce
register = template.Library()

@register.inclusion_tag('regsoft/show_tags.html')
def show_tags():
	participations = Participation.objects.filter(confirmed=True)
	pcr = 0
	controlz = 0
	for i in participations:
		tcs = TeamCaptain.objects.filter(g_l=i.g_l, event=i.event)
		pcr += reduce((lambda x,y :x+Participant.objects.filter(captain=y).count()), tcs, 0)
	recnacc = Participant.objects.filter(acco=True).count()
	firewallz = Participant.objects.filter(firewallz_passed=True).count()
	controlz = Participant.objects.filter(controlz=True).count()

	return {'pcr':pcr, 'controlz':controlz, 'firewallz':firewallz, 'recnacc':recnacc}

@register.simple_tag
def navbar_color(name):
	username = name
	if 'firewallz' == username:
		return 'cyan'
	if 'controlz' == username:
		return 'light-green'
	if 'recnacc' == username:
		return 'orange'
	else:
		return 'blue'
@register.inclusion_tag('regsoft/tables.html')
def show_tables(tables):
	return {'tables':tables}