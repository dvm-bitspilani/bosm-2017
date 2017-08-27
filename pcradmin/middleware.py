from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from pcradmin import views

class PCrAdminMiddleware(object):

	def __init__(self, get_response):
		self.get_response = get_response
	
	def __call__(self, request):
		return self.get_response(request)

	def process_view(self, request,  view_func, view_args, view_kwargs):
		
		if 'admin' in request.path:
			return None
		
		if request.user.is_superuser:
			return None
		
		if view_func == views.index:
			return None

		if request.user.is_authenticated():

			if 'logout' not in request.path:

				if not request.user.username == 'pcradmin' and 'pcradmin' in request.path:

					return render(request, 'pcradmin/message.html',{'message':'Access Denied'})

				else:

					return None