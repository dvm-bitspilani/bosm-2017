from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import *
from events.models import *
from .forms import *
import random
from django.core.urlresolvers import reverse
import json

@login_required(login_url='registrations:login')
def index(request):

	user = request.user
	g_l = GroupLeader.objects.get(user=user)
	events_added = [part.event for part in Participation.objects.filter(g_l=g_l)]
	return render(request, 'registrations/index.html', {'user':user, 'added_events':events_added, 'g_l':g_l})


def signup_view(request):

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

			send_to = request.POST["email"]
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
			'''%(name, str(request.build_absolute_uri(reverse("registrations:index"))) + generate_email_token(GroupLeader.objects.get(email=send_to)) + '/')

			email = EmailMultiAlternatives("Registration for BOSM '17", 'Click '+ str(request.build_absolute_uri(reverse("registrations:email_confirm", kwargs={'token':generate_email_token(GroupLeader.objects.get(email=send_to))})))  + '/' + ' to confirm.', 
											'register@bits-bosm.org', [send_to.strip()]
											)
			email.attach_alternative(body, "text/html")

			try:
				email.send()
			
			except SMTPException:
				print "email not sent"
				# try:
				# 	BOSM.settings.EMAIL_HOST_USER = BOSM.config.email_host_user[1]
				# 	BOSM.settings.EMAIL_HOST_PASSWORD = BOSM.config.email_host_pass[1]
				# 	email.send()
				# except SMTPException:
				# 	BOSM.settings.EMAIL_HOST_USER = BOSM.config.email_host_user[2]
				# 	BOSM.settings.EMAIL_HOST_PASSWORD = BOSM.config.email_host_pass[2]
				# 	email.send()

			message = "A confirmation link has been sent to %s. Kindly click on it to verify your email address." %(send_to)
			return render(request, 'registrations/message.html', {'message':message})

		else:

			message = str(uform.errors) + str(pform.errors)
			return render(request, 'registrations/message.html', {'message':message, 'url':request.META.get('HTTP_REFERER')})				

	else:

		uform = UserForm()
		pform = GroupLeaderForm()

		return render(request, 'registrations/signup.html', {'uform':uform, 'pform':pform})	


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
		gleader.save()

		return gleader

	except ObjectDoesNotExist:

		return False


#################   End of helper functions  ####################

def email_confirm(request, token):
	
	member = authenticate_email_token(token)
	
	if member:

		context = {
			'error_heading': 1,
			'message': 'Your email has beeen verified. Please wait for further correspondence from the Department of PCr, BITS, Pilani>',
		}
	else:
		context = {
			'status': 0,
			'error_heading': "Invalid Token",
			'message': "Sorry! This is an invalid token. Email couldn't be verified.",
		}
	return render(request, 'registrations/message.html', context)
@csrf_exempt
def user_login(request):

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				if user.is_staff:
					login(request, user)
					if user.username == 'pcradmin':
						return HttpResponseRedirect(reverse('pcradmin:index'))
					else:
						return HttpResponseRedirect(reverse('regsoft:home'))
				else:
					login(request, user)
					return HttpResponseRedirect(reverse('registrations:index'))
			else:
				context = {'error_heading' : "Account Inactive", 'message' :  'Your account is currently INACTIVE. To activate it, call the following members of the Department of Publications and Correspondence. Karthik Maddipoti: +91-7240105158, Additional COntacts:- +91-9829491835, +91-9829493083, +91-9928004772, +91-9928004778 - pcr@bits-bosm.org .'}
				return render(request, 'registrations/message.html', context)
		else:
			context = {'error_heading' : "Invalid Login Credentials", 'message' :  'Invalid Login Credentials. Please try again'}
			return render(request, 'registrations/message.html', context)

	else:
		return render(request, 'registrations/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('registrations:index')

def show_sports(request):
	return render(request, 'registrations/manage_sports.html')

@csrf_exempt
def manage_sports(request):

	user = request.user
	g_l = GroupLeader.objects.get(user=user)
	if not request.method=='POST':
#[{'name':'col', 'id':1},{'name':'as', 'id':2},]
		all_events = [{'name':event.name, 'id':event.id} for event in Event.objects.all()]
		events_added = [{'name':part.event.name, 'id':part.event.id} for part in Participation.objects.filter(g_l=g_l)]
		if events_added:
			x=1
			events_left = [ i for i in all_events if i not in events_added]
		else:
			x=0
			events_left = all_events
		return JsonResponse({'x':x, 'status':1, 'events_added':events_added, 'events_left':events_left})

	else:
		data = dict(request.POST)
		print data
		try:

			events_added = data['sportsadded[]']
			for e_id in events_added:
				event = get_object_or_404(Event, id=e_id)
				try:
					part = Participation.objects.get(g_l=g_l, event=event)
					continue
				except:
					Participation.objects.create(g_l=g_l, event=event)
		except KeyError:
			print "no added sports"
		try:

			events_left = data['sportsleft[]']
			for e_id in events_left:
				event = get_object_or_404(Event, id=e_id)
				try:
					part = Participation.objects.get(g_l=g_l, event=event)
					try:
						tc = TeamCaptain.objects.filter(event=event, g_l=g_l)
						tc.delete()
					except:
						print "no team registered in this event"
					part.delete()

				except:
					continue
		except KeyError:
			print "no sports left"
		return JsonResponse({'status':1})


"""

@login_required
def add_sports(request):

	if request.method == 'POST':

		id_list = request.POST.getlist('id_list[]')
		g_leader = GroupLeader.objects.get(user=request.user)

		if id_list:

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

		return HttpResponseRedirect('/')


"""

@login_required
def register_captain(request, event_id):
	
	if request.method == 'POST':
		data = request.POST
		print data
		user = request.user
		tc_form = TeamCaptainForm(data)
		event = Event.objects.get(id=event_id)
		g_l = GroupLeader.objects.get(user=user)

		if tc_form.is_valid():
			
			teamCaptain = tc_form.save(commit=False)
			teamCaptain.event = event
			
			try :
				part = Participation.objects.get(event=event, g_l=g_l)
				teamCaptain.g_l = g_l
				teamCaptain.save()
				Participant.objects.create(captain=teamCaptain, name=teamCaptain.name)
				try:
					participants = [i for i in dict(request.POST)['participants'] if i]
				except:
					participants = []
				if participants:
					
					teamCaptain.is_single = False
					teamCaptain.save()
					if (event.max_limit>len(participants)>=event.min_limit-1):
						for part in participants:
							Participant.objects.create(captain=teamCaptain, name = part)
						teamCaptain.total_players = len(participants) + 1
						teamCaptain.save()
						return redirect(reverse('registrations:add_extra_templ', kwargs={'tc_id':teamCaptain.id}))
					
					else:
						return render(request, 'registrations/message.html', {'user':user,'message':'Invalid details filled.'})
				
				else:
					
					teamCaptain.is_single = True
					if event.min_limit == event.max_limit == 1:
						teamCaptain.save()
						return redirect(reverse('registrations:add_extra_templ', kwargs={'tc_id':teamCaptain.id}))
					else:
						return render(request, 'registrations/message.html', {'user':user,'message':'Invalid details filled.'})
		
			except:
				return render(request, 'registrations/message.html', {'user':user,'message':'Invalid access'})

		else:
			return render(request, 'registrations/message.html', {'user':user,'message':tc_form.errors})
		return redirect(reverse('registrations:show'))
	else:
		# form = TeamCaptainForm()
		user=request.user
		g_l = GroupLeader.objects.get(user=user)
		event = Event.objects.get(id=event_id)
		try:
			tc = TeamCaptain.objects.get(g_l=g_l, event=event)
			if event.max_limit != 1:
				data = {}
				data['tc'] = tc.name
				data['participants'] = [part.name for part in Participant.objects.filter(captain=tc)]
				data['url'] = reverse('registrations:add_extra_templ', kwargs={'tc_id':tc.id})
				return render(request, 'registrations/participants.html', data)
		except Exception, e:
			print e	
		part = get_object_or_404(Participation, event=event, g_l=g_l)
		return render(request, 'registrations/register_captain.html', {'event':event})

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



@login_required
def remove_players(request, event_id, participant_id):

	event = Event.objects.get(id=event_id)
	g_l = GroupLeader.objects.get(user=request.user)

	if Event.objects.get(event=event, g_l=g_l).exists():

		Participant.objects.get(id=participant_id).remove()

		###return render(request, 'registrations/<template>', {'user':user, 'count':count})
		###return JsonResponse()

	else:

		return render(request, 'registrations/message.html', {'message':'Player does not exist.'})

'''

