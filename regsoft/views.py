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
	rows = [{'data':[g_l.college, count_players(g_l)], 'link':[{'title':'Allot', 'url':reverse('regsoft:recnacc-college', kwargs={'gl_id':g_l.id})}]} for g_l in g_ls if count_players(g_l)!=0]
	headings = ['College', 'No. of Participants', 'Allot']
	tables = [{'title':'Select College to allot rooms', 'rows':rows, 'headings':headings}]
	return render(request,'regsoft/tables.html' {'tables':tables})


@staff_member_required
def recnacc_college(request, gl_id):
	g_l = GroupLeader.objects.get(id=gl_id)
	rows = [{'data':[tc.name, tc.event.name, tc.g_l.college, tc.total_players], 'link':[{'title':'Allot', 'url':reverse('regsoft:recnacc-team', kwargs={'tc_id':tc.id})}]} for tc in TeamCaptain.objects.filter(firewallz_passed=True, g_l=g_l, if_payment=True)]
	headings = ['Team Captain', 'Event', 'College', 'No. of Players', 'Select']
	tables = [{'title':'Select Team', 'rows':rows, 'headings':headings}]
	return render(request,'regsoft/tables.html' {'tables':tables})


@staff_member_required
def recnacc_team(request, tc_id):
	tc = TeamCaptain.objects.get(id=tc_id)
	rooms = [{'room':room.room, 'id':room.id, 'vacancy':room.vacancy} for room in Room.objects.all()]
	parts1 = Participant.objects.filter(captain=tc, acco=True)
	parts2 = Participant.objects.filter(captain=tc, acco=False)
	return render(request, 'regsoft/allot.html', {'allotted':parts1, 'Unallotted':parts2, 'rooms':rooms})



def count_players(g_l):
	tcs = TeamCaptain.objects.filter(g_l=g_l, if_payment=True, firewallz_passed=True)
	sum=0
	for tc in tcs:
		sum+=tc.total_players
	return sum

@staff_member_required
def recnacc_change(request):
	
	if request.POST:
		data = request.POST
		
		if 'allocate' in data['submit']:
			try:
				parts_id = dict(data)['allocate']
				room_id = data['room']
				room = Room.objects.get(id=room_id)
				if len(parts_id) > room.vacancy:
					raise KeyError
			except:
				return redirect(request.META.get('HTTP_REFERER'))
				
			rows = []
			tc = Participant.objects.get(id=parts_id[0]).captain
			tc.room =room
			tc.save()
			room.vacancy -= len(parts_id)
			room.save()
			for part_id in parts_id:
				part = Participant.objects.get(id=part_id)
				part.acco = True
				part.save()
				# rows.append({'data':[tc.name, tc.gender, tc.g_l.college, tc.phone, room.room, room.bhavan.name], 'link':[]})
			# headings = ['Name', 'Gender', 'College', 'Phone', 'Room', 'Bhavan']
			# title = 'Teams alloted Room just now'
			# tables = [{'title':title, 'headings':headings, 'rows':rows}]
			# return render(request, 'regsoft/tables.html', {'tables':tables})
			gl_id = tc.g_l.id
		

		if 'deallocate' in data['submit']:
			try:
				parts_id = dict(data)['deallocate']
			except:
				return redirect(request.META.get('HTTP_REFERER'))
			tc = Participant.objects.get(id=parts_id[0]).captain
			room = tc.room
			for part_id in parts_id:
				part = Participant.objects.get(id=part_id)
				part.acco = False
				part.save()
				room.vacancy -= 1
				room.save()
			if all((not part.acco for part in Participant.objects.filter(captain=tc))):
				tc.room = None
				tc.save()
		return redirect(reverse('regsoft:recnacc-college', kwargs={'gl_id':gl_id}))


	# rows1 = [{'tc':tc, 'event':tc.event.name}  for tc in TeamCaptain.objects.filter(g_l=g_l, if_payment=True, firewallz_passed=True, room=None)]
	# rows2 = [{'tc':tc, 'event':tc.event.name}  for tc in TeamCaptain.objects.filter(g_l=g_l, if_payment=True, firewallz_passed=True).exclude(room=None)]

	# rooms = Room.objects.exclude(vacancy=0)
	# return render(request, 'regsoft/allot_room.html', {'allocate':rows1, 'deallocate':rows2, 'rooms':rooms})

@staff_member_required
def all_bhavans(request):
	rows =[{'data':[room.room, room.bhavan.name, room.vacancy], 'link':[] } for room in Room.objects.all()]
	headings = ['Room', 'Bhavan', 'Vacancy']
	tables = [{'title':'All Bhavans', 'headings':headings, 'rows':rows}]
	return render(request,'regsoft/tables.html' {'tables':tables})


@staff_member_required
def college_vs_bhavan(request):
	rows = list(set([{'data':[tc.g_l.college, tc.room.bhavan.name], 'link':[]} for tc in TeamCaptain.objects.filter(firewallz_passed=True, if_payment=True, acco=True)]))
	headings = ['College', 'Bhavan']
	tables = [{'title':'Bhavans vs College', 'headings':headings, 'rows':rows}]
	return render(request,'regsoft/tables.html' {'tables':tables})


@staff_member_required
def firewallz_approved(request):
	rows = [[part.name, part.captain.g_l.college, part.captain.gender,part.captain.g_l.name, part.captain.event.name, part.acco ] for tc in TeamCaptain.objects.filter(firewallz_passed=True, if_payment=True, acco=True) for part in Participant.objects.filter(captain=tc)]
	headings = ['Participant', 'College', 'Gender', 'Group Leader', 'Event', 'Alloted']
	tables = [{'title':'Firewallz Approved Participants', 'headings':headings, 'rows':rows}]
	return render(request,'regsoft/tables.html' {'tables':tables})


def controlz_home(request):
	if request.method == 'POST':
		try:
			barcode = request.POST['code']
			g_leader = GroupLeader.objects.get(id=barcode[::2])

		except:
			return render(request, 'registrations/message.html', {'message':'Group Leader with the given barcode does not exist.'})

		
