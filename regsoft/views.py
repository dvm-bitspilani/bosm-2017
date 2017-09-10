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
from django.contrib.auth import logout

def home(request):
	
	profiles = GroupLeader.objects.filter(pcr_approved=True)
	headings = ['Name', 'College','Phone','No. of Paid Participants',  'Code', 'View Participants']
	rows = []
	urls = []
	for profile in profiles:
		tc = TeamCaptain.objects.filter(g_l = profile)
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
def index(request):
	g_ls = GroupLeader.objects.filter(pcr_approved=True)
	return render(request, 'regsoft/index.html', {'groupleaders':g_ls})


# @staff_member_required
def gen_barcode(g_l):
	try:
		gl_id = g_l.id
		encoded = g_l.barcode
		if encoded == '':
			raise ValueError
		return encoded
	except:
		gl_ida = "%04d" % int(gl_id)
		mixed = string.ascii_uppercase + string.ascii_lowercase
		encoded = ''.join([x+mixed[randint(0,51)] for x in gl_ida])
		g_l.barcode = encoded
		g_l.save()
	print 'encoded: ', encoded
	try:
		image='/home/dvm/bosm/public_html/bosm2017/barcodes/%04s.gif' % int(gl_id)
		barg.code128_image(encoded).save(image)
	except:
		image = '/home/tushar/barcodes/%04d.gif' % int(gl_id)
		barg.code128_image(encoded).save(image)
	return encoded


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
	rows = [{'data':[g_l.college, count_players(g_l)], 'link':[{'title':'Allot', 'url':reverse('regsoft:recnacc-college', kwargs={'gl_id':g_l.id})}]} for g_l in g_ls if count_players(g_l)!=0]
	headings = ['College', 'No. of Participants', 'Allot']
	tables = [{'title':'Select College to allot rooms', 'rows':rows, 'headings':headings}]
	return render(request,'regsoft/recnacc_home.html', {'tables':tables})


@staff_member_required
def recnacc_college(request, gl_id):
	g_l = GroupLeader.objects.get(id=gl_id)
	rows = [{'data':[tc.name, tc.event.name, tc.g_l.college, tc.total_players], 'link':[{'title':'Allot', 'url':reverse('regsoft:recnacc-team', kwargs={'tc_id':tc.id})}]} for tc in TeamCaptain.objects.filter(firewallz_passed=True, g_l=g_l)]
	headings = ['Team Captain', 'Event', 'College', 'No. of Players', 'Select']
	tables = [{'title':'Select Team for '+g_l.college, 'rows':rows, 'headings':headings}]
	return render(request,'regsoft/tables.html', {'tables':tables})


@staff_member_required
def recnacc_team(request, tc_id):
	tc = TeamCaptain.objects.get(id=tc_id)
	rooms = Room.objects.all()
	parts1 = Participant.objects.filter(captain=tc, acco=True)
	parts2 = Participant.objects.filter(captain=tc, acco=False)
	return render(request, 'regsoft/allot.html', {'alloted':parts1, 'unalloted':parts2, 'rooms':rooms, 'tc':tc})



def count_players(g_l):
	tcs = TeamCaptain.objects.filter(g_l=g_l, firewallz_passed=True)
	sum=0
	for tc in tcs:
		sum+=tc.total_players
	return sum

@staff_member_required
def recnacc_change(request):
	if request.POST:
		data = request.POST
		if 'allocate' == data['action']:
			try:
				parts_id = dict(data)['data']
				room_id = data['room']
				room = Room.objects.get(id=room_id)
				if len(parts_id) > room.vacancy:
					raise KeyError
			except:
				return redirect(request.META.get('HTTP_REFERER'))
				
			rows = []
			tc = Participant.objects.get(id=parts_id[0]).captain
			tc.room =room
			tc.acco = True
			tc.save()
			room.vacancy -= len(parts_id)
			room.save()
			for part_id in parts_id:
				part = Participant.objects.get(id=part_id)
				part.acco = True
				part.room = room
				part.save()
			gl_id = tc.g_l.id
		

		if 'deallocate' == data['action']:
			print data
			try:
				parts_id = dict(data)['data']
				print parts_id
			except:
				return redirect(request.META.get('HTTP_REFERER'))
			tc = Participant.objects.get(id=parts_id[0]).captain
			room = tc.room
			for part_id in parts_id:
				part = Participant.objects.get(id=part_id)
				part.acco = False
				part.room = None
				part.save()
				room.vacancy += 1
				room.save()
			if all((not part.acco for part in Participant.objects.filter(captain=tc))):
				tc.room = None
				tc.save()
			gl_id = tc.g_l.id
		return redirect(reverse('regsoft:recnacc-college', kwargs={'gl_id':gl_id}))


