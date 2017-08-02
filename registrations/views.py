from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required

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
				user.save()
				g_l_profile = pform.save(commit=False)
				g_l_profile.user = user
				g_l_profile.save()
				new_user = authenticate(username=request.data['username'],
                                    password=request.data['password'],)
				login(request, new_user)

				return HttpResponseRedirect('/')

			else:

				print uform.errors, pform.errors

		else:

			uform = UserForm()
			pform = GroupLeaderForm()

			return render...

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

		for id in id_list:

			event = Event.objects.get(pk=id)
			Participation.objects.get(g_l=g_leader, event=event).delete()

		#participation_list = Participation.objects.filter(g_l=g_leader)
		#return JsonResponse({'status':0,'participations':participation_list})

		return HttpResponseRedirect('/')