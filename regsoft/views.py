from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from registrations import views, urls
from events.models import *
from django.shortcuts import render, redirect, get_object_or_404
from registrations.models import *
from regsoft.models import *
import barg
from functools import reduce
import string
from random import randint
import json
from django.contrib.auth import logout

def home(request):
	
	profiles = GroupLeader.objects.filter(pcr_approved=True)
	headings = ['Name', 'College','Phone','No. of Paid Participants',  'Code', 'View Participants']
	rows = []
	urls = []
	for profile in profiles:
		tc = TeamCaptain.objects.filter(g_l = profile, pcr_final=True)
		no_paid = 0
		for t in tc:
			 if t.payment > 0:
				no_paid += t.participant_set.all().count()
		data = (profile.name, profile.college, str(profile.phone), no_paid, str(profile.barcode).upper())
		rows.append({'data':data, 'link':[{'title':'View Participants', 'link':'#'}]})
	t1 = {
		'title' : 'Barcodes',
		'headings':headings,
		'rows':rows,
	}
	return render(request, 'regsoft/tables.html', {'tables':[t1]})

@staff_member_required
def index(request, message=None):
	g_ls = GroupLeader.objects.filter(pcr_approved=True)
	return render(request, 'regsoft/index.html', {'groupleaders':g_ls})

def gen_barcode(g_l):
	gl_id = g_l.id
	encoded = g_l.barcode
	if encoded == '':
		raise ValueError
	if encoded is not None:
		return encoded
	gl_ida = "%04d" % int(gl_id)
	mixed = string.ascii_uppercase + string.ascii_lowercase
	encoded = ''.join([x+mixed[randint(0,51)] for x in gl_ida])
	g_l.barcode = encoded
	g_l.save()
	print 'encoded: ', encoded
	try:
		image='/root/live/bosm/backend/resources/bosm2017/barcodes/gleaders/%04s.gif' % int(gl_id)
		barg.code128_image(encoded).save(image)
	except:
		image = '/home/auto-reload/Desktop/barcodes/gleaders/%04d.gif' % int(gl_id)
		barg.code128_image(encoded).save(image)
	return encoded

def gen_barcode_participant(part):

	part_id = part.id
	print part_id
	encoded = part.barcode
	if encoded == '':
		raise ValueError
	if encoded is not None:
		return encoded
	part_ida = "%04d" % int(part_id)
	mixed = string.ascii_uppercase + string.ascii_lowercase
	encoded = ''.join([x+mixed[randint(0,51)] for x in part_ida])
	part.barcode = encoded
	part.save()

	print 'encoded: ', encoded
	try:
		image='/root/live/bosm/backend/resources/bosm2017/barcodes/participants/%04s.gif' % int(part_id)
		barg.code128_image(encoded).save(image)
	except:
		image = '/home/auto-reload/Desktop/barcodes/participants/%04d.gif' % int(part_id)
		barg.code128_image(encoded).save(image)
	return encoded

@staff_member_required
def get_barcode(request):
	g_ls = GroupLeader.objects.filter(pcr_approved=True)
	for g_l in g_ls:
		bc = gen_barcode(g_l)

	return redirect('regsoft:firewallz-home')

###########################################   FIREWALLZ ###############################################

@staff_member_required
def firewallzo_home(request):
	if request.method == 'POST':
		try:
			barcode = request.POST['barcode']
			g_l = GroupLeader.objects.get(barcode=barcode)
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		parts_id = [participant.id for captain in g_l.teamcaptain_set.filter(pcr_final=True, is_extra=False) for participant in captain.participant_set.all()]
		parts = Participant.objects.filter(pk__in=parts_id)
		confirmed = [{'name':part.name,
			'college': part.captain.g_l.college,
			'event': part.captain.event.name,
			'pcr':Participation.objects.get(event=part.captain.event, g_l=part.captain.g_l).confirmed,
			'captain':part.captain.name,
			'id':part.id,
			'barcode':part.barcode,
			'captain_id':part.captain.id} for part in parts.filter(firewallz_passed=True).order_by('captain__event__name')]
		unconfirmed = [{'name':part.name,
			'college': part.captain.g_l.college,
			'event': part.captain.event.name,
			'pcr':Participation.objects.get(event=part.captain.event, g_l=part.captain.g_l).confirmed,
			'captain':part.captain.name,
			'id':part.id,
			'captain_id':part.captain.id} for part in parts.filter(firewallz_passed=False).order_by('captain__event__name')]
		coaches = [[coach.name, coach.event.name, coach.g_l.college] for coach in Coach.objects.filter(g_l=g_l) ]
		return render(request, 'regsoft/firewallzo_home.html',{'confirmed':confirmed, 'unconfirmed':unconfirmed, 'gl_id':g_l.id, 'coaches':coaches})



	return render(request, 'regsoft/firewallzo_home.html', {'group_leaders':GroupLeader.objects.filter(pcr_approved=True)})

