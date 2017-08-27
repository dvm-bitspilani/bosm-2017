from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from registrations import views, urls
from events.models import *
from django.shortcuts import render, redirect, get_object_or_404
from registrations.models import *
import barg
from functools import reduce

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
def gen_barcode(gl_id):
	try:
		try:
			g_l = GroupLeader.objects.get(id=gl_id)
			encoded = g_l.barcode
		except ObjectDoesNotExist:
			return None
		encoded = ""+encoded
	except:
		gl_ida = "%04d" % int(gl_id)
		mixed = string.ascii_uppercase + string.ascii_lowercase
		encoded = ''.join([x+mixed[randint(0,51)] for x in gl_ida])
		g_l.barcode = encoded
		g_l.save()
	try:
		image='/home/dvm/bosm/public_html/bosm2017/barcodes/%s.gif' % str(gl_id)
	except:
		image = '~/barcodes/%s.gif' % str(gl_id)
	barg.code128_image(encoded).save(image)
	return encoded


@staff_member_required
def recnacc_home(request):
	g_ls = GroupLeader.objects.filter(pcr_approved=True)
	rows = [{'data':[g_l.college, count_players(g_l)], 'link':[{'title':'Allot', 'url':reverse('regsoft:allot_room', kwargs={'gl_id':g_l.id})}]} for g_l in g_ls if count_players(g_l)!=0]
	headings = ['College', 'No. of Participants', 'Allot']
	tables = [{'title':'Select College to allot rooms', 'rows':rows, 'headings':headings}]
	return render(request,'regsoft/tables.html' {'tables':tables})


def count_players(g_l):
	tcs = TeamCaptain.objects.filter(g_l=g_l, if_payment=True, firewall=True)
	sum=0
	for tc in tcs:
		sum+=tc.total_players
	return sum

@staff_member_required
def allot_room(request, gl_id):
	g_l = get_object_or_404(GroupLeader, id=gl_id)
	if request.POST:
		data = request.POST
		
		if 'allocate' in data['submit']:
			tcs_id = dict(data)['allocate']
			room_id = data['room']
			if not tcs_id and not room_id:
				return redirect(request.META.get('HTTP_REFERER'))
			room = Room.objects.get(id=room_id)
			count = 0
			for tc_id in tcs_id:
				count += get_object_or_404(TeamCaptain, id=tc_id).total_players
			if total_players > room.vacancy:
				return redirect(request.META.get('HTTP_REFERER'))

			rows = []
			for tc_id in tcs_id:
				tc = TeamCaptain.objects.get(id=tc_id)
				tc.room = room
				tc.save()
				room.vacancy -= tc.total_players
				room.save()
				rows.append({'data':[tc.name, tc.gender, tc.g_l.college, tc.phone, room.room, room.bhavan.name], 'link':[]})
			headings = ['Name', 'Gender', 'College', 'Phone', 'Room', 'Bhavan']
			title = 'Teams alloted Room just now'
			tables = [{'title':title, 'headings':headings, 'rows':rows}]
			return render(request, 'regsoft/tables.html', {'tables':tables})
		
		if 'deallocate' in data['submit']:
			tcs_id = dict(data)['deallocate']

			if not tcs_id:
				return redirect(request.META.get('HTTP_REFERER'))

			for tc_id in tcs_id:
				tc = get_object_or_404(TeamCaptain, id=tc_id)
				room = tc.room
				room.vacancy += tc.total_players
				room.save()
				tc.room = None
				tc.save()
			return redirect(reverse('regsoft:allot_room', kwargs={'gl_id':g_l.id}))


	rows1 = [{'tc':tc, 'event':tc.event.name}  for tc in TeamCaptain.objects.filter(g_l=g_l, if_payment=True, firewall=True, room=None)]
	rows2 = [{'tc':tc, 'event':tc.event.name}  for tc in TeamCaptain.objects.filter(g_l=g_l, if_payment=True, firewall=True).exclude(room=None)]

	rooms = Room.objects.exclude(vacancy=0)
	return render(request, 'regsoft/allot_room.html', {'allocate':rows1, 'deallocate':rows2, 'rooms':rooms})


@staff_member_required
def main_list(request):
	TeamCaptain.objects.filter()

def controlz_home(request):
	if request.method == 'POST':
		try:
			barcode = request.POST['code']
			g_leader = GroupLeader.objects.get(id=barcode[::2])

		except:
			return render(request, 'registrations/message.html', {'message':'Group Leader with the given barcode does not exist.'})

		