@staff_member_required
def all_bhavans(request):
	rows =[{'data':[bhavan.name, reduce(lambda x,y:x+y.vacancy, bhavan.room_set.all(), 0),], 'link':[{'title':'Details', 'url':reverse('regsoft:bhavan_details', kwargs={'b_id':bhavan.id})},] } for bhavan in Bhavan.objects.all()]
	headings = ['Bhavan', 'Vacancy', 'Room-wise details']
	tables = [{'title':'All Bhavans', 'headings':headings, 'rows':rows}]
	return render(request,'regsoft/tables.html', {'tables':tables})

@staff_member_required
def bhavan_details(request, b_id):
	bhavan = Bhavan.objects.get(id=b_id)
	rows = [{'data':[room.room, room.vacancy], 'link':[]} for room in bhavan.room_set.all()]
	headings = ['Room', 'Vacancy']
	tables = [{'title': 'Details for ' + bhavan.name + ' bhavan', 'headings':headings, 'rows':rows}]
	return render(request, 'regsoft/tables.html', {'tables':tables})


@staff_member_required
def college_vs_bhavan(request):
	rows = list([{'data':[tc.g_l.college, tc.room.bhavan.name, tc.name, tc.event.name], 'link':[]} for tc in TeamCaptain.objects.filter(firewallz_passed=True, acco=True)])
	print rows
	headings = ['College', 'Bhavan', 'Name', 'Event']
	tables = [{'title':'Bhavans vs College', 'headings':headings, 'rows':rows}]
	return render(request,'regsoft/tables.html', {'tables':tables})


@staff_member_required
def firewallz_approved(request):
	keys=[]
	for tc in TeamCaptain.objects.filter(firewallz_passed=True):
		keys += list([{'data':[part.name, part.captain.g_l.college, part.captain.gender,part.captain.g_l.name, part.captain.event.name, part.acco, part.room], 'link':[]}] for part in tc.participant_set.all())
	
	rows = []
	for key in keys:
		for l in key:
			rows.append(l)

	headings = ['Participant', 'College', 'Gender', 'Group Leader', 'Event', 'Alloted', 'Room']
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
		rows = [{'id':part.id, 'name':part.name, 'event':part.captain.event.name, 'captain':part.captain.name, 'link':reverse('regsoft:controlz_edit', kwargs={'part_id':part.id}), 'college':g_leader.college} for part in Participants.objects.filter(captain__g_l=g_leader, firewallz_passed=True)]
		headings = ['Name', 'Event', 'Captain', 'College', 'Edit', 'Select']
		table = {'title':'Participants for ' + g_leader.college, 'rows':rows, 'headings':headings}
		return render(request, 'regsoft/controlz_home.html', {'table':table, 'gl_id':g_leader.id})

	return render(request, 'regsoft/controlz_home.html', 
		{'group_leaders':GroupLeader.objects.filter(pcr_approved=True)})


@staff_member_required
def controlz_edit(request, part_id):
	part = Participant.objects.get(id=part_id)
	if request.method=='POST':
		try:
			name = request.POST['name']
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		part.name = name
		part.save()
		request.method = 'POST'
		request.POST['barcode'] = g_l.barcode
		controlz_home(request)

		
	tc = part.captain
	g_l = tc.g_l
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
		p, created = Participation.objects.get_or_create(g_l=g_l, event=event, confirmed=True)
		if created:
			if event.max_limit == 1:
				tc = TeamCaptain.objects.create(g_l=g_l, name=name, is_single=True, event=event, firewallz_passed=True, gender=gender)
				Participant.objects.create(name=name, captain=tc, firewallz_passed=True)
			else:
				return redirect(request.META.get('HTTP_REFERER'))
		else:
			if event.max_limit == 1:
				try:
					tc1 = TeamCaptain.objects.filter(event=event, g_l=g_l)[0]
					tc = TeamCaptain.objects.create(g_l=g_l, name=name, is_single=True, event=event, firewallz_passed=True, gender=gender, email=tc1.email, phone=tc1.phone)
				except:
					tc = TeamCaptain.objects.create(g_l=g_l, name=name, is_single=True, event=event, firewallz_passed=True, gender=gender)

				part = Participant.objects.create(name=name, captain=tc, firewallz_passed=True)
			else:
				try:
					tc1 = TeamCaptain.objects.filter(event=event, g_l=g_l)[0]
					if not(event.min_limit <= tc1.total_players < event.max_limit):
						raise ValueError
				except:
					return redirect(request.META.get('HTTP_REFERER'))

				part = Participant.objects.create(captain=tc1, name=name)
				tc1.total_players+=1
				tc1.save()

		# request.POST['barcode'] = g_l.barcode
		return redirect(reverse('regsoft:home'))

	events = Event.objects.all()
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
		part in Participant.objects.get(id=part_id)
		tc = part.captain
		if tc.participant_set.all().count() == 1:
			tc.delete()
		else:
			part.delete()
			tc.total_players-=1
			tc.save()
	request.method = 'POST'
	request.POST['barcode'] = g_l.barcode
	return redirect('regosft:controlz_home')