@login_required
def add_extra_event_templ(request, tc_id):
	get_object_or_404(TeamCaptain, id=tc_id)
	event_set =  Event.objects.filter(min_limit=1, max_limit=1)
	print event_set
	return render(request, 'registrations/add_extra_event.html',{'tc_id':tc_id, 'events':event_set})

@csrf_exempt
@login_required
def add_extra_event(request, tc_id):

	groupleader = GroupLeader.objects.get(user=request.user)
	teamCaptain = TeamCaptain.objects.get(id=tc_id)
	participants = Participant.objects.filter(captain=teamCaptain)

	if request.method == "POST":
		data = request.POST
		print data
		for p_id, e_id in data.iteritems():
			print p_id, e_id
			if e_id!='0':
				participant = Participant.objects.get(id=p_id)

				event = Event.objects.get(id=e_id)

				tc = TeamCaptain(name=participant.name, g_l=groupleader,event=event, if_payment=False)
				tc.save()
				Participant.objects.create(name=tc.name, captaain=tc)
		return JsonResponse({'status':1})
	event_set =  [{'name':event.name, 'id':event.id} for event in Event.objects.filter(min_limit=1, max_limit=1)]
	if participants:
		players = [{'name':part.name, 'id':part.id} for part in participants]
	data = {'participants':players, 'events':event_set}
	return JsonResponse(data)

