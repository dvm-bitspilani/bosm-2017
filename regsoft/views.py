from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from registrations import views, urls
from events.models import *
from django.shortcuts import render, redirect, get_object_or_404
from registrations.models import *
from regsoft.models import *
import barg
from functools import reduce
from django.http import HttpResponseRedirect

def home(request):
	return render(request, 'regsoft/base.html')

@staff_member_required
def index(request):
	if request.user.username.lower() == 'firewallz' or request.user.is_superuser:
		return redirect(reverse('regsoft:firewallz-home'))
	elif request.user.username.lower() == 'recnacc':
		return redirect(reverse('regsoft:recnacc-home'))
	elif request.user.username.lower() == 'controlz':
		return redirect(reverse('regsoft:controlz-home'))
	elif request.user.username.lower() == 'firewallzi':
		return redirect(reverse('regsoft:firewallzi-home'))
	else:
		return render(request, 'pcradmin/messsage.html', {'messsage':'Access denied.'})

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
	return render(request,'regsoft/tables.html', {'tables':tables})


@staff_member_required
def recnacc_college(request, gl_id):
	g_l = GroupLeader.objects.get(id=gl_id)
	rows = [{'data':[tc.name, tc.event.name, tc.g_l.college, tc.total_players], 'link':[{'title':'Allot', 'url':reverse('regsoft:recnacc-team', kwargs={'tc_id':tc.id})}]} for tc in TeamCaptain.objects.filter(firewallz_passed=True, g_l=g_l, if_payment=True)]
	headings = ['Team Captain', 'Event', 'College', 'No. of Players', 'Select']
	tables = [{'title':'Select Team', 'rows':rows, 'headings':headings}]
	return render(request,'regsoft/tables.html', {'tables':tables})


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
	return render(request,'regsoft/tables.html', {'tables':tables})


@staff_member_required
def college_vs_bhavan(request):
	rows = list(set([{'data':[tc.g_l.college, tc.room.bhavan.name], 'link':[]} for tc in TeamCaptain.objects.filter(firewallz_passed=True, if_payment=True, acco=True)]))
	headings = ['College', 'Bhavan']
	tables = [{'title':'Bhavans vs College', 'headings':headings, 'rows':rows}]
	return render(request,'regsoft/tables.html', {'tables':tables})


@staff_member_required
def firewallz_approved(request):
	rows = [[part.name, part.captain.g_l.college, part.captain.gender,part.captain.g_l.name, part.captain.event.name, part.acco ] for tc in TeamCaptain.objects.filter(firewallz_passed=True, if_payment=True, acco=True) for part in Participant.objects.filter(captain=tc)]
	headings = ['Participant', 'College', 'Gender', 'Group Leader', 'Event', 'Alloted']
	tables = [{'title':'Firewallz Approved Participants', 'headings':headings, 'rows':rows}]
	return render(request,'regsoft/tables.html', {'tables':tables})


##################################################   CONTROLZ ######################################################


@staff_member_required
def controlz_home(request):
	if request.method == 'POST':
		try:
			barcode = request.POST['code']
			g_leader = GroupLeader.objects.get(id=barcode[::2])
		except:
			return render(request, 'registrations/message.html', {'message':'Group Leader with the given barcode does not exist.'})

		c_rows = []
		u_rows = []
		for tc in TeamCaptain.objects.filter(g_l=g_leader):
			if tc.firewallz_passed == True:
				c_rows.append({'data':[str(tc.name.title()), str(tc.event.name.title()), str(tc.total_players), tc.paid], 'links':[{'title':'Edit details', 'url':reverse('regsoft:view_captain', kwargs={'tc_id':tc.id}), }, {'title':'Show Teamm List','url':reverse('regsoft:show_team_list', kwargs={'tc_id':tc.id})}]})

				if not tc.paid:
					c_rows[1]['links'].append({'title':'Make payment', 'url':reverse('regsoft:payment', kwargs={'tc_id':tc.id})})
				else:
					c_rows[1]['links'].append({'title':'Already paid', 'url':'#'})

			else:
				u_rows.append({'data':[str(tc.name.title()), str(tc.event.name.title()), str(tc.total_players)],})

		confirmed = {
			'title':'Participants confirmed by Firewallz',
			'headings':['Name', 'Event', 'Total Players', 'Paid', 'Edit details', 'Team List', 'Payment'],
			'rows':c_rows
		}
		unconfirmed = {
			'title':'Participants not confirmed by Firewallz',
			'headings':['Name', 'Event', 'Total Players'],
			'rows':u_rows
		}

		context = {
			'tables':[confirmed, unconfirmed]
		}

		return render(request,'regsoft/tables.html', context)

	else:
		return render(request, 'regsoft/firewallz_home.html')

