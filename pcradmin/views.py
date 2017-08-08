from django.shortcuts import render, redirect, get_object_or_404
from registrations.models import *
from events.models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth import login, logout
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from functools import reduce
from registrations.urls import *

@staff_member_required
def index(request):
	
	return render(request, 'pcradmin/dashboard.html')


@staff_member_required
def sport_limit(request):
	
	events = Event.objects.order_by('name')
	return render(request, 'pcradmin/sport_limit.html')


@staff_member_required
def sport_limit_change(request, event_id):
	
	event = get_object_or_404(Event, id=event_id)
	if request.method == 'POST':

		data = request.POST
		try:

			event.max_limit = data['max_limit']
			event.min_limit = data['min_limit']
			event.save()
			return render(request, 'pcradmin/sport_limit_saved.html', {'event':event})
		
		except: 
			print "invalid data"

	return render(request, 'pcradmin/sport_limit_change.html', {'event':event})


@staff_member_required
def email_select(request):

	group_leaders = GroupLeader.objects.all()
	return render(request, 'pcradmin/email_select.html', {'g_ls':group_leaders})


@staff_member_required
def email_compose(request, gl_id):

	g_l = get_object_or_404(GroupLeader, id=gl_id)
	if request.method == 'POST':

		sub = request.POST['sub']
		body = request.POST['body']
		send_to = request.POST['to']
		email = EmailMessage(sub, body,'register@bits-bosm.org', [send_to])
		
		try:
			email.send()
		except SMTPException:

			try:
				BOSM.settings.EMAIL_HOST_USER = BOSM.config.email_host_user[1]
				BOSM.settings.EMAIL_HOST_PASSWORD = BOSM.config.email_host_pass[1]
				email.send()
			except SMTPException:

				try :
					BOSM.settings.EMAIL_HOST_USER = BOSM.config.email_host_user[2]
					BOSM.settings.EMAIL_HOST_PASSWORD = BOSM.config.email_host_pass[2]
					email.send()	
				except:
					return render(request, 'pcradmin/email_not_sent.html')

		return render(request, "pcradmin/email_sent.html", {'email':send_to})

	else:

		context = {
		'to' : g_l.email,
		'subject' : "BOSM 2017",
		"body" : '',
		}
		return render(request, 'pcradmin/email_compose.html', context)


@staff_member_required
def status_change(request):
	
	if request.method == "POST":

		data = request.POST
		group_leaders = data['gls']
		if group_leaders:
			if "deactivate" == data['submit']:

				for gl_id in group_leaders:
					gl = GroupLeader.objects.get(id=gl_id)
					gl.pcr_approved = False
					gl.save()
					send_status_email(gl.email, "Frozen")
			elif "activate" == data['submit']:
				for gl_id in group_leaders:
					gl = GroupLeader.objects.get(id=gl_id)
					if gl.email_verified:

						gl.pcr_approved = True
						gl.save()
						send_status_email(gl.email, "Approved")
					else:
						context = {
						'email':gl.email,
						'name' : gl.name,
						'error_heading' : 'Email Unverified',
						'error_message' : 'This user has not verified its email. This is user is deactivated.'
						}
						return render(request, 'pcradmin/error.html', context)
				return render(request, 'pcradmin/success.html',)
		else:

			return redirect(request.META.get('HTTP_REFERER'))

	else:

		gl_active = GroupLeader.objects.filter(user__is_staff=False, pcr_approved=True)
		gl_inactive = GroupLeader.objects.filter(user__is_staff=False, pcr_approved=False).order_by('email_verified')
		return render(request, 'pcradmin/status_select.html', {'active':gl_active, 'inactive':gl_inactive})


