from django.shortcuts import render, redirect, get_object_or_404
from registrations.models import *
from django.http import HttpResponseRedirect, HttpResponse
from events.models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib.auth import login, logout
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from functools import reduce
from registrations.urls import *
from django.views.decorators.csrf import csrf_exempt

@staff_member_required
def index(request):
	
	return render(request, 'pcradmin/dashboard.html', {'dashboard':True})


@staff_member_required
def sport_limit(request):
	
	events = Event.objects.order_by('name')
	return render(request, 'pcradmin/change_limits.html', {'events':events})


@staff_member_required
def sport_limit_change(request, event_id):
	
	event = get_object_or_404(Event, id=event_id)
	if request.method == 'POST':

		data = request.POST
		event.max_limit = (data['max_limit'])
		event.min_limit = (data['min_limit'])
		event.save()
		return redirect(reverse('pcradmin:sport_limit'))

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
					return render(request, 'pcradmin/message.html', {'message':'Email not sent'})

		return render(request, "pcradmin/message.html", {'email':send_to, 'message':'Email sent'})

	else:

		context = {
		'g_l':g_l,
		'to' : g_l.email,
		'subject' : "BOSM 2017",
		"body" : '',
		}
		return render(request, 'pcradmin/email_compose.html', context)

@staff_member_required
def status_change(request):
	
	if request.method == "POST":

		data = request.POST
		try:
			group_leaders = data['gls']
			if group_leaders:
				if "Deactivate" == data['submit']:

					for gl_id in group_leaders:
						gl = GroupLeader.objects.get(id=gl_id)
						gl.pcr_approved = False
						gl.user.is_active = False
						user = gl.user
						user.is_active = False
						gl.save()
						user.save()
						send_status_email(gl.email, "Frozen")
				elif "Activate" == data['submit']:
					for gl_id in group_leaders:
						gl = GroupLeader.objects.get(id=gl_id)
						if gl.email_verified:

							gl.pcr_approved = True
							gl.user.is_active = True
							user = gl.user
							gl.save()
							user.is_active = True
							user.save()
							send_status_email(gl.email, "Approved")
						else:
							error_message = 'This user has not verified its email. This is user is deactivated.'
							return render(request, 'pcradmin/message.html', {'message':error_message})
		except:	

			return redirect(request.META.get('HTTP_REFERER'))

	else:

		gl_active = GroupLeader.objects.filter(user__is_staff=False, user__is_active=True,)
		gl_inactive = GroupLeader.objects.filter(user__is_staff=False, user__is_active=False, email_verified=True)
		return render(request, 'pcradmin/status_select.html', {'active':gl_active, 'inactive':gl_inactive})


### helper function ###
def send_status_email(send_to, status):
	if status == 'Approved':
		subject = "Account Approved"
		body = "Dear User, Your account status has been changed, and is now "+status+". You can use your credentials to login to <a>bits-bosm.org/registrations</a> to add teams."

	elif status == 'Frozen':
		subject = "Account Frozen"
		body = "Dear User, Your account status has been changed, and is now "+status+". You can no longer log on using your credentials."
	email = EmailMessage(subject, body,'register@bits-bosm.org', [send_to])
	
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
				return render(request, 'pcradmin/message.html', {'message':'Email not sent'})

	return