@staff_member_required
def view_captain(request, tc_id):

	captain = get_object_or_404(TeamCaptain, id=tc_id)
	##### DELETE/ADD PARTICIPANT #####
	if request.method == 'POST':
		task = request.POST['task']
		if 'delete' == task:
			participant_list = request.POST.getlist('remove')
			for p in participant_list:
				Participant.objects.remove(p)

		elif 'add' == task:
			new_list = request.POST.getlist('increase')
			if captain.total_players + new_list.count() > captain.event.max_limit:
				return render(request, 'registrations/message.html', {'message':'Error hai bro!'})
			
			else:
				for part in new_list:
					Participant.objects.create(name=part, captain=captain)
					Participant.save()

		elif 'change' == task:
			data = request.POST.pop(0)
			for key,value in data:
				participant = Participant.objects.get(id=key)
				participant.name = value
				participant.save()

	participant_list = Participant.objects.filter(captain=captain)
	rows = []
	for p in participant_list:
		rows.append({'data':[str(p.name).title(), p.firewallz_passed, ]})
	tables = {
		'headings':['Participant Name', 'Firewallz Approved', 'Delete Participant'],
		'rows':rows,
		'title':'Edit Participants for ' + captain.event.name + ' ' + captain.g_l.college
	}

	return render(request, 'regsoft/tables.html', {'tables':[tables]})



@staff_member_required
def firewallzo_home(request):
	if request.method == 'POST':
		try:
			barcode = request.POST['barcode']
			g_l = GroupLeader.objects.get(barcode=barcode)
		except:
			return render(request.META.get('HTTP_REFERER'))
		parts = Participant.objects.filter(captain__g_l=g_l)
		confirmed = [{'name':part.name,
			'college': part.captain.g_l.college,
			'event': part.captain.event.name,
			'pcr':Participation.objects.get(event=part.captain.event, g_l=part.captain.g_l).confirmed,
			'id':part.id} for part in parts.filter(firewallz_passed=True).order_by('captain.event.name')]
		unconfirmed = [{'name':part.name,
			'college': part.captain.g_l.college,
			'event': part.captain.event.name,
			'pcr':Participation.objects.get(event=part.captain.event, g_l=part.captain.g_l).confirmed,
			'id':part.id} for part in parts.filter(firewallz_passed=False).order_by('captain.event.name')]
		
		total = Participant.objects.all().count()
		passed = Participation.objects.filter(firewallz_passed=True).count()
		return render(request, 'regsoft/firewallzo_home.html',
			{'confirmed':confirmed, 'unconfirmed':unconfirmed, 'total':total, 'passed':passed})

	events = Event.objects.all()
	total = Participant.objects.all().count()
	passed = Participation.objects.filter(firewallz_passed=True).count()
	return render(request, 'regsoft/firewallz_home.html', {'events':events, 'total':total, 'passed':passed})

@staff_member_required
def firewallz_swap(request):
	try:
		data = request.POST
	except:
		return render(request.META.get('HTTP_REFERER'))

	if 'confirm' in data['submit']:
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
	elif 'unconfirm' in data['submit']:
		part_ids = dict(data)['data']
		for part_id in part_ids:
			part = Participant.objects.get(id=part_id)
			part.firewallz_passed=False
			part.save()
			tc = part.captain
			tc.firewallz_passed=False
			tc.save()
		return redirect('regsoft:firewallz-home')
			
	return render(request.META.get('HTTP_REFERER'))

	