@staff_member_required
def firewallz_swap(request):
	try:
		data = request.POST
	except:
		return redirect(request.META.get('HTTP_REFERER'))
	print data
	if 'confirm' == data['action']:
		part_ids = dict(data)['data']
		print part_ids
		for part_id in part_ids:
			part = Participant.objects.get(id=part_id)
			part.firewallz_passed=True
			barcode = gen_barcode_participant(part)
			print barcode
			part.save()
			tc = part.captain
			if part.name == part.captain.name:
				captain = part.captain
				captain.firewallz_passed = True
				captain.save()
		return redirect('regsoft:firewallz-home')
	elif 'unconfirm' == data['action']:
		part_ids = dict(data)['data']
		print part_ids
		for part_id in part_ids:
			part = Participant.objects.get(id=part_id)
			part.firewallz_passed=False
			part.save()
			if part.name == part.captain.name:
				captain = part.captain
				captain.firewallz_passed = False
				captain.save()

		return redirect('regsoft:firewallz-home')
			
	return redirect(request.META.get('HTTP_REFERER'))

@staff_member_required
def firewallz_edit(request, part_id):
	part = Participant.objects.get(id=part_id)
	tc = part.captain
	g_l = tc.g_l
	if request.method=='POST':
		try:
			name = request.POST['name']
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		if part.name == part.captain.name:
			captain = part.captain
			captain.name = name
			captain.save()
		part.name = name
		part.save()
		request.method = 'POST'

		return redirect(reverse('regsoft:firewallz-home'))
		
	return render(request, 'regsoft/controlz_edit.html', 
		{'name':part.name, 'college':g_l.college, 'captain':tc.name, 'g_l':g_l.name, 'event':tc.event})

@staff_member_required
def firewallz_add(request, gl_id):
	g_l = GroupLeader.objects.get(id=gl_id)
	if request.method == 'POST':
		try:
			event = Event.objects.get(id=request.POST['event'])
			name = request.POST['name']
			gender = request.POST['gender']
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		
		if event.max_limit == 1:
			try:
				for t in TeamCaptain.objects.filter(event=event, g_l=g_l):
					if t.phone > 0:
						tc1 = t
						break
				print tc1
				tc = TeamCaptain.objects.create(g_l=g_l, name=name, is_single=True, event=event, gender=gender, email=tc1.email, phone=tc1.phone, pcr_final=True)
			except:
				tc = TeamCaptain.objects.create(g_l=g_l, name=name, is_single=True, event=event, gender=gender, pcr_final=True)

			part = Participant.objects.create(name=name, captain=tc,)
		else:
			try:
				tc1 = TeamCaptain.objects.filter(event=event, g_l=g_l)[0]
				if not(tc1.total_players < event.max_limit):
					raise ValueError
			except:
				return redirect(request.META.get('HTTP_REFERER'))

			part = Participant.objects.create(captain=tc1, name=name,)
			tc1.total_players+=1
			tc1.save()

		# request.POST['barcode'] = g_l.barcode
		return redirect(reverse('regsoft:firewallz-home'))
	events = [part.event for part in Participation.objects.filter(g_l=g_l, confirmed=True)]
	return render(request,  'regsoft/controlz_add.html',{'events':events, 'g_l':g_l})

@staff_member_required
def firewallz_delete(request):
	try:
		gl_id = request.POST['gl_id']
		g_l = GroupLeader.objects.get(id=gl_id)
		parts_id = dict(request.POST)['data']
	except:
		return render(request, 'registrations/message.html', {'message':'Group Leader with the given barcode does not exist.'})
	for part_id in parts_id:
		part = Participant.objects.get(id=part_id)
		tc = part.captain
		if tc.participant_set.all().count() == 1:
			tc.delete()
		else:
			part.delete()
			tc.total_players-=1
			tc.save()
	return redirect('regosft:firewallz-home')

@staff_member_required
def firewallz_edit_tc(request, tc_id):
	tc = TeamCaptain.objects.get(id=tc_id)
	if request.method == 'POST':
		name = request.POST['name']
		phone = request.POST['phone']
		tc.name = name
		tc.phone = phone
		tc.save()
		return redirect('regsoft:firewallz-home')
	return render(request, 'regsoft/firewallz_edit_tc.html', {'tc':tc, 'event':tc.event, 'g_l':tc.g_l})





###################################################### RECNACC #############################################

@staff_member_required
def recnacc_home(request):
	if request.method == 'POST':
		try:
			barcode = request.POST['barcode']
			g_l = GroupLeader.objects.get(barcode=barcode)
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		return redirect(reverse('regsoft:recnacc-college', kwargs={'gl_id':g_l.id}))

	g_ls = GroupLeader.objects.filter(pcr_approved=True)
	rows = [{'data':[g_l.college, count_players(g_l), if_alloted_any(g_l)], 'link':[{'title':'Allot', 'url':reverse('regsoft:recnacc-college', kwargs={'gl_id':g_l.id})}]} for g_l in g_ls if count_players(g_l)!=0]
	headings = ['College', 'No. of Participants','Alloted', 'Allot']
	tables = [{'title':'Select College to allot rooms', 'rows':rows, 'headings':headings}]
	return render(request,'regsoft/recnacc_home.html', {'tables':tables})