@staff_member_required
@csrf_exempt
def confirm_events(request, gl_id):
	gl = get_object_or_404(GroupLeader, pk=gl_id,)

	if request.method == 'POST':
		data = request.POST
		try:
			confirm = data['confirm']
			for i in confirm:
				p = Participation.objects.get(pk=int(i))
				event = p.event
				g_l = p.g_l
				teamcaptain = TeamCaptain.objects.get(g_l=g_l, event=event)
				if teamcaptain.if_payment :
					send_to = teamcaptain.email
					name = teamcaptain.name
					body = '''<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
					<center><img src="http://bits-bosm.org/2016/static/docs/email_header.jpg"></center>
					<pre style="font-family:Roboto,sans-serif">
					
					Hello %s!
					Your team registration for %s has been confirmed.
					<a href='%s'>Click Here</a> to pay %d for the same.
					
					'''%(name, event.name, str(request.build_absolute_uri(reverse("registrations:paytm")) + generate_payment_token(TeamCaptain.objects.get(email=send_to))) + '/', event.price)

					email = EmailMultiAlternatives("Payment for BOSM '17", 'Click '+ str(request.build_absolute_uri(reverse("registrations:index")) + generate_payment_token(TeamCaptain.objects.get(email=send_to))) + '/' + ' to confirm.', 
												'register@bits-bosm.org', [send_to.strip()]
												)
					email.attach_alternative(body, "text/html")

					try:
						email.send()
						p.confirmed = True
						p.save()
					
					except SMTPException:
				
						try:
							bosm2016.settings.EMAIL_HOST_USER = bosm2016.email_config.config.email_host_user[1]
							bosm2016.settings.EMAIL_HOST_PASSWORD = bosm2016.email_config.config.email_host_pass[1]
							email.send()
							p.confirmed = True
							p.save()
					
						except SMTPException:
							bosm2016.settings.EMAIL_HOST_USER = bosm2016.email_config.config.email_host_user[2]
							bosm2016.settings.EMAIL_HOST_PASSWORD = bosm2016.email_config.config.email_host_pass[2]
							email.send()
							p.confirmed = True
							p.save()
		
			return render(request, 'pcradmin/message.html', {'message':'Email sent'})

		except:
			return redirect(request.META.get('HTTP_REFERER'))
		


	else:
		events = []
		for p in Participation.objects.filter(g_l=gl,confirmed=False):
			events.append(p.event)
		teamcaptains = []
		for event in events:
			teamcaptains.append(TeamCaptain.objects.get(g_l=gl, event=event))
		print teamcaptains
		for captain in teamcaptains:
			print captain
		return render(request, 'pcradmin/confirm_events.html', {'teamcaptains':teamcaptains, 'g_l':gl})

@staff_member_required
def final_confirmation(request):
	g_leaders = GroupLeader.objects.filter(pcr_approved=True)
	return render(request, 'pcradmin/final_confirm.html', {'g_leaders':g_leaders})

@staff_member_required
def final_confirmation_email(request, gl_id):
	
	g_l = get_object_or_404(GroupLeader, id=gl_id)
	if request.method == 'POST':

		sub = request.POST['sub']
		body = request.POST['body']
		send_to = request.POST['to']
		email = EmailMessage(sub, body,'register@bits-bosm.org', [send_to])

		import xlsxwriter
		try:
			import cStringIO as StringIO
		except ImportError:
			import StringIO
		a_list = []


		gleaders = GroupLeader.objects.all()

		for p in gleaders:
			a_list.append({'obj': p})
		data = sorted(a_list, key=lambda k: k['obj'].id)
		output = StringIO.StringIO()
		workbook = xlsxwriter.Workbook(output)
		worksheet = workbook.add_worksheet('new-spreadsheet')
		date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})
		worksheet.write(0, 0, "Generated:")
		from time import gmtime, strftime
		generated = strftime("%d-%m-%Y %H:%M:%S UTC", gmtime())
		worksheet.write(0, 1, generated)

		worksheet.write(1, 0, "ID")
		worksheet.write(1, 1, "Name")
		worksheet.write(1, 2, "Email ID")
		worksheet.write(1, 3, "Mobile No.")
		worksheet.write(1, 4, "College")
		worksheet.write(1, 5, "Total teams")
		worksheet.write(1, 6, "Total players")

		for i, row in enumerate(data):

			worksheet.write(i+2, 0, deepgetattr(row['obj'], 'id', 'NA'))
			worksheet.write(i+2, 1, deepgetattr(row['obj'], 'name', 'NA'))
			worksheet.write(i+2, 2, deepgetattr(row['obj'], 'email', 'NA'))
			worksheet.write(i+2, 3, deepgetattr(row['obj'], 'phone', 'NA'))
			worksheet.write(i+2, 1, deepgetattr(row['obj'], 'college', 'NA'))
			worksheet.write(i+2, 1, get_teams(row['obj']))
			worksheet.write(i+2, 1, get_players(row['obj']))

		workbook.close()
		filename = 'GroupLeaders_BOSM\'17.xlsx'
		output.seek(0)
		email.attach_file(workbook)
		
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
					return render(request, 'pcradmin/message.html', {'message':'Email not sent'})

		return render(request, "pcradmin/message.html", {'message':'Email sent to ' + send_to})

	else:

		context = {
		'g_l':g_l,
		'to' : g_l.email,
		'subject' : "BOSM 2017",
		"body" : 'This is the final confirmation email. PFA the list of all participating group leaders for BOSM \'17.'
		}
		return render(request, 'pcradmin/email_compose.html', context)



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
def list_gl(request):
	gls = GroupLeader.objects.filter(pcr_approved=True)
	return render(request, 'pcradmin/list_gls.html', {'gls':gls})