@staff_member_required
def firewallzo_home(request):
	if request.method == 'POST':
		try:
			barcode = request.POST['barcode']
			g_l = GroupLeader.objects.get(barcode=barcode)
		except:
			return redirect(request.META.get('HTTP_REFERER'))
		parts = Participant.objects.filter(captain__g_l=g_l)
		print parts
		confirmed = [{'name':part.name,
			'college': part.captain.g_l.college,
			'event': part.captain.event.name,
			'pcr':Participation.objects.get(event=part.captain.event, g_l=part.captain.g_l).confirmed,
			'captain':part.captain.name,
			'id':part.id} for part in parts.filter(firewallz_passed=True).order_by('captain__event__name')]
		print confirmed
		unconfirmed = [{'name':part.name,
			'college': part.captain.g_l.college,
			'event': part.captain.event.name,
			'pcr':Participation.objects.get(event=part.captain.event, g_l=part.captain.g_l).confirmed,
			'captain':part.captain.name,
			'id':part.id} for part in parts.filter(firewallz_passed=False).order_by('captain__event__name')]
		print unconfirmed
		return render(request, 'regsoft/firewallzo_home.html',{'confirmed':confirmed, 'unconfirmed':unconfirmed})
	events = Event.objects.all()
	total = Participant.objects.all().count()
	passed = Participant.objects.filter(firewallz_passed=True).count()
	return render(request, 'regsoft/firewallzo_home.html', {'events':events, 'total':total, 'passed':passed})

@staff_member_required
def firewallz_swap(request):
	try:
		data = request.POST
	except:
		return redirect(request.META.get('HTTP_REFERER'))

	if 'confirm' in data['action']:
		part_ids = dict(data)['data']
		for part_id in part_ids:
			part = Participant.objects.get(id=part_id)
			part.firewallz_passed=True
			part.save()
			tc = part.captain
			if all((part.firewallz_passed for part in Participant.objects.filter(captain=tc))):
				tc.firewallz_passed=True
				tc.save()
		return redirect('regsoft:firewallz-home')
	elif 'unconfirm' in data['action']:
		part_ids = dict(data)['data']
		for part_id in part_ids:
			part = Participant.objects.get(id=part_id)
			part.firewallz_passed=False
			part.save()
			tc = part.captain
			tc.firewallz_passed=False
			tc.save()
		return redirect('regsoft:firewallz-home')
			
	return redirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def get_details(request):
	context = {}
	if request.method == 'POST':
		if 'event' in request.POST:
			event = Event.objects.get(id=request.POST['id'])
			captain_list = TeamCaptain.objects.filter(event=event)
			participant_list = []
			for captain in captain_list:
				participant_list += Participant.objects.filter(captain=captain)

			rows = []
			for participant in participant_list:
				rows.append({'data':[str(participant.name).title(), str(participant.captain.name).title(), str(participant.captain.g_l.college).title(), participant.captain.paid], 'link':[]})

			headings = ['Name', 'Captain', 'College', 'Payment']
			title = 'Participant list for ' + event.name
			print rows
		elif 'college' in request.POST:
			g_leader = GroupLeader.objects.get(id=request.POST['id'])
			captain_list = TeamCaptain.objects.filter(g_l=g_leader)
			participant_list = []
			for captain in captain_list:
				participant_list += Participant.objects.filter(captain=captain)

			rows = []
			for participant in participant_list:
				rows.append({'data':[str(participant.name).title(), str(participant.captain.name).title(), str(participant.captain.event.name).title(), participant.captain.payment], 'link':[]})

			headings = ['Name', 'Captain', 'Event', 'Payment']
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

####################    BILLINGS      #########################