def if_alloted_any(g_l):
	x=0
	y=0
	for tc in TeamCaptain.objects.filter(g_l=g_l, is_extra=False, if_payment=True):
		for part in tc.participant_set.filter(firewallz_passed=True):
			y+=1
			if part.acco:
				x+=1
	return x==y
def count_players(g_l):
	tcs = TeamCaptain.objects.filter(g_l=g_l,pcr_final=True, is_extra=False, if_payment=True)
	sum=0
	for tc in tcs:
		sum+=tc.participant_set.filter(firewallz_passed=True).count()
	return sum

def count_players_accomodated(g_l):
	tcs = TeamCaptain.objects.filter(g_l=g_l, pcr_final=True, is_extra=False, if_payment=True)
	sum=0
	for tc in tcs:
		sum+=tc.participant_set.filter(acco=True).count()
	return sum

@staff_member_required
def recnacc_college(request, gl_id):
	g_l = GroupLeader.objects.get(id=gl_id)
	rooms = Room.objects.all()
	parts1 = []
	parts2 = []
	for tc in TeamCaptain.objects.filter(g_l=g_l, pcr_final=True, is_extra=False, if_payment=True):
		if tc.participant_set.filter(firewallz_passed=True):
			parts1 += Participant.objects.filter(captain=tc, acco=True, firewallz_passed=True)
			parts2 += Participant.objects.filter(captain=tc, acco=False, firewallz_passed=True)
	
	coach1 = Coach.objects.filter(g_l=g_l, acco=True)
	coach2 = Coach.objects.filter(g_l=g_l, acco=False)
	return render(request, 'regsoft/allot.html', {'alloted':parts1, 'unalloted':parts2, 'rooms':rooms,'g_l':g_l, 'coach_unalloted':coach2, 'coach_alloted':coach1})

@staff_member_required
def recnacc_change(request):
	if request.POST:
		from datetime import datetime
		data = request.POST
		if 'allocate' == data['action']:
			try:
				parts_id = dict(data)['data']
				room_id = data['room']
				room = Room.objects.get(id=room_id)
				
			except:
				return redirect(request.META.get('HTTP_REFERER'))
				
			rows = []
			room.vacancy -= len(parts_id)
			room.save()
			gl_id=0
			for part_id in parts_id:
				part = Participant.objects.get(id=part_id)
				part.acco = True
				part.room = room
				part.recnacc_time = datetime.now()
				part.save()
				if part.captain.name == part.name:
					tc = part.captain
					tc.room =room
					tc.acco = True
					tc.save()
				gl_id = part.captain.g_l.id
			
			try:
				coach_list = data.getlist('coach_data')
				for c_id in coach_list:
					coach = Coach.objects.get(id=c_id)
					coach.acco = True
					coach.room = room
					coach.save()
					room.vacancy -= 1
					room.save()
			except:
				pass
				
		if 'deallocate' == data['action']:
			print data
			try:
				parts_id = dict(data)['data']
				print parts_id
			except:
				return redirect(request.META.get('HTTP_REFERER'))
			tc = Participant.objects.get(id=parts_id[0]).captain
			# room = tc.room
			for part_id in parts_id:
				part = Participant.objects.get(id=part_id)
				part.acco = False
				room = part.room
				part.room = None
				part.save()
				room.vacancy += 1
				room.save()
			if all((not part.acco for part in Participant.objects.filter(captain=tc))):
				tc.room = None
				tc.save()
			try:
				coach_list = data.getlist('coach_data')
				for c_id in coach_list:
					coach = Coach.objects.get(id=c_id)
					room = coach.room
					coach.acco = False
					coach.room = None
					coach.save()
					room.vacancy += 1
					room.save()
			except:
				pass
			gl_id = tc.g_l.id
		return redirect(reverse('regsoft:recnacc-college', kwargs={'gl_id':gl_id}))

@staff_member_required
def add_coach_recnacc(request, gl_id):
	g_leader = GroupLeader.objects.get(id=gl_id)
	if request.method == 'POST':
		try:
			event = Event.objects.get(id=request.POST['event'])
			name = request.POST['name']
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		coach = Coach.objects.create(name=name, event=event, g_l=g_leader)
		if request.user.username == 'firewallz':
			return redirect(reverse('regsoft:firewallz-home'))			
		return redirect(reverse('regsoft:recnacc-college', kwargs={'gl_id':gl_id}))
		
	events = [part.event for part in Participation.objects.filter(g_l=g_leader)]
	return render(request, 'regsoft/add_coach.html', {'g_l':g_leader, 'events':events})