@staff_member_required
def list_tc(request, gl_id):

	g_leader = GroupLeader.objects.get(pk=gl_id)
	teamcaptains = TeamCaptain.objects.filter(g_l=g_leader)
	return render(request, 'pcradmin/list_tc.html', {'teamcaptains':teamcaptains, 'g_l':g_leader})

@staff_member_required
def search_tc(request):

	try:
		search = request.GET['search']
		attr = request.GET['attr']
		'''
		teamcaptains = TeamCaptain.objects.filter(Q(name__icontains=search) | 
			Q(g_l__college__icontains=search) | 
			Q(g_l__email__icontains=search) |
			Q(email__icontains=search))
		'''
		attribute = getattr(TeamCaptain,  attr)
		teamcaptains = TeamCaptain.objects.filter(attribute__icontains=search)
		return request(request, 'pcradmin/search_tc.html', {'teamcaptains':teamcaptains})
	except:
		return redirect(request.META.get('HTTP_REFERER'))

@staff_member_required
def team_detail(request, tc_id):

	teamcaptain = get_object_or_404(TeamCaptain, tc_id)

	return redirect(request, 'pcradmin/details.html', {'teamcaptain':teamcaptain})

@staff_member_required
def stats(request):

	return render(request, 'pcradmin/stats.html')

@staff_member_required
def stats_order(request, order):

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
		return render(request, 'pcradmin/stats.html', {'order':order, 'list' : collegewise, 'stats':True})


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
		return render(request, 'pcradmin/stats.html', {'order':order, 'list' : collegewise,'stats':True})

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
					entry[event.name] = '- -'
			both[g_l.college] = entry
		return render(request, 'pcradmin/stats_both.html', {'colleges':colleges, 'events':events_name, 'list':both,'stats':True})


########################## HELPER function ################################

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

######################### PDF generators  #####################
@staff_member_required
def get_list(request):

	g_l = GroupLeader.objects.all()
	return render(request, 'pcradmin/gen_pdf.html', {'pdf':True, 'gls':g_l})
@staff_member_required
def get_list_gleaders(request):

	import xlsxwriter
	try:
		import cStringIO as StringIO
	except ImportError:
		import StringIO
	a_list = []


	gleaders = GroupLeader.objects.all()

	for p in gleaders:
		a_list.append({'obj': p})
	data = sorted(a_list, key=lambda k: k['obj'].id)
	output = StringIO.StringIO()
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet('new-spreadsheet')
	date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})
	worksheet.write(0, 0, "Generated:")
	from time import gmtime, strftime
	generated = strftime("%d-%m-%Y %H:%M:%S UTC", gmtime())
	worksheet.write(0, 1, generated)

	worksheet.write(1, 0, "ID")
	worksheet.write(1, 1, "Name")
	worksheet.write(1, 2, "Email ID")
	worksheet.write(1, 3, "Mobile No.")
	worksheet.write(1, 4, "College")
	worksheet.write(1, 5, "Total teams")
	worksheet.write(1, 6, "Total players")

	for i, row in enumerate(data):
		"""for each object in the date list, attribute1 & attribute2
		are written to the first & second column respectively,
		for the relevant row. The 3rd arg is a failure message if
		there is no data available"""

		worksheet.write(i+2, 0, deepgetattr(row['obj'], 'id', 'NA'))
		worksheet.write(i+2, 1, deepgetattr(row['obj'], 'name', 'NA'))
		worksheet.write(i+2, 2, deepgetattr(row['obj'], 'email', 'NA'))
		worksheet.write(i+2, 3, deepgetattr(row['obj'], 'phone', 'NA'))
		worksheet.write(i+2, 1, deepgetattr(row['obj'], 'college', 'NA'))
		worksheet.write(i+2, 1, get_teams(row['obj']))
		worksheet.write(i+2, 1, get_players(row['obj']))

	workbook.close()
	filename = 'GroupLeaders_ExcelReport.xlsx'
	output.seek(0)
	response = HttpResponse(output.read(), content_type="application/ms-excel")
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	return response

