from django.shortcuts import render
from registrations.models import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from registrations.models import *
from events.models import *
from registrations.views import *
from django.views.decorators.csrf import csrf_exempt
import sendgrid
import os
from sendgrid.helpers.mail import *
from registrations.sg_config import *

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.response import Response
from .serializers import *
from rest_framework.views import APIView
from rest_framework import status


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def api_test(request):
	g_leader = GroupLeader.objects.get(user=request.user)
	g_l_serializer = GroupLeaderSerializer(g_leader)
	captains = TeamCaptain.objects.filter(g_l=g_leader)
	captains_serializer = TeamCaptainSerializer(captains,many=True)
	return Response({'user':unicode(request.user), 'g_leader':g_l_serializer.data, 'captains':captains_serializer.data})

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def index(request):
	g_leader = GroupLeader.objects.get(user=request.user)
	g_l_serializer = GroupLeaderSerializer(g_leader)
	captains = TeamCaptain.objects.filter(g_l=g_leader)
	captains_serializer = TeamCaptainSerializer(captains,many=True)
	return Response({'user':unicode(request.user), 'g_leader':g_l_serializer.data, 'captains':captains_serializer.data})

@api_view(['POST'])
@permission_classes((AllowAny,))
def user_login(request, format=None):
    
	username = request.data['username']
	password = request.data['password']

	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)
			content = {
        'user': unicode(request.user),
        'auth': unicode(request.auth), 
    }
		else:
			content = {'Error': 'Inactive'}

	else:
		content = {'Error':'Invalid credentials'}

	return Response(content)