@staff_member_required
def recnacc_checkout(request):
	g_ls = GroupLeader.objects.filter(pcr_approved=True)
	rows = [{'data':[g_l.name, g_l.college, count_players_accomodated(g_l)], 'link':[{'title':'Select', 'url':reverse('regsoft:recnacc_checkout_id', kwargs={'gl_id':g_l.id})},]} for g_l in g_ls]
	headings = ['Group Leader', 'College', 'Total Players', 'Select']
	tables = {'title':'Select College for Checkout', 'headings':headings, 'rows':rows}
	return render(request, 'regsoft/tables.html', {'tables':[tables,]})

@staff_member_required
def recnacc_checkout_id(request,gl_id):
	g_l = GroupLeader.objects.get(id=gl_id)
	if request.method == 'POST':
		from datetime import datetime
		data = request.POST
		part_list = data.getlist('part_list')

		participant_list = Participant.objects.filter(id__in=part_list)
		for p_id in part_list:
			part = Participant.objects.get(id=p_id)
			part.acco = False
			part.room = None
			part.checkout = True
			part.save()
		time = datetime.now()
		amount_retained = int(data['retained'])
		amount_returned = (len(part_list)*300) - amount_retained
		return render(request, 'regsoft/checkout_invoice.html', {'retained':amount_retained, 'returned':amount_returned, 'part_list':participant_list, 'g_l':g_l, 'time':time})

	teamcaptain_list = g_l.teamcaptain_set.filter(pcr_final=True)
	part_list = Participant.objects.filter(captain__g_l=g_l, acco=True, captain__pcr_final=True)
	return render(request, 'regsoft/checkout.html', {'part_list':part_list, 'g_l':g_l})


@staff_member_required
def all_bhavans(request):
	rows =[{'data':[bhavan.name, reduce(lambda x,y:x+y.vacancy, bhavan.room_set.all(), 0),], 'link':[{'title':'Details', 'url':reverse('regsoft:bhavan_details', kwargs={'b_id':bhavan.id})},] } for bhavan in Bhavan.objects.all()]
	headings = ['Bhavan', 'Vacancy', 'Room-wise details']
	tables = [{'title':'All Bhavans', 'headings':headings, 'rows':rows}]
	return render(request,'regsoft/tables.html', {'tables':tables})

@staff_member_required
def bhavan_details(request, b_id):
	bhavan = Bhavan.objects.get(id=b_id)
	rows = [{'data':[room.room, room.vacancy, room.capacity], 'link':[]} for room in bhavan.room_set.all()]
	headings = ['Room', 'Vacancy', 'Capacity']
	tables = [{'title': 'Details for ' + bhavan.name + ' bhavan', 'headings':headings, 'rows':rows}]
	return render(request, 'regsoft/tables.html', {'tables':tables})

@staff_member_required
def college_vs_bhavan(request):
	x = [[part.captain.g_l.college, part.room.bhavan.name, part.room.room, part.captain.event.name] for part in Participant.objects.filter(firewallz_passed=True, acco=True)]
	rows = [{'data':i, 'link':[]} for i in x]
	print rows
	headings = ['College', 'Bhavan','Room', 'Event']
	tables = [{'title':'Bhavans vs College', 'headings':headings, 'rows':rows}]
	return render(request,'regsoft/tables.html', {'tables':tables})

@staff_member_required
def firewallz_approved(request):
	keys=[]
	for tc in TeamCaptain.objects.filter(pcr_final=True):
		keys += list([{'data':[part.name, part.captain.g_l.college, part.captain.gender,part.captain.g_l.name, part.captain.event.name, part.acco, part.room.room, part.room.bhavan], 'link':[]}] for part in tc.participant_set.filter(firewallz_passed=True) if part.acco)
		keys += list([{'data':[part.name, part.captain.g_l.college, part.captain.gender,part.captain.g_l.name, part.captain.event.name, part.acco, '-', '-'], 'link':[]}] for part in tc.participant_set.filter(firewallz_passed=True) if not part.acco)
		
	rows = []
	for key in keys:
		for l in key:
			rows.append(l)

	headings = ['Participant', 'College', 'Gender', 'Group Leader', 'Event', 'Alloted', 'Room', 'Bhavan']
	tables = [{'title':'Firewallz Approved Participants', 'headings':headings, 'rows':rows}]
	return render(request,'regsoft/tables.html', {'tables':tables})


##################################################   CONTROLZ ######################################################

@staff_member_required
def controlz_home(request):
	if request.method == 'POST':
		try:
			barcode = request.POST['barcode']
			g_leader = GroupLeader.objects.get(barcode=barcode)
		except:
			return render(request, 'registrations/message.html', {'message':'Group Leader with the given barcode does not exist.'})
		rows = [{'id':part.id, 'name':part.name, 'event':part.captain.event.name, 'captain_id':part.captain.id, 'captain':part.captain.name, 'link':reverse('regsoft:controlz_edit', kwargs={'part_id':part.id}), 'college':g_leader.college} for part in Participant.objects.filter(captain__g_l=g_leader, firewallz_passed=True)]
		headings = ['Name', 'Event', 'Captain', 'College', 'Edit', 'Select']
		table = {'title':'Participants for ' + g_leader.college, 'rows':rows, 'headings':headings}
		return render(request, 'regsoft/controlz_home.html', {'table':table, 'gl_id':g_leader.id})

	return render(request, 'regsoft/controlz_home.html', 
		{'group_leaders':GroupLeader.objects.filter(pcr_approved=True)})


