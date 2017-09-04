from django.shortcuts import render, redirect, get_object_or_404
from registrations.models import *
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
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
from django.conf import settings
from BOSM.settings import BASE_DIR
import sendgrid
import os
from sendgrid.helpers.mail import *
from registrations.sg_config import *
import xlsxwriter
from time import gmtime, strftime

try:
	import cStringIO as StringIO
except ImportError:
	import StringIO

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

		subject = request.POST['sub']
		body = Content(request.POST['body'])
		to_email = Email(request.POST['to'])
		from_email = Email('register@bits-bosm.org')
		sg = sendgrid.SendGridAPIClient(apikey=API_KEY)

		try:
			mail = Mail(from_email, subject, to_email, body)
			response = sg.client.mail.send.post(request_body=mail.get())

		except:
			print "Mail Not Sent."
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
			group_leaders = request.POST.getlist('gls')

			print group_leaders
			if group_leaders:
				if "Deactivate" == data['submit']:

					for gl_id in group_leaders:
						gl = GroupLeader.objects.get(id=gl_id)
						gl.pcr_approved = False
						user = gl.user
						user.is_active = False
						gl.save()
						user.save()
						send_status_email(gl.email, "Frozen")
					return redirect('pcradmin:index')

				elif "Activate" == data['submit']:
					for gl_id in group_leaders:
						gl = GroupLeader.objects.get(id=gl_id)
						print gl
						if gl.email_verified:
							print gl
							gl.pcr_approved = True
							user = gl.user
							gl.save()
							print user
							user.is_active = True
							user.save()
							send_status_email(gl.email, "Approved")
						else:
							error_message = 'This user has not verified its email. This is user is deactivated.'
							return render(request, 'pcradmin/message.html', {'message':error_message})
					return redirect('pcradmin:index')
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
		body = Content("text/html", "Dear User, Your account status has been changed, and is now "+status+". You can use your credentials to login to <a>bits-bosm.org/2017/registrations</a> to add teams.")

	elif status == 'Frozen':
		subject = "Account Frozen"
		body = Content("Dear User, Your account status has been changed, and is now "+status+". You can no longer log in using your credentials.")
	sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
	to_email = Email(send_to)
	from_email = Email('register@bits-bosm.org')
	#try:
	mail = Mail(from_email, subject, to_email, body)
	response = sg.client.mail.send.post(request_body=mail.get())

	#except :
	#	print "Mail Not Sent."
	return

@staff_member_required
@csrf_exempt
def confirm_events(request, gl_id):
	gl = get_object_or_404(GroupLeader, pk=gl_id,)

	if request.method == 'POST':
		data = request.POST
		try:
			confirm = data.getlist('confirm')
			print confirm

		except:
			return redirect(request.META.get('HTTP_REFERER'))
			
		for i in confirm:
			teamcaptain = TeamCaptain.objects.get(pk=int(i))
			event = teamcaptain.event
			g_l = teamcaptain.g_l
			sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
			if teamcaptain.email:
				to_email = Email(teamcaptain.email)
				name = teamcaptain.name
				if teamcaptain.if_payment :
					body = '''<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
				<pre style="font-family:Roboto,sans-serif">
				
				Greetings, %s!

				Your team has been shortlisted to participate for %s in BOSM 2017. 
				To cofirm Your participation, please make the pre-payment of %s within 3 days of receiving this mail.

				The link for pre-payment is : <a>https://paytm.com/education</a>

				<b>
				The steps for pre-payment are attached below.
				Only the captain can make the pre-payment.
				The payment for each team is mentioned below:
				</b>
				<br><br>
				<img src="https://bits-bosm.org/2017/static/images/rates.png">

				Regards,
				Ashay Anurag
				CoSSAcn (Head)
				Dept. of Publications & Correspondence, BOSM 2017
				BITS Pilani
				+91-9929022741

				'''%(name, event.name, event.price)

					subject = "Payment for BOSM '17"
					from_email = Email('register@bits-bosm.org')
					content = Content("text/html", body)
					import base64

					with open(os.path.join(BASE_DIR, "workbooks/Pre-Payment Process.pdf"), "rb") as xl_file:
						encoded_string = base64.b64encode(xl_file.read())

					attachment = Attachment()
					attachment.content = encoded_string
					attachment.filename = "Pre-Payment Process.pdf"

				else:
					body = '''<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
				<pre style="font-family:Roboto,sans-serif">
				
				Hello %s!
				Your team registration for %s has been confirmed for BOSM 2017.

				Regards,
				Ashay Anurag
				CoSSAcn (Head)
				Dept. of Publications & Correspondence, BOSM 2017
				BITS Pilani
				+91-9929022741

				'''%(name, event.name,)
					
					subject = "Confirmation for BOSM '17"
					from_email = Email('register@bits-bosm.org')
					content = Content("text/html", body)

				try:

					mail = Mail(from_email, subject, to_email, content)
					if attachment:
						mail.add_attachment(attachment)
					response = sg.client.mail.send.post(request_body=mail.get())
					p = Participation.objects.get(event=event, g_l=g_l)
					p.confirmed = True
					teamcaptain.paid = True
					teamcaptain.save()
					p.save()
				
				except :
						return render(request, 'pcradmin/message.html', {'message':'Email not sent'})
	
		return render(request, 'pcradmin/message.html', {'message':'Emails sent'})

		

	else:
		events = [p.event for p in Participation.objects.filter(g_l=gl,confirmed=False)]

		teamcaptains=[]
		for event in events:
			teamcaptains.append(list(TeamCaptain.objects.filter(g_l=gl, event=event)))

		print teamcaptains
		captains = []
		print len(teamcaptains[0]), len(teamcaptains[1])
		for i in range(0,len(teamcaptains)):
			for j in range(0,len(teamcaptains[i])):
				captains.append(teamcaptains[i][j])
		return render(request, 'pcradmin/confirm_events.html', {'teamcaptains':captains, 'g_l':gl})


