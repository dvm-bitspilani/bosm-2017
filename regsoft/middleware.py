from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from registrations import views

class RegsoftMiddleware(object):

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		return self.get_response(request)

	def process_view(self, request, view_func, view_args, view_kwargs):

		if 'admin' in request.path:
			return None

		if request.user.is_superuser:
			return None

		if 'regsoft' not in request.path:
			return None

		if view_func == views.index or 'getbarcode' in request.path:
			return None

		message='You don\'t have access to this page.'

		if 'logout' not in request.path:

			if request.user.username not in request.path:
				return render(request, 'registrations/message.html', {'message':message})

			if request.user.username == 'firewallz' and 'firewallzi' in request.path:
				return render(request, 'registrations/message.html', {'message':message})