@staff_member_required
def controlz_edit(request, part_id):
	part = Participant.objects.get(id=part_id)
	tc = part.captain
	g_l = tc.g_l
	if request.method=='POST':
		try:
			name = request.POST['name']
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		if part.name == part.captain.name:
			captain = part.captain
			captain.name = name
			captain.save()
		part.name = name
		part.save()
		request.method = 'POST'

		return redirect('regsoft:controlz-home')
		
	return render(request, 'regsoft/controlz_edit.html', 
		{'name':part.name, 'college':g_l.college, 'captain':tc.name, 'g_l':g_l.name, 'event':tc.event})

@staff_member_required
def controlz_add(request, gl_id):
	g_l = GroupLeader.objects.get(id=gl_id)
	if request.method == 'POST':
		try:
			event = Event.objects.get(id=request.POST['event'])
			name = request.POST['name']
			gender = request.POST['gender']
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		
		if event.max_limit == 1:
			try:
				tc1 = TeamCaptain.objects.filter(event=event, g_l=g_l)[0]
				tc = TeamCaptain.objects.create(g_l=g_l, name=name, is_single=True, event=event, firewallz_passed=True, gender=gender, email=tc1.email, phone=tc1.phone, pcr_final=True)
			except:
				tc = TeamCaptain.objects.create(g_l=g_l, name=name, is_single=True, event=event, firewallz_passed=True, gender=gender, pcr_final=True)

			part = Participant.objects.create(name=name, captain=tc, firewallz_passed=True)
		else:
			try:
				tc1 = TeamCaptain.objects.filter(event=event, g_l=g_l)[0]
				if not(tc1.total_players < event.max_limit):
					raise ValueError
			except:
				return redirect(request.META.get('HTTP_REFERER'))

			part = Participant.objects.create(captain=tc1, name=name, firewallz_passed=True)
			tc1.total_players+=1
			tc1.save()

		# request.POST['barcode'] = g_l.barcode
		return redirect(reverse('regsoft:controlz_home'))
	events = [part.event for part in Participation.objects.filter(g_l=g_l, confirmed=True)]
	return render(request,  'regsoft/controlz_add.html',{'events':events})

@staff_member_required
def controlz_delete(request):
	try:
		gl_id = request.POST['gl_id']
		g_l = GroupLeader.objects.get(id=gl_id)
		parts_id = dict(request.POST)['data']
	except:
		return render(request, 'registrations/message.html', {'message':'Group Leader with the given barcode does not exist.'})
	for part_id in parts_id:
		part = Participant.objects.get(id=part_id)
		tc = part.captain
		if tc.participant_set.all().count() == 1:
			tc.delete()
		else:
			part.delete()
			tc.total_players-=1
			tc.save()
	return redirect('regosft:controlz_home')


@staff_member_required
def controlz_edit_tc(request, tc_id):
	tc = TeamCaptain.objects.get(id=tc_id)
	if request.method == 'POST':
		name = request.POST['name']
		phone = request.POST['phone']
		tc.name = name
		tc.phone = phone
		tc.save()
		return redirect('regsoft:controlz-home')
	return render(request, 'regsoft/firewallz_edit_tc.html', {'tc':tc, 'event':tc.event, 'g_l':tc.g_l})


@staff_member_required
def recnacc_list(request, gl_id):
	g_leader = get_object_or_404(GroupLeader, id=gl_id)
	participant_list = []
	for captain in g_leader.teamcaptain_set.filter(pcr_final=True):
		participant_list += captain.participant_set.filter(firewallz_passed=True, acco=True)
	
	participant_list.sort(key=lambda x: x.recnacc_time, reverse=True)
	coaches_list = Coach.objects.filter(g_l=g_leader, acco=True)
	return render(request, 'regsoft/recnacc_list.html', {'participant_list':participant_list, 'coaches':coaches_list})