@staff_member_required
def final_list_download(request):

	import xlsxwriter
	import os
	try:
		import cStringIO as StringIO
	except ImportError:
		import StringIO
	a_list = []

	try:
		xl_file = open(os.path.join(BASE_DIR, "workbooks/final_list_2017.xlsx"))
		xl_file.close()
		os.remove(os.path.join(BASE_DIR, "workbooks/final_list_2017.xlsx"))

	except:
		pass

	gleaders = GroupLeader.objects.all()

	for p in gleaders:
		a_list.append({'obj': p})
	data = sorted(a_list, key=lambda k: k['obj'].id)
	output = StringIO.StringIO()
	workbook = xlsxwriter.Workbook(os.path.join(BASE_DIR, 'workbooks/final_list_2017.xlsx'))
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

	return redirect(reverse('pcradmin:final_confirmation'))


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
		sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
		from_email = Email("no-reply@bits-bosm.org")
		to_email = Email(send_to)
		subject = sub
		content = Content("text/html", "We welcome you on behalf to BOSM '17 at BITS, Pilani. PFA the list of participating colleges.")

		import base64

		with open(os.path.join(BASE_DIR, "workbooks/final_list.xlsx"), "rb") as xl_file:
			encoded_string = base64.b64encode(xl_file.read())

		attachment = Attachment()
		attachment.content = encoded_string
		attachment.filename = "gleaders.xlsx"


		
		try:
			mail = Mail(from_email, subject, to_email, content)
			mail.add_attachment(attachment)
			response = sg.client.mail.send.post(request_body=mail.get())

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
		return render(request, 'pcradmin/final_confirmation_email.html', context)



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
def stats(request, order=None):

	return render(request, 'pcradmin/stats.html')

