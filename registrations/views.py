from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives

from .models import *
from events.models import *
from .forms import *

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



				return HttpResponseRedirect('/')

			else:

				print uform.errors, pform.errors

		else:

			uform = UserForm()
			pform = GroupLeaderForm()

			return render(request, 'registrations/index.html', {'uform':uform, 'pform':pform}) 

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

