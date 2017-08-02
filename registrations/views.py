from django.shortcuts import render

# Create your views here.
@login_required
def register_captain(request):
	
	if request.method == 'POST':
		data = request.POST
		user = request.user
		event_id = data['event_id']
		tc_form = TeamCapTainForm(data)
		if tc_form.is_valid:
			event = Event.objects.get(id=event_id)
			teamCaptain = tc_form.save(commit=False)
			teamCaptain.event.add(event)
			g_l = GroupLeader.objects,get(user=user)
			teamCaptain.g_l = g_l
			partcipants = data['partcipants']
			if partcipants:
				teamCaptain.is_single = False
				for part in partcipants:
					Partcipants.objects.create(captain=teamCaptain, name = part)
				return render
			else:
				teamCaptain.is_single = True
		else:
			return render()
		
	else:
		form = TeamCapTainForm()

		return render()