@staff_member_required
def generate_recnacc_list(request):
	if request.method == 'POST':
		
		data = request.POST
		id_list = data.getlist('data')
		cid_list = data.getlist('coach_data')
		c_rows = []
		# value = 300
		for p_id in id_list:
			part = Participant.objects.get(id=p_id)
			c_rows.append({'data':[part.name, part.captain.g_l.college, part.captain.gender,part.captain.g_l.name, part.captain.event.name, part.room.room, part.room.bhavan, 300], 'link':[]})
			
		for cid in cid_list:
			coach = Coach.objects.get(id=cid)
			c_rows.append({'data':[coach.name, coach.g_l.college, 'N/A(Coach)', coach.g_l.name, coach.event.name,coach.room.room,coach.room.bhavan, 300 ]})
		amount = (len(id_list)+len(cid_list))*300
		c_rows.append({'data':['Total', '','','','','','',amount]})
		table = {
			'title':'Participant list for RecNAcc',
			'headings':['Name', 'College', 'Gender', 'GroupLeader', 'Event', 'Room','Bhavan', 'Caution Deposit'],
			'rows': c_rows
		}
		return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def add_coach_controlz(request, gl_id):
	g_leader = GroupLeader.objects.get(id=gl_id)
	if request.method == 'POST':
		try:
			event = Event.objects.get(id=request.POST['event'])
			name = request.POST['name']
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		coach = Coach.objects.create(name=name, event=event, g_l=g_leader)
		return redirect(reverse('regsoft:create_bill', kwargs={'gl_id':gl_id}))
		
	events = [part.event for part in Participation.objects.filter(g_l=g_leader)]
	return render(request, 'regsoft/add_coach.html', {'g_l':g_leader, 'events':events})

@staff_member_required
def get_details(request):
	context = {}
	if request.method == 'POST':
		if 'event' in request.POST:
			event = Event.objects.get(id=request.POST['id'])
			captain_list = TeamCaptain.objects.filter(event=event, pcr_final=True)
			participant_list = []
			for captain in captain_list:
				participant_list += Participant.objects.filter(captain=captain, firewallz_passed=True)

			rows = []
			for participant in participant_list:
				try:
					room = participant.room.room
					bhavan = participant.room.bhavan.name
				except:
					room = 'None'
					bhavan = 'None'
				rows.append({'data':[str(participant.name).title(), str(participant.captain.name).title(), str(participant.captain.g_l.college).title(),room, bhavan], 'link':[]})

			headings = ['Name', 'Captain', 'College', 'Room', 'Bhavan']
			title = 'Participant list for ' + event.name
			print rows
		elif 'college' in request.POST:
			g_leader = GroupLeader.objects.get(id=request.POST['id'])
			captain_list = TeamCaptain.objects.filter(g_l=g_leader, pcr_final=True)
			participant_list = []
			for captain in captain_list:
				participant_list += Participant.objects.filter(captain=captain, firewallz_passed=True)

			rows = []
			for participant in participant_list:
				try:
					room = participant.room.room
					bhavan = participant.room.bhavan.name
				except:
					room = 'None'
					bhavan = 'None'
				rows.append({'data':[str(participant.name).title(), str(participant.captain.name).title(), str(participant.captain.event.name).title(),  room, bhavan], 'link':[]})

			headings = ['Name', 'Captain', 'Event', 'Room', 'Bhavan']
			title = 'Participant list for ' + request.POST['college']

		table = {
			'headings':headings,
			'rows':rows,
			'title':title
		}

		context = {
			'tables':[table,]
		}
	events = Event.objects.all()
	gls = GroupLeader.objects.all()
	context['events'] = events
	context['gls'] = gls
	return render(request, 'regsoft/controlz_details.html', context)

#######################################    BILLINGS      ##############################################

# @staff_member_required
# def view_captain_controlz(request, gl_id):
# 	try:
# 		g_leader = GroupLeader.objects.get(id=gl_id)
# 	except:
# 		return render(request, 'pcradmin/message', {'message':'Invalid group leader'})
	
# 	c_rows = []
# 	u_rows = []
# 	c_count = 0
# 	u_count = 0
# 	for tc in TeamCaptain.objects.filter(g_l=g_leader):
# 		if tc.firewallz_passed == True:
# 			try:
# 				room = tc.room.room
# 				bhavan = tc.room.bhavan.name
# 			except:
# 				room = 'None'
# 				bhavan = 'None'
# 			if tc.if_payment:
# 				c_rows.append({'data':[str(tc.name.title()), str(tc.event.name.title()), str(tc.total_players), tc.payment,tc.event.price, room, bhavan], 'link':[{'title':'Edit details', 'url':reverse('regsoft:view_captain', kwargs={'tc_id':tc.id}), }, {'title':'Show Team List','url':reverse('regsoft:show_team_list', kwargs={'tc_id':tc.id})}]})
# 			else:
# 				c_rows.append({'data':[str(tc.name.title()), str(tc.event.name.title()), str(tc.total_players), tc.payment,'Extra Event	', room, bhavan], 'link':[{'title':'Edit details', 'url':reverse('regsoft:view_captain', kwargs={'tc_id':tc.id}), }, {'title':'Show Team List','url':reverse('regsoft:show_team_list', kwargs={'tc_id':tc.id})}]})
			
# 			c_count += 1

# 		else:
# 			u_rows.append({'data':[str(tc.name.title()), str(tc.event.name.title()), str(tc.total_players)],})
# 			u_count += 1