### helper function ###
def send_status_email(send_to, status):
	if status == 'Approved':
		subject = "Account Approved"
	elif status == 'Frozen':
		subject = "Account Frozen"
	body = "Dear User, Your account status has been changed, and is now "+status+"."
	email = EmailMessage(sub, body,'register@bits-bosm.org', [send_to])
	
	try:
		email.send()
	except SMTPException:

		try:
			BOSM.settings.EMAIL_HOST_USER = BOSM.config.email_host_user[1]
			BOSM.settings.EMAIL_HOST_PASSWORD = BOSM.config.email_host_pass[1]
			email.send()
		except SMTPException:

			try :
				BOSM.settings.EMAIL_HOST_USER = BOSM.config.email_host_user[2]
				BOSM.settings.EMAIL_HOST_PASSWORD = BOSM.config.email_host_pass[2]
				email.send()	
			except:
				print "email not sent"
				return

	return

@staff_member_required
def confirm_events(request, gl_id):
	gl = get_object_or_404(GroupLeader, id=gl_id, pcr_approved=True)

	if request.method == 'POST':
		confirmed=True
		unconfirmed=True
		try:
			confirm = data['confirm']
			for i in confirm:
				p = Participation.objects.get(id=int(i))
				p.confirmed = True
				p.save()

				event = Participation.event
				teamcaptain = event.teamcaptain_set.filter.get(g_l=g_l)
				send_to = teamcaptain.email
				name = teamcaptain.name
				body = '''<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
					<center><img src="http://bits-bosm.org/2016/static/docs/email_header.jpg"></center>
					<pre style="font-family:Roboto,sans-serif">
					
					Hello %s!
					Your team registration for %s has been confirmed.
					<a href='%s'>Click Here</a> to pay %d for the same.
					
					'''%(name, event.name, str(request.build_absolute_uri(reverse("registrations:Index"))) + generate_payment_token(TeamCaptain.objects.get(email_id=send_to)) + '/', event.price)

				email = EmailMultiAlternatives("Payment for BOSM '17", 'Click '+ str(request.build_absolute_uri(reverse("Index"))) + generate_payment_token(TeamCaptain.objects.get(email_id=send_to)) + '/' + ' to confirm.', 
												'register@bits-bosm.org', [send_to.strip()]
												)
				email.attach_alternative(body, "text/html")

				try:
					email.send()
					
				except SMTPException:
				
					try:
						bosm2016.settings.EMAIL_HOST_USER = bosm2016.email_config.config.email_host_user[1]
						bosm2016.settings.EMAIL_HOST_PASSWORD = bosm2016.email_config.config.email_host_pass[1]
						email.send()
					
					except SMTPException:
						bosm2016.settings.EMAIL_HOST_USER = bosm2016.email_config.config.email_host_user[2]
						bosm2016.settings.EMAIL_HOST_PASSWORD = bosm2016.email_config.config.email_host_pass[2]
						email.send()
		

		except:
			confirmed=False
		
		### Probably not necessary###
		'''
		try:
			unconfirm = data['unconfirm']
			for i in unconfirm:
				p = Participation.objects.get(id=i)
				p.confirmed = False
				p.save()
		except:
			unconfirmed = False

			'''
		if not confirmed:
			return redirect(request.META.get('HTTP_REFERER'))
		context = {}
		return render(request, 'pcradmin/success.html', context)


	else:
		events = list(set([{'event':p.event, 'status':p.confirmed, 'part_id':p.id} for p in Participation.objects.filter(g_l=gl).order_by('confirmed')]))
		return render(request, 'pcradmin/confirm_events.html', {'events':events})


####### Helper function for payment token #######

def generate_payment_token(teamcaptain):

	import uuid
	token = uuid.uuid4().hex
	registered_tokens = [profile.payment_token for profile in TeamCaptain.objects.all()]

	while token in registered_tokens:
		token = uuid.uuid4().hex

	teamcaptain.payment_token = token
	teamcaptain.save()
	
	return token

###############################  END of Helper functions  ################

@staff_member_required
def list_tc(request):

	teamcaptains = TeamCaptain.objects.all()
	return render(request, 'pcradmin/list_tc.html', {'teamcaptains':teamcaptains})

