from django.conf.urls import urls
from . import views

app_name = 'registrations'

urlpatterns = [
	url(r'^$', views.index, name="Index"),
	
]