@staff_member_required
def view_captain_controlz(request, gl_id):
	try:
		g_leader = GroupLeader.objects.get(id=gl_id)
	except:
		return render(request, 'pcradmin/message', {'message':'Invalid group leader'})
	c_rows = []
	u_rows = []
	c_count = 0
	u_count = 0
	for tc in TeamCaptain.objects.filter(g_l=g_leader):
		if tc.firewallz_passed == True:
			try:
				room = tc.room.room
				bhavan = tc.room.bhavan.name
			except:
				room = 'None'
				bhavan = 'None'
			if tc.if_payment:
				amount_left = tc.event.price - tc.payment
				c_rows.append({'data':[str(tc.name.title()), str(tc.event.name.title()), str(tc.total_players), tc.payment,amount_left, room, bhavan], 'link':[{'title':'Edit details', 'url':reverse('regsoft:view_captain', kwargs={'tc_id':tc.id}), }, {'title':'Show Team List','url':reverse('regsoft:show_team_list', kwargs={'tc_id':tc.id})}]})

				if not tc.payment == tc.event.price:
					c_rows[c_count]['link'].append({'title':'Make payment', 'url':reverse('regsoft:create_bill', kwargs={'tc_id':tc.id})})
				else:
					c_rows[c_count]['link'].append({'title':'Already paid/Print Bill', 'url':reverse('regsoft:print_bill', kwargs={'tc_id':tc.id})})
			else:
				amount_left = 0
				c_rows.append({'data':[str(tc.name.title()), str(tc.event.name.title()), str(tc.total_players), tc.payment,amount_left, room, bhavan], 'link':[{'title':'Edit details', 'url':reverse('regsoft:view_captain', kwargs={'tc_id':tc.id}), }, {'title':'Show Team List','url':reverse('regsoft:show_team_list', kwargs={'tc_id':tc.id})}]})
				c_rows[c_count]['link'].append({'title':'Extra Event', 'url':'#'})
				
			c_count += 1

		else:
			u_rows.append({'data':[str(tc.name.title()), str(tc.event.name.title()), str(tc.total_players)],})
			u_count += 1

	confirmed = {
		'title':'Teams confirmed by Firewallz from ' + g_leader.college,
		'headings':['Name', 'Event', 'Total Players', 'Amount Paid','Amount left','Room','Bhavan', 'Edit details', 'Team List', 'Payment Options'],
		'rows':c_rows 
	}
		# print confirmed
	unconfirmed = {
		'title':'Participants not confirmed by Firewallz from ' + g_leader.college,
		'headings':['Name', 'Event', 'Total Players'],
		'rows':u_rows
		}
	# print unconfirmed

	context = {
		'tables':[confirmed, unconfirmed]
	}

	return render(request, 'regsoft/controlz_home.html', context)

@staff_member_required
def create_bill(request, tc_id):
	captain = get_object_or_404(TeamCaptain, id=tc_id)
	if request.method == 'POST':
		data = request.POST
		bill = Bill()
		bill.two_thousands = data['twothousands']
		bill.five_hundreds = data['fivehundreds']
		bill.hundreds = data['hundreds']
		bill.fifties = data['fifties']
		bill.twenties = data['twenties']
		bill.tens = data['tens']
		amount_dict = {'twothousands':2000, 'fivehundreds':500, 'hundreds':100, 'fifties':50, 'twenties':20, 'tens':10}
		bill.amount = 0
		for key,value in amount_dict.iteritems():
			bill.amount += int(data[key])*int(value)
		try:
			bill.draft_number = data['draft_number']
		except:
			pass
		bill.draft_amount = data['draft_amount']
		
		if not (bill.amount == 0 and bill.draft_amount == 0):
			bill.captain = captain
			bill.save()
			captain.paid = True
			captain.payment = captain.payment + int(bill.amount) + int(bill.draft_amount)
			captain.save()

			return redirect(reverse('regsoft:view_captain_controlz', kwargs={'gl_id':captain.g_l.id}))

		else:
			return redirect(reverse('regsoft:create_bill', kwargs={'tc_id':tc_id}))

	amount = captain.event.price - captain.payment	
	return render(request, 'regsoft/create_bill.html', {'captain':captain, 'amount':amount})

@staff_member_required
def print_bill(request, tc_id):
	from datetime import datetime
	time_stamp = datetime.now()
	captain = TeamCaptain.objects.get(id=tc_id)
	g_leader = captain.g_l
	for part in captain.participant_set.all():
		part.controlz = True
		part.save()
	bill = Bill.objects.get(captain=captain)
	try:
		draft = bill.draft_number
	except:
		draft = ''
	payment_methods = [{'method':'Cash', 'amount':bill.amount}, {'method':'Draft #'+draft, 'amount':bill.draft_amount}]	
	total = int(bill.amount) + int(bill.draft_amount)
	return render(request, 'regsoft/print_bill.html', {'captain':captain, 'g_leader':g_leader, 'time':time_stamp, 'bill':bill, 'payment_methods':payment_methods, 'total':total})


@staff_member_required
def get_barcode(request):
	g_ls = GroupLeader.objects.all()
	for g_l in g_ls:
		bc = gen_barcode(g_l)

	return redirect('regsoft:firewallz-home')

@staff_member_required
def user_logout(request):
	logout(request)
	return redirect('regsoft:index')