@api_view(['POST', 'GET'])
@permission_classes((AllowAny, ))
def create_user(request):

	user_serializer = UserSerializer(data=request.data)

	if user_serializer.is_valid():

		user = user_serializer.save()
		user.is_active = False
		user.save()


		send_to = request.data['profile']['email']
		name = request.data['profile']['name']
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
			'''%(name, str(request.build_absolute_uri(reverse("registrations:index"))) + 'email_confirm/' + generate_email_token(GroupLeader.objects.get(email=send_to)) + '/')

			# email = EmailMultiAlternatives("Registration for BOSM '17", 'Click '+ str(request.build_absolute_uri(reverse("registrations:email_confirm", kwargs={'token':generate_email_token(GroupLeader.objects.get(email=send_to))})))  + '/' + ' to confirm.', 
			# 								'register@bits-bosm.org', [send_to.strip()]
			# 								)
			# email.attach_alternative(body, "text/html")
		sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
		from_email = Email('register@bits-bosm.org')
		to_email = Email(send_to)
		subject = "Registration for BOSM '17"
		content = Content('text/html', body)

		try:
			mail = Mail(from_email, subject, to_email, content)
			response = sg.client.mail.send.post(request_body=mail.get())
		except :
			return Response({'message':'Email sending failed.'})

		message = "A confirmation link has been sent to %s. Kindly click on it to verify your email address.(Email may be present in the spams folder)." %(send_to)
		return Response({'message':message})

	else:
		return Response({'message':get_errors(user_serializer._errors)}, status=status.HTTP_400_BAD_REQUEST)

############ Get Errors #############
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_vars(message='')
def get_errors(d):
	for k,v in d.iteritems():
		if isinstance(v, dict):
			get_errors.message += get_errors(v)
		else:
			return v[0]
	return get_errors.message

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def show_sports(request):

	g_leader = GroupLeader.objects.get(user=request.user)
	sports = Event.objects.all()
	sports_added = [participation.event for participation in Participation.objects.filter(g_l=g_leader)]
	sports_left = [sport for sport in sports if sport not in sports_added]
	added_serializer = EventSerializer(sports_added, many=True)
	left_serializer = EventSerializer(sports_left, many=True)

	return Response({'sports_added':added_serializer.data, 'sports_left':left_serializer.data,})

@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def manage_sports(request):

	data = request.data
	print data
	g_l = GroupLeader.objects.get(user=request.user)
	try:
		events_added = data['sportsadded']
		for e_id in eval(events_added):
			print e_id
			event = get_object_or_404(Event, id=int(e_id))
			part, created = Participation.objects.get_or_create(g_l=g_l, event=event)
	except KeyError:
		pass
		
	try:
		events_left = data['sportsleft']

		for e_id in eval(events_left):
			event = get_object_or_404(Event, id=int(e_id))
			try:
				Participation.objects.get(g_l=g_l, event=event).delete()
				TeamCaptain.objects.filter(event=event, g_l=g_l).delete()
			except:
				continue
	except KeyError:
		pass
	
	g_leader = GroupLeader.objects.get(user=request.user)
	sports = Event.objects.all()
	sports_added = [participation.event for participation in Participation.objects.filter(g_l=g_leader)]
	sports_left = [sport for sport in sports if sport not in sports_added]
	added_serializer = EventSerializer(sports_added, many=True)
	left_serializer = EventSerializer(sports_left, many=True)

	return Response({'sports_added':added_serializer.data, 'sports_left':left_serializer.data,})

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def get_id(request):
	gl = GroupLeader.objects.get(user=request.user)
	g_l_serializer = GroupLeaderSerializer(gl)
	return Response(g_l_serializer.data)

@api_view(['GET', ])
def test_sport(request, e_id):
	data = request.data
	g_l = GroupLeader.objects.get(user=request.user)
	try:
		event = Event.objects.get(id=e_id)
	except:
		return Response({'message':'Event does not exist'})
	if event.min_limit == 1 and event.max_limit == 1:
		return Response({'message':'Success'})
	try:
		Participation.objects.get(g_l=g_l, event = event)
		try:
			tc = TeamCaptain.objects.get(g_l=g_l, event=event)
			participants = ParticipantSerializer(tc.participant_set.all(), many=True)
			return Response({'participants':participants.data, 'message':'Details already added'})
		except:
			return Response({'message':'Success'})
	
	except:
		return Response({'message':'Add sport first'})

@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def register_captain(request):

	data = request.data
	print data
	e_id = int(data['event'])
	g_id = int(data['g_l'])
	try:
		event = Event.objects.get(id=e_id)
	except:
		return Response({'error':'Error in event.'})
	user = request.user
	g_l = GroupLeader.objects.get(user=user)
	print g_l
	if g_id == g_l.id:
		try:
			participation = Participation.objects.get(event=event, g_l=g_l)
			tc = TeamCaptain.objects.get(g_l=g_l, event=event)
			# captain.delete()
			participants = ParticipantSerializer(tc.participant_set.all(), many=True)

			return Response({'participants':participants.data, 'message':'Sports already added'})
		except:
			pass
		captain_serializer = TeamCaptainSerializer(data=data)
		if captain_serializer.is_valid():
			captain = captain_serializer.save()
			
			Participant.objects.create(name=data['name'], captain=captain)
			try:
				participants = [participant for participant in eval(data['participants'])]
			except:
				participants = []

			if participants:
				participants_added = []
				captain.is_single = False
				captain.save()
				print len(participants)
				if (event.max_limit>len(participants)>=event.min_limit-1):
					for participant in participants:
						participants_added.append(Participant.objects.create(name=participant, captain=captain))
					captain.total_players = len(participants) + 1
					captain.save()
					g_l_serializer = GroupLeaderSerializer(g_l)
					captain_serializer = TeamCaptainSerializer(captain)
					participant_data = ParticipantSerializer(participants_added, many=True)

					return Response({'g_leader':g_l_serializer.data, 'captain':captain_serializer.data, 'participants':participant_data.data})

				else:
					captain.delete()
					return Response({'message':'Invalid number of players'})

			else:
				captain.is_single = True
				if event.min_limit == event.max_limit == 1:
					captain.save()
					g_l_serializer = GroupLeaderSerializer(g_l)
					captain_serializer = TeamCaptainSerializer(captain)
					return Response({'g_leader':g_l_serializer.data, 'captain':captain_serializer.data,})

				else:
					captain.delete()
					return Response({'message':'Invalid number of players'})

		else:
			return Response({'message':get_errors(captain_serializer.errors)})
	else:
		return Response({'message':'Access Denied'})

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def add_events(request, tc_id):

	user = request.user
	g_leader = GroupLeader.objects.get(user=user)
	captain = TeamCaptain.objects.get(id=tc_id)
	participants = Participant.objects.filter(captain=captain)
	event_set =  [event for event in Event.objects.filter(min_limit=1, max_limit=1) if Participation.objects.filter(event=event, g_l=g_leader)]
	events_data = EventSerializer(event_set, many=True)
	participants_data = ParticipantSerializer(participants, many=True)
	return Response({'participants':participants_data.data, 'events':events_data.data})

@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def add_extra_event(request, tc_id):

	data = request.data
	user = request.user
	groupleader = GroupLeader.objects.get(user=user)
	captain = TeamCaptain.objects.get(id=tc_id)
	participants = Participant.objects.filter(captain=captain)
	participant_data = []
	for e_id in eval(data['part_data']):
		if e_id[0]!='0':
			print e_id[0]
			for i in e_id[1:]:
				participant = Participant.objects.get(id=int(i))
				event = Event.objects.get(id=int(e_id[0]))
				participation = get_object_or_404(Participation, g_l=groupleader, event=event)
				tc = TeamCaptain(name=participant.name, g_l=groupleader,event=event, if_payment=False, gender=captain.gender)
				tc.save()
				participant_data.append(Participant.objects.create(name=tc.name, captain=tc))
	g_l_serializer = GroupLeaderSerializer(groupleader)
	captain_serializer = TeamCaptainSerializer(captain)
	participant_data = ParticipantSerializer(participant_data, many=True)

	return Response({'g_leader':g_l_serializer.data, 'captain':captain_serializer.data, 'participants_changed':participant_data.data})

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_logout(request):
	logout(request)

	return Response({'message':'Successfully logged out.'})