# 	confirmed = {
# 		'title':'Teams confirmed by Firewallz from ' + g_leader.college,
# 		'headings':['Name', 'Event', 'Total Players', 'Amount Paid','Amount to be Paid','Room','Bhavan', 'Edit details', 'Team List', ],
# 		'rows':c_rows 
# 	}	
# 	print confirmed
# 	unconfirmed = {
# 		'title':'Participants not confirmed by Firewallz from ' + g_leader.college,
# 		'headings':['Name', 'Event', 'Total Players'],
# 		'rows':u_rows
# 	}
# 	print unconfirmed

# 	context = {
# 		'tables':[confirmed, unconfirmed]
# 	}

# 	return render(request, 'regsoft/controlz_home.html', context)

# 	return render(request, 'regsoft/controlz_home.html', context)

@staff_member_required
def get_captains(request):
	g_ls = GroupLeader.objects.filter(pcr_approved=True)
	rows = [{'data':[g_l.college, count_players(g_l)], 'link':[{'title':'Create Bill', 'url':reverse('regsoft:create_bill', kwargs={'gl_id':g_l.id})}, {'title':'View Bills', 'url':reverse('regsoft:view_bills', kwargs={'gl_id':g_l.id})}]} for g_l in g_ls if count_players(g_l)!=0]
	headings = ['College', 'No. of Participants', 'Create Bills', 'View Bills']
	tables = [{'title':'Select College to create bills', 'rows':rows, 'headings':headings}]
	return render(request,'regsoft/recnacc_home.html', {'tables':tables})

@staff_member_required
def create_bill(request, gl_id):
	g_leader = get_object_or_404(GroupLeader, id=gl_id)
	if request.method == 'POST':
		data = request.POST
		id_list = data.getlist('data')
		print data.getlist('coach_data')
		coach_list = Coach.objects.filter(id__in=data.getlist('coach_data'))
		bill = Bill()
		bill.two_thousands = data['twothousands']
		bill.five_hundreds = data['fivehundreds']
		bill.hundreds = data['hundreds']
		bill.fifties = data['fifties']
		bill.twenties = data['twenties']
		bill.tens = data['tens']
		bill.two_thousands_returned = data['twothousandsreturned']
		bill.five_hundreds_returned = data['fivehundredsreturned']
		bill.hundreds_returned = data['hundredsreturned']
		bill.fifties_returned = data['fiftiesreturned']
		bill.twenties_returned = data['twentiesreturned']
		bill.tens_returned = data['tensreturned']
		amount_dict = {'twothousands':2000, 'fivehundreds':500, 'hundreds':100, 'fifties':50, 'twenties':20, 'tens':10}
		return_dict = {'twothousandsreturned':2000, 'fivehundredsreturned':500, 'hundredsreturned':100, 'fiftiesreturned':50, 'twentiesreturned':20, 'tensreturned':10}
		bill.amount = 0
		for key,value in amount_dict.iteritems():
			bill.amount += int(data[key])*int(value)
		for key,value in return_dict.iteritems():
			bill.amount -= int(data[key])*int(value)

		for coach in coach_list:
			coach.paid = True
			coach.save()

		try:
			bill.draft_number = data['draft_number']
		except:
			pass
		bill.draft_amount = data['draft_amount']
		print bill.draft_amount
		bill.amount += int(bill.draft_amount)
		if not (bill.amount == 0 and bill.draft_amount == 0):
			bill.g_leader = g_leader
			bill.save()
			for p_id in id_list:
				part = Participant.objects.get(id=p_id)
				part.bill = bill
				part.controlz = True
				part.save()
			for coach in coach_list:
				coach.bill = bill
				coach.save()

			return redirect(reverse('regsoft:view_bills', kwargs={'gl_id':g_leader.id}))

		else:
			return redirect(reverse('regsoft:create_bill', kwargs={'gl_id':gl_id}))
	
	participant_list = []
	coaches_list = Coach.objects.filter(g_l=g_leader, paid=False)
	for captain in g_leader.teamcaptain_set.filter(pcr_final=True):
		participant_list += captain.participant_set.filter(firewallz_passed=True, controlz=False)
	
	
	return render(request, 'regsoft/create_bill.html', {'g_leader':g_leader, 'participant_list':participant_list, 'coaches':coaches_list})

@staff_member_required
def view_bills(request, gl_id):
	g_leader = GroupLeader.objects.get(id=gl_id)
	c_rows = [{'data':[bill.participant_set.count(),bill.coach_set.count(), bill.time_paid, bill.amount-bill.draft_amount, bill.draft_amount, bill.draft_number], 'link':[{'title':'View details', 'url':reverse('regsoft:bill_details',kwargs={'b_id':bill.id})}]} for bill in Bill.objects.filter(g_leader = g_leader, is_displayed=True)]
	bill_table = {
		'title':"Bills created under " + g_leader.name,
		'headings':['Participants','Coaches','Time paid',  'Cash paid', 'Draft Amount', 'Draft Number', 'View Details'],
		'rows':c_rows,
	}

	return render(request, 'regsoft/tables.html', {'tables':[bill_table]})