@staff_member_required
def search_tc(request):

	try:
		search = request.GET['search']
		teamcaptains = TeamCaptain.objects.filter(Q(name__icontains=search) | 
			Q(g_l__college__icontains=search) | 
			Q(g_l__email__icontains=search) |
			Q(email__icontains=search))
		return request(request, 'pcradmin/search_tc.html', {'teamcaptains':teamcaptains})
	except:
		return redirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def stats(request):

	if order == 'collegewise':

		g_ls = GroupLeader.objects.filter(email_verified=True, approved=True)
		collegewise = []
		for g_l in g_ls:

			entry = {}
			entry['name'] = g_l.college
			teamcaptains = TeamCaptain.objects.filter(g_l=g_l)
			entry['total'] = str(reduce(count_players_confirmed, teamcaptains)) + ' | ' + str(reduce(count_players, teamcaptains))
			teamcaptains_m = teamcaptains.filter(gender='M')
			entry['male'] = str(reduce(count_players.confirmed, teamcaptains_m)) + ' | ' + str(reduce(count_players, teamcaptains_m))
			teamcaptains_f = teamcaptains.filter(gender='F')
			entry['female'] = str(reduce(count_players_confirmed, teamcaptains_f)) + ' | ' + str(reduce(count_players, teamcaptains_f))
			
			for i in ['total', 'male', 'female']:
				if entry[i] == '0 | 0': entry[i] = '- -'

			collegewise.append(entry)
		return render(request, 'pcradmin/stats.html', {'order':order, 'list' : collegewise})


	if order == 'Sportwise':
		events = Events.objects.all()
		sportwise = []
		for event in events:
			entry = {}
			entry['name'] = event.name
			teamcaptains = TeamCaptain.objects.filter(event=event)
			entry['total'] = str(reduce(count_players_confirmed, teamcaptains)) + ' | ' + str(reduce(count_players, teamcaptains))
			teamcaptains_m = teamcaptains.filter(gender='M')
			entry['male'] = str(reduce(count_players.confirmed, teamcaptains_m)) + ' | ' + str(reduce(count_players, teamcaptains_m))
			teamcaptains_f = teamcaptains.filter(gender='F')
			entry['female'] = str(reduce(count_players_confirmed, teamcaptains_f)) + ' | ' + str(reduce(count_players, teamcaptains_f))
			
			for i in ['total', 'male', 'female']:
				if entry[i] == '0 | 0': entry[i] = '- -'

			sportwise.append(entry)
		return render(request, 'pcradmin/stats.html', {'order':order, 'list' : collegewise})

	if order == 'both':
		g_ls = GroupLeader.objects.filter(email_verified=True, approved=True)
		colleges = [g_l.college for g_l in g_ls]
		events = Events.objects.all()
		events_name = [event.name  for event in events]
		both = {}
		for g_l in g_ls:
			entry = {}
			for event in events:
				teamcaptains = TeamCaptain.objects.filter(event=event, g_l=g_l)
				entry[event.name] = str(reduce(count_players_confirmed, teamcaptains)) + ' | ' + str(reduce(count_players, teamcaptains))
				if entry[event.name] == '0 | 0':
					entry[i] = '- -'
			both[g_l.college] = entry
		return render(request, 'pcradmin/stats_both.html', {'colleges':colleges, 'events':events_name, 'list':both})


### HELPER function ###
def count_players(x,y):
	try:
		return x.total_players + y.total_players
	except :
		return x + y.total_players

def count_players_confirmed(x,y):
	
	g_l_y = y.g_l
	event_y = y.event
	try:
		event_x = x.event
		g_l_x = x.g_l
		z=0
		if Participation.objects.get(g_l=g_l_y, event=event_y).confirmed:
			z+=y.total_players
		if Participation.objects.get(g_l=g_l_x, event=event_x).confirmed:
			z+=x.total_players
		return z
	except :
		if Participation.objects.get(g_l=g_l_y, event=event_y).confirmed:
			return x + y.total_players
		else:
			return x