@login_required
def transport(request):

	user = request.user
	if request.method == "POST":

		transport = Transport()
		transport.g_l = GroupLeader.objects.get(user=request.user)
		transport.departure = request.POST["departure"]
		transport.date = request.POST["date"]
		transport.no_of_passengers = request.POST["no_of_passengers"]
		transport.save()

	return render(request, 'registrations/transport.html', {'user':user})

@login_required
def render_list(request):

	user = request.user
	g_l = GroupLeader.objects.get(user=user)
	captain_list = g_l.teamcaptain_set.all()

	return render(request, 'registrations/list.html', {'user':user, 'captain_list':captain_list})



##################################################### PayTM ###########################################################

def paytm_request(request, token):

	teamcaptain = TeamCaptain.objects.get(payment_token=token)

	from django.conf import settings
	import Checksum

	MERCHANT_KEY = settings.PAYTM_MERCHANT_KEY
	MERCHANT_ID = settings.PAYTM_MERCHANT_ID
	CALLBACK_URL = settings.HOST_URL + settings.PAYTM_CALLBACK_URL
	# Generating unique temporary ids
	order_id = Checksum.__id_generator__()
	teamcaptain.order_id = order_id
	bill_amount = teamcaptain.event.price
	name = teamcaptain.name + ' ' + teamcaptain.event.name
	if bill_amount:

		data_dict = {
                    'MID':MERCHANT_ID,
                    'ORDER_ID':order_id,
                    'TXN_AMOUNT': bill_amount,
                    'CUST_ID': name,
                    'INDUSTRY_TYPE_ID':'Retail',
                    'WEBSITE':'DIYtestingweb',   #testing phase
                    'CHANNEL_ID':'WEB',
                    'CALLBACK_URL':CALLBACK_URL,
                }
		param_dict = data_dict
		param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(data_dict, MERCHANT_KEY)
		return render(request,"payment.html",{'paytmdict':param_dict})
	return HttpResponse("Bill Amount Error.")

@login_required
@csrf_exempt
def response(request):
    if request.method == "POST":
        MERCHANT_KEY = settings.PAYTM_MERCHANT_KEY
        data_dict = {}
        for key in request.POST:
            data_dict[key] = request.POST[key]
        verify = Checksum.verify_checksum(data_dict, MERCHANT_KEY, data_dict['CHECKSUMHASH'])
        if verify:
            teamcaptain = TeamCaptain.objects.get(order_id=request.POST["ORDERID"])
            teamcaptain.paid = True
            return render(request,"response.html",{"paytm":data_dict})
        else:
            return HttpResponse("checksum verify failed")
    return HttpResponse(status=200)



################################################## End of PayTM #######################################################