@staff_member_required
def stats_order(request, order=None):

	if order == 'college':

		g_ls = GroupLeader.objects.filter(email_verified=True, pcr_approved=True)
		collegewise = []
		totals = [0,0,0,0,0,0,0]
		for g_l in g_ls:

			teamcaptains = TeamCaptain.objects.filter(g_l=g_l)
			if not teamcaptains:
				continue
			entry, counts = helper_for_stats(teamcaptains)
			if entry['total']=='- -':
				continue
			entry['name'] = g_l.college
			entry['url'] = reverse('pcradmin:collegewise', kwargs={'gl_id':g_l.id})
			for i in range(7):
				totals[i] += counts[i]
			for i in ['total', 'male', 'female']:
				if entry[i] == '0 | 0': entry[i] = '- -'
			collegewise.append(entry)
		collegewise.append({'name':'Total', 'url':'#',
		 	'total':str(totals[0]) + ' | ' + str(totals[1]),
		 	'male':str(totals[2]) + ' | ' + str(totals[3]),
			'female':str(totals[4]) + ' | ' + str(totals[5]),
			'coach':str(totals[6])}
			)
		order = 'Stats Collegewise'
		return render(request, 'pcradmin/statistics.html', {'order':order, 'list' : collegewise, 'stats':True, 'name':'College'})


	if order == 'sport':
		events = Event.objects.all()
		sportwise = []
		totals = [0,0,0,0,0,0,0]
		for event in events:
			
			teamcaptains = TeamCaptain.objects.filter(event=event)
			if not teamcaptains:
				continue
			entry, counts = helper_for_stats(teamcaptains)
			if entry['total']=='- -':
				continue
			entry['name'] = event.name
			entry['url'] = reverse('pcradmin:sportwise', kwargs={'e_id':event.id})
			for i in range(7):
				totals[i] += counts[i]
			for i in ['total', 'male', 'female']:
				if entry[i] == '0 | 0': entry[i] = '- -'
			sportwise.append(entry)
		sportwise.append({'name':'Total', 'url':'#',
		 	'total':str(totals[0]) + ' | ' + str(totals[1]),
		 	'male':str(totals[2]) + ' | ' + str(totals[3]),
			'female':str(totals[4]) + ' | ' + str(totals[5]),
			'coach':str(totals[6])}
			)
		order = 'Stats Sportwise'
		return render(request, 'pcradmin/statistics.html', {'order':order, 'list' : sportwise,'stats':True, 'name':'Events'})


	if order=='master_list':
		output = StringIO.StringIO()
		workbook = xlsxwriter.Workbook(output)
		worksheet = workbook.add_worksheet('new-spreadsheet')
		date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})
		worksheet.write(0, 0, "Generated:")
		generated = strftime("%d-%m-%Y %H:%M:%S UTC", gmtime())
		worksheet.write(0, 1, generated)
		worksheet.write(1,0,"Colleges\Sport")

		g_ls = GroupLeader.objects.filter(email_verified=True, pcr_approved=True)
		events = Event.objects.all()
		
		for i,event in enumerate(events):
			worksheet.write(1,i+1, event.name)
		for i,g_l in enumerate(g_ls):

			worksheet.write(2+i,0,g_l.college)
			for j,event in enumerate(events):
				teamcaptains = TeamCaptain.objects.filter(event=event, g_l=g_l)
				entry = str(reduce(count_players_confirmed, teamcaptains,0)) + ' | ' + str(reduce(count_players, teamcaptains,0))
				if entry == '0 | 0':
					entry = '- -'
				worksheet.write(2+i, 1+j, entry)
		workbook.close()
		filename = 'MasterList.xlsx'
		output.seek(0)
		response = HttpResponse(output.read(), content_type="application/ms-excel")
		response['Content-Disposition'] = 'attachment; filename=%s' % filename
		return response


########################## HELPER function ################################

def count_players(x,y):
	return x + y.total_players

def count_players_confirmed(x,y):
	if Participation.objects.get(g_l=y.g_l, event=y.event).confirmed:
		return x + y.total_players
	else:
		return x

@staff_member_required
def stats_college(request, gl_id):
	g_l = get_object_or_404(GroupLeader, pk=gl_id)
	events = Event.objects.all()
	sportwise = []
	totals = [0,0,0,0,0,0,0]
	for event in events:
		teamcaptains = TeamCaptain.objects.filter(event=event, g_l=g_l)
		if not teamcaptains:
			continue
		entry, counts = helper_for_stats(teamcaptains)
		if entry['total']=='- -':
			continue
		entry['name'] = event.name
		entry['url'] = reverse('pcradmin:show_participants', kwargs={'gl_id':g_l.id, 'event_id':event.id})
		for i in range(7):
			totals[i] += counts[i]
		for i in ['total', 'male', 'female']:
			if entry[i] == '0 | 0': entry[i] = '- -'
		sportwise.append(entry)
	sportwise.append({'name':'Total', 'url':'#',
		'total':str(totals[0]) + ' | ' + str(totals[1]),
		'male':str(totals[2]) + ' | ' + str(totals[3]),
		'female':str(totals[4]) + ' | ' + str(totals[5]),
		'coach':str(totals[6])}
		)
		
	order = 'Stats Sportwise for ' + g_l.college
	return render(request, 'pcradmin/statistics.html', {'order':order, 'list' : sportwise,'stats':True, 'name':'Event'})

