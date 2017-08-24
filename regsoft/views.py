from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from registrations.models import *
from registrations import views, urls
from events.models import *

@staff_member_required
def index(request):
	if request.user.username.lower() == 'firewallz':
		return redirect(reverse('regsoft:firewallz-home'))
	elif request.user.username.lower() == 'recnacc':
		return redirect(reverse('regsoft:recnacc-home'))
	elif request.user.username.lower() == 'controlz':
		return redirect(reverse('regsoft:controlz-home'))
	elif request.user.username.lower() == 'firewallzi':
		return redirect(reverse('regsoft:firewallzi-home'))
	else:
		return render(request, 'registrations/messsage.html', {'messsage':'Access denied.'})

@staff_member_required
def controlz_home(request):
	if request.method == 'POST':
		try:
			barcode = request.POST['code']
			g_leader = GroupLeader.objects.get(id=barcode[::2])

		except:
			return render(request, 'registrations/message.html', {'message':'Group Leader with the given barcode does not exist.'})

		