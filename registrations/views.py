from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives

from .models import *
from events.models import *
from .forms import *

import random

def index(request):

	user = request.user

	if user.is_authenticated():

		g_leader = GroupLeader.objects.get(user=user)
		participation_list = Participation.objects.filter(g_l=g_leader)

		return render ...

	else:

		if request.method == 'POST':

			uform = UserForm(data=request.POST)
			pform = GroupLeaderForm(data=request.POST)

			if uform.is_valid() and pform.is_valid():

				user = uform.save()
				user.set_password(user.password)
				user.is_active = False
				user.save()
				g_l_profile = pform.save(commit=False)
				g_l_profile.user = user
				g_l_profile.save()

				send_to = request.POST["email_id"]
				name = request.POST["name"]
				body = '''<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
				<center><img src="http://bits-bosm.org/2016/static/docs/email_header.jpg"></center>
				<pre style="font-family:Roboto,sans-serif">
Hello %s!

Thank you for registering!

Greetings from BITS Pilani!

It gives me immense pleasure in inviting your institute to the 32nd edition of BITS Open Sports Meet (BOSM), the annual national sports meet of Birla Institute of Technology & Science, Pilani, India. This year, BOSM will be held from September 15th to 19th.             

Kindly go through the invite attached with this email and apply through our website www.bits-bosm.org. Applications close on 31st August 2016 at 1700 hrs.            

Please apply as soon as possible to enable us to confirm your participation at the earliest.             

We would be really happy to see your college represented at our sports festival.            

We look forward to seeing you at BOSM 2016.

<a href='%s'>Click Here</a> to verify your email.

P.S: THIS EMAIL DOES NOT CONFIRM YOUR PRESENCE AT BOSM 2017. YOU WILL BE RECEIVING ANOTHER EMAIL FOR THE CONFIRMATION OF YOUR PARTICIPATION. 

Regards,
CoSSAcn (Head)
Dept. of Publications & Correspondence, BOSM 2017
BITS Pilani
+91-7240105158, +91-9829491835, +91-9829493083, +91-9928004772, +91-9928004778
pcr@bits-bosm.org
</pre>
				'''%(name, str(request.build_absolute_uri(reverse("Index"))) + generate_email_token(GroupLeader.objects.get(email_id=send_to)) + '/')

				email = EmailMultiAlternatives("Registration for BOSM '17", 'Click '+ str(request.build_absolute_uri(reverse("Index"))) + generate_email_token(GroupLeader.objects.get(email_id=send_to)) + '/' + ' to confirm.', 
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

				return render()

			else:

				print uform.errors, pform.errors

		else:

			uform = UserForm()
			pform = GroupLeaderForm()

			return render(request, 'registrations/index.html', {'uform':uform, 'pform':pform}) 


############# Helper functions for Django Email ##########

def generate_email_token(gleader):

	import uuid
	token = uuid.uuid4().hex
	registered_tokens = [profile.email_token for profile in GroupLeader.objects.all()]

	while token in registered_tokens:
		token = uuid.uuid4().hex

	gleader.email_token = token
	gleader.save()
	
	return token

def authenticate_email_token(token):

	try:
		gleader = GroupLeader.objects.get(email_token=token)
		gleader.email_verified = True
		gleader.email_token = None
		gleader.user.is_active = True
		gleader.save()

		return gleader

	except ObjectDoesNotExist:

		return False


#################   End of helper functions  ####################

def email_confirm(request, token):
	
	member = email_authenticate_token(token)
	
	if member:

		context = {
			'error_heading': 1,
			'error_message': 'Your email has beeen verified. Your username and password can now be used to login at <a>bits-bosm.org.</a>',
		}
	else:
		context = {
			'status': 0,
			'error_heading': "Invalid Token",
			'error_message': "Sorry! This is an invalid token. Email couldn't be verified.",
		}
	return render()

def user_login(request):

	context = RequestContext(request)

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				if user.is_staff:
					login(request, user)
					if user.username == 'pcradmin':
						return HttpResponseRedirect(reverse('pcradmin:dashboard'))
					else:
						return HttpResponseRedirect(reverse('regsoft:home'))
				else:
					login(request, user)
					return HttpResponseRedirect('/')
			else:
				context = {'error_heading' : "Account Inactive", 'error_message' :  'Your account is currently INACTIVE. To activate it, call the following members of the Department of Publications and Correspondence. Karthik Maddipoti: +91-7240105158, Additional COntacts:- +91-9829491835, +91-9829493083, +91-9928004772, +91-9928004778 - pcr@bits-bosm.org .'}
				return render()
		else:
			context = {'error_heading' : "Invalid Login Credentials", 'error_message' :  'Invalid Login Credentials. Please try again'}
			return render()
	else:
		return render()

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def show_sports(request):

	return JsonResponse({'status':1})

@login_required
def add_sports(request):

	if request.method == 'POST':

		id_list = request.POST.getlist('id_list[]')
		g_leader = GroupLeader.objects.get(user=request.user)

		for id in id_list:

			participation = Participation()
			participation.g_l = g_leader
			participation.event = Event.objects.get(pk=id)

			participation.save()

		#participation_list = Participation.objects.filter(g_l=g_leader)
		#return JsonResponse({'status':0,'participations':participation_list})

		return HttpResponseRedirect('/')

@login_required
def remove_sports(request):

	if request.method == 'POST':

		id_list = request.POST.getlist('id_list[]')
		g_leader = GroupLeader.objects.get(user=request.user)

		for e_id in id_list:

			event = Event.objects.get(pk=e_id)
			Participation.objects.get(g_l=g_leader, event=event).delete()

		#participation_list = Participation.objects.filter(g_l=g_leader)
		#return JsonResponse({'status':0,'participations':participation_list})

		return HttpResponseRedirect('/')

@login_required
def register_captain(request, event_id):
	
	if request.method == 'POST':
		data = request.POST
		user = request.user
		tc_form = TeamCaptainForm(data)

		if tc_form.is_valid():
			
			event = Event.objects.get(id=event_id)
			teamCaptain = tc_form.save(commit=False)
			teamCaptain.event.add(event)
			g_l = GroupLeader.objects.get(user=user)
			
			if Event.objects.get(event=event, g_l=g_l).exists():
				
				teamCaptain.g_l = g_l
				participants = request.POST.getlist['participants']
				
				if participants:
					
					teamCaptain.is_single = False
					teamCaptain.save()
					
					if (event.max_limit>=participants.count()>=event.min_limit):
						for part in participants:
							if part:
								Participant.objects.create(captain=teamCaptain, name = part)
						teamCaptain.total_players = len(participants) + 1
						teamCaptain.save()
						return render
				
				else:
					
					teamCaptain.is_single = True
					if event.min_limit == event.max_limit == 1:
						teamCaptain.save()

						return render()

					else:

						print "errors"
		
			else:
					print "errors"

		else:
			return render()
		
	else:
		
		form = TeamCaptainForm()
		count = Event.objects.get(id=event_id)
		
		return render()
'''
@login_required
def add_players(request):

	event_id = request.POST["event_id"]
	event = get_object_or_404(Event, event_id)
	user = request.user

	g_l = GroupLeader.objects.get(user=user)

	if Event.objects.get(event=event, g_l=g_l).exists():

		if request.method == "POST":

			player_name = request.POST["player_name"]
			participant = Participant()
			participant.name = player_name
			participant.captain = TeamCaptain.objects.get(event=event, g_l=g_l)
			participant.save()

			return ...

		else:

			return ...

	else:

		print "error"

'''

@login_required
def remove_players(request, event_id, participant_id):

	event = Event.objects.get(id=event_id)
	g_l = GroupLeader.objects.get(user=request.user)

	if Event.objects.get(event=event, g_l=g_l).exists():

		Participant.objects.get(id=participant_id).remove()

		return render()

	else:

		print "error"

@login_required
def add_extra_event(request, participant_id):

	participant = Participant.objects.get(id=participant_id)
	groupleader = GroupLeader.objects.get(user=request.user)

	if participant__captain__g_l == groupleader:

		if request.method == "POST":

			id_list = request.POST.getlist('id_list[]')

			for e_id in id_list:

				event = Event.objects.get(id=e_id)
				TeamCaptain.objects.create(name=participant.name, g_l=groupleader,event=event)

		else:

			event_set = Event.objects.filter(min_limit=1, max_limit=1) and not Event.teamcaptain_set.filter(name=participant.name, g_l=groupleader)

			return render()

@login_required
def transport(request):

	if request.method == "POST":

		transport = Transport()
		transport.g_l = GroupLeader.objects.get(user=request.user)
		transport.departure = request.POST["departure"]
		transport.arrival = request.POST["arrival"]
		transport.no_of_passengers = request.POST["no_of_passengers"]

		transport.save()

		return render()

	else:

		return render()

@login_required
def render_list(request):

	user = request.user
	g_l = GroupLeader.objects.get(user=user)
	captain_list = g_l.teamcaptain_set.all()

	return render(request, 'registrations/list.html', {'user':user, 'captain_list':captain_list})