@staff_member_required
def stats_sport(request, e_id):
	event = get_object_or_404(Event, pk=e_id)
	g_ls = GroupLeader.objects.filter(pcr_approved=True, email_verified=True)
	sportwise = []
	totals = [0,0,0,0,0,0,0]
	for g_l in g_ls:
		teamcaptains = TeamCaptain.objects.filter(event=event, g_l=g_l)
		if not teamcaptains:
			continue
		entry, counts = helper_for_stats(teamcaptains)
		if entry['total']=='- -':
			continue
		entry['name'] = g_l.college
		entry['url'] = reverse('pcradmin:show_participants', kwargs={'gl_id':g_l.id, 'event_id':event.id})
		for i in range(7):
			totals[i] += counts[i]
		for i in ['total', 'male', 'female']:
			if entry[i] == '0 | 0': entry[i] = '- -'
		sportwise.append(entry)
	sportwise.append({'name':'Total', 'url':'#',
		'total':str(totals[0]) + ' | ' + str(totals[1]),
		'male':str(totals[2]) + ' | ' + str(totals[3]),
		'female':str(totals[4]) + ' | ' + str(totals[5]),
		'coach':str(totals[6])}
		)
	
	order = 'Stats Collegewise for ' + event.name
	return render(request, 'pcradmin/statistics.html', {'order':order, 'list' : sportwise,'stats':True, 'name':'College'})


######################### PDF generators  #####################
@staff_member_required
def get_list(request):

	g_l = GroupLeader.objects.all()
	return render(request, 'pcradmin/gen_pdf.html', {'pdf':True, 'gls':g_l})

@staff_member_required
def get_list_gleaders(request):

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
	return redirect('pcradmin:index')

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


def helper_for_stats(teamcaptains):
	entry = {}
	total_c = reduce(count_players_confirmed, teamcaptains,0)
	total = reduce(count_players, teamcaptains,0)
	entry['total'] = str(total_c) + ' | ' + str(total)
	teamcaptains_m = teamcaptains.filter(gender='M')
	male_c = reduce(count_players_confirmed, teamcaptains_m,0)
	male = reduce(count_players, teamcaptains_m,0)
	entry['male'] = str(male_c) + ' | ' + str(male)
	teamcaptains_f = teamcaptains.filter(gender='F')
	female_c = reduce(count_players_confirmed, teamcaptains_f,0)
	female = reduce(count_players, teamcaptains_f,0)
	entry['female'] = str(female_c) + ' | ' + str(female)
	coach = len([tc.coach for tc in teamcaptains if tc.coach])
	entry['coach'] = str(coach)
	return [entry, [total, total_c, male_c, male, female_c, female, coach]]

@staff_member_required
def show_participants(request, gl_id, event_id):
	try:
		g_l = GroupLeader.objects.get(id=gl_id)
		event = Event.objects.get(id=event_id)
		tcs = TeamCaptain.objects.filter(event=event, g_l=g_l)
	except:
		return redirect(request.META.get('HTTP_REFERER'))
	phone = ''
	email = ''
	participants = []
	for tc in tcs:
		phone += str(tc.phone) + '  '
		email += str(tc.email) + '  '
		for part in Participant.objects.filter(captain=tc):
			participants.append(part.name)
	return render(request, 'pcradmin/show_participants.html',
	{'college':g_l.college, 'event':event.name, 'phone':phone, 'email':email, 'parts':participants}
	)


@staff_member_required
def change_paid(request):
	if request.method == 'POST':
		data = request.POST
		try:
			tc_ids = dict(data['tc'])
			if not tc_ids:
				return render(request.META.get('HTTP_REFERER'))
		except:
			return render(request.META.get('HTTP_REFERER'))
		if 'paid' == data['submit']:
			x=True
		elif 'unpaid' == data['submit']:
			x=False
		for tc_id in tc_ids:
			TeamCaptain.objects.filter(id=tc_id).update(paid=x)
		
		return redirect('pcradmin:index')
	paid = []
	unpaid = []
	for participation in Participation.objects.filter(confirmed=True):
		paid.append(list(TeamCaptain.objects.filter(g_l=participation.g_l, event=participation.event,paid=True)))
		unpaid.append(list(TeamCaptain.objects.filter(g_l=participation.g_l, event=participation.event, paid=False, if_payment=True)))
	return render(request, 'pcradmin/change_paid.html', {'unpaid':unpaid, 'paid':paid})