@staff_member_required
def get_list_captains(request, gl_id):

	import xlsxwriter
	try:
		import cStringIO as StringIO
	except ImportError:
		import StringIO
	a_list = []

	g_leader = get_object_or_404(GroupLeader, pk=gl_id)
	captains = TeamCaptain.objects.filter(g_l=g_leader)

	for p in captains:
		a_list.append({'obj': p})
	data = sorted(a_list, key=lambda k: k['obj'].id)
	output = StringIO.StringIO()
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet('new-spreadsheet')
	date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})
	worksheet.write(0, 0, "Generated:")
	from time import gmtime, strftime
	generated = strftime("%d-%m-%Y %H:%M:%S UTC", gmtime())
	worksheet.write(0, 1, generated)

	worksheet.write(1, 0, "ID")
	worksheet.write(1, 1, "Name")
	worksheet.write(1, 2, "Email ID")
	worksheet.write(1, 3, "Mobile No.")
	worksheet.write(1, 5, "Event")
	worksheet.write(1, 6, "Total players")

	for i, row in enumerate(data):
		"""for each object in the date list, attribute1 & attribute2
		are written to the first & second column respectively,
		for the relevant row. The 3rd arg is a failure message if
		there is no data available"""

		worksheet.write(i+2, 0, deepgetattr(row['obj'], 'id', 'NA'))
		worksheet.write(i+2, 1, deepgetattr(row['obj'], 'name', 'NA'))
		worksheet.write(i+2, 2, deepgetattr(row['obj'], 'email', 'NA'))
		worksheet.write(i+2, 3, deepgetattr(row['obj'], 'phone', 'NA'))
		worksheet.write(i+2, 4, str(deepgetattr(row['obj'], 'event.name', 'NA')))
		worksheet.write(i+2, 5, deepgetattr(row['obj'], 'total_players', 'NA'))

	workbook.close()
	filename = g_leader.name + '_ExcelReport.xlsx'
	output.seek(0)
	response = HttpResponse(output.read(), content_type="application/ms-excel")
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	return response


def deepgetattr(obj, attr, default = None):

	attributes = attr.split(".")
	for i in attributes:
		try:
			obj = getattr(obj, i)

		except AttributeError:
			if default:
				return default
			else:
				raise

		return obj

def get_teams(obj):

	teams = Participation.objects.filter(g_l=obj).count()
	return str(teams)

def get_players(obj):

	total_players = 0
	for captain in obj.teamcaptain_set.all():

		total_players += captain.total_players

	return str(total_players)
	return str(teams)

############################### End PDFs ########################

@staff_member_required
def user_logout(request):

	logout(request)
	return HttpResponseRedirect('/')

######################### Custom Error Handlers  #####################

@staff_member_required
def custom_page_not_found(request):

	return render(request, 'pcradmin/404page.html')

@staff_member_required
def custom_permission_denied(request):

	return render(request, 'pcradmin/403page.html')

@staff_member_required
def custom_bad_request(request):

	return render(request, 'pcradmin/400page.html')	