@staff_member_required
def get_details(request):
	if request.method == 'POST':
		if 'event' in request.POST:
			event = Event.objects.get(id=request.POST['id'])
			captain_list = TeamCaptain.objects.filter(event=event)
			participant_list = []
			for captain in captain_list:
				participant_list += Participant.objects.filter(captain=captain)

			rows = []
			for participant in participant_list:
				rows.append((str(participant.name).title(), str(participant.captain.name).title(), str(participant.captain.g_l.college).title(), participant.captain.paid))

			headings = ['Name', 'Captain', 'College', 'Payment']
			title = 'Participant list for ' + event.name

		elif 'college' in request.POST:
			g_leader = GroupLeader.objects.get(college=request.POST['college'])
			captain_list = TeamCaptain.objects.filter(g_l=g_leader)
			participant_list = []
			for captain in captain_list:
				participant_list += Participant.objects.filter(captain=captain)

			rows = []
			for participant in participant_list:
				rows.append((str(participant.name).title(), str(participant.captain.name).title(), str(participant.captain.event.name).title(), participant.captain.paid))

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
	
	return render(request, 'regsoft/controlz-details.html', context)

####################    BILLINGS      #########################

@staff_member_required
def view_captains_controlz(request, gl_id):
	g_leader = GroupLeader.objects.get(id=gl_id)
	c_rows = []
	paid_captains = TeamCaptain.objects.filter(g_l=g_leader, paid=True)
	for captain in paid_captains:
		c_rows.append({'data':[str(captain.name).title(), str(g_leader.name).title(), str(g_leader.college).title(), captain.total_players, str(captain.gender).title(), str(captain.event.name).title()], 'links':[{'title':'Print Receipt', 'url':reverse('regsoft:print_bill', kwargs={'tc_id':captain.id})}]})
	u_rows = []
	unpaid_captains = TeamCaptain.objects.filter(g_l=g_leader, paid=False)
	for captain in paid_captains:
		u_rows.append({'data':[str(captain.name).title(), str(g_leader.name).title(), str(g_leader.college).title(), captain.total_players, str(captain.gender).title(), str(captain.event.name).title()], 'links':[{'title':'Create Bill', 'url':reverse('regsoft:create_bill', kwargs={'tc_id':captain.id})}]})

	confirmed = {
		'title':'Paid teams from ' + g_leader.college,
		'headings' : ['Captain Name', 'Group Leader', 'College', 'Total Players', 'Gender', 'Event', 'Print Receipt'],
		'rows':c_rows,
	}
	unconfirmed = {
		'title':'Unpaid teams from ' + g_leader.college,
		'headings' : ['Captain Name', 'Group Leader', 'College', 'Total Players', 'Gender', 'Event', 'Create Bill'],
		'rows':u_rows,
	}

	context = {
		'tables':[confirmed, unconfirmed],
	}
	return render(request, 'regsoft/tables.html', context)

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
			bill.amount += data[key]*value
		
		if bill.amount == 0:
			try:
				bill.draft_number = data['draft_number']
			except:
				pass
			bill.draft_amount = data['draft_amount']
		
		if not (bill.amount == 0 and bill.draft_amount == 0):
			bill.captain = captain
			bill.save()
			captain.paid = True
			captain.save()

			return redirect(reverse('regsoft:view_captains_controlz', kwargs={'gl_id':captain.g_l.id}))

		else:
			return redirect(reverse('regsoft:create_bill', kwargs={'tc_id':tc_id}))
		
	return render(request, 'regsoft/create_bill.html')

@staff_member_required
def print_bill(request, tc_id):
	from datetime import datetime
	time_stamp = datetime.now()
	captain = TeamCaptain.objects.get(id=tc_id)
	g_leader = captain.g_l
	return render(request, 'regsoft/receipt.html', {'captain':captain, 'g_leader':g_leader, 'time':time_stamp})

@staff_member_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/')