@staff_member_required
def master_bill(request):
	bill_list = Bill.objects.all()
	two_thousand = 0
	five_hundred = 0
	hundred = 0
	fifty = 0
	twenty = 0
	ten = 0
	returned_two_thousand = 0
	returned_five_hundred = 0
	returned_hundred = 0
	returned_fifty = 0
	returned_twenty = 0
	returned_ten = 0
	for bill in bill_list:
		two_thousand += bill.two_thousands
		five_hundred += bill.five_hundreds
		hundred += bill.hundreds
		fifty += bill.fifties
		twenty += bill.twenties
		ten += bill.tens
		returned_two_thousand += bill.two_thousands_returned
		returned_five_hundred += bill.five_hundreds_returned
		returned_hundred += bill.hundreds_returned
		returned_fifty += bill.fifties_returned
		returned_twenty += bill.twenties_returned
		returned_ten += bill.tens_returned

	rows = [{'data':['Two Thousands', two_thousand]},
			{'data':['Five Hundreds', five_hundred]},
			{'data':['Hundreds', hundred]},
			{'data':['Fifties', fifty]},
			{'data':['Twenties', twenty]},
			{'data':['Tens', ten]},
			{'data':['Returned Two Thousands', returned_two_thousand]},
			{'data':['Returned Five Hundreds', returned_five_hundred]},
			{'data':['Returned Hundreds', returned_hundred]},
			{'data':['Returned Fifties', returned_fifty]},
			{'data':['Returned Twenties', returned_twenty]},
			{'data':['Returned Tens', returned_ten]},]
	headings = ['Denomination', 'Number of notes']
	title = 'Notes Master List'
	table = {
	'rows':rows,
	'headings':headings,
	'title':title,
	}
	return render(request, 'regsoft/tables.html', {'tables':[table,]})

@staff_member_required
def bill_details(request, b_id):
	bill = get_object_or_404(Bill, id=b_id)
	c_rows = [{'data':[part.name, part.captain.name, part.captain.event.name, bill.time_paid,], 'link':[]} for part in bill.participant_set.all()]
	table = {
		'title' : 'Participant details for the bill under ' + bill.g_leader.name + ' from ' + bill.g_leader.college+'. Cash amount = Rs ' + str(bill.amount-bill.draft_amount) + '. Draft Amount = Rs ' + str(bill.draft_amount),
		'headings' : ['Name', 'Captain', 'Event', 'Time created',],
		'rows':c_rows,
	}
	d_rows = [{'data':[coach.name, coach.event.name, bill.time_paid,], 'link':[]} for coach in bill.coach_set.all()]
	table2 = {
		'title':'Coach details',
		'headings':['Name','Event','Time created'],
		'rows':d_rows
	}
	return render(request, 'regsoft/bill_details.html', {'tables':[table, table2], 'bill':bill})

@staff_member_required
def delete_bill(request, b_id):
	bill = get_object_or_404(Bill, id=b_id)
	gl_id = bill.g_leader.id
	g_leader = bill.g_leader
	for part in bill.participant_set.all():
		part.controlz = False
		part.bill = None
		part.save()
	
	for coach in bill.coach_set.all():
		coach.paid = False
		coach.bill = None
		coach.save()

	bill.is_displayed = False
	bill.save()
	return redirect(reverse('regsoft:view_bills', kwargs={'gl_id':gl_id}))

@staff_member_required
def team_captain_list(request):
	rows = [{'data':[captain.name, captain.event.name, captain.phone, captain.email, captain.g_l.college]} for captain in TeamCaptain.objects.filter(pcr_final=True)]
	table = {
		'rows':rows,
		'headings':['Name', 'Event', 'Phone', 'Email', 'College'],
		'title':'Captains finalised by PCr',
	}
	return render(request, 'regsoft/tables.html', {'tables':[table]})

@staff_member_required
def print_bill(request, b_id):
	from datetime import datetime
	time_stamp = datetime.now()
	bill = get_object_or_404(Bill, id=b_id)
	g_leader = bill.g_leader
	part_list = bill.participant_set.all()
	coach_list = bill.coach_set.all()

	try:
		draft = bill.draft_number
	except:
		draft = ''
	payment_methods = [{'method':'Cash', 'amount':bill.amount-bill.draft_amount}, {'method':'Draft #'+draft, 'amount':bill.draft_amount}]

	number = Bill.objects.all().count()
	return render(request, 'regsoft/print_bill.html', {'part_list':part_list, 'coaches_list':coach_list ,'g_leader':g_leader, 'time':time_stamp, 'bill':bill, 'payment_methods':payment_methods, 'total':bill.amount, 'number':number})

@staff_member_required
def contacts(request):
	return render(request, 'regsoft/contact.html')

@staff_member_required
def user_logout(request):
	logout(request)
	return redirect('regsoft:index')
