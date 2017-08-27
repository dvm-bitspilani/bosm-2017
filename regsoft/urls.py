from django.conf.urls import url
from . import views

app_name = 'regsoft'

urlpatterns = [
	url(r'^$', views.index, name='index'),


	########## Firewallz #############
	url(r'^firewallz/$', views.firewallzO_home, name='firewallz-home'),

	########## RecNAcc #############
	url(r'^recnacc/$', views.recnacc_home, name='recnacc-home'),
	url(r'^recnacc/allot_room/(?P<gl_id>\d+)/$', views.allot_room, name='allot_room'),
	url(r'recnacc/main_list',views.main_list, name="main_list"),
	
	########## Controlz #############
	url(r'^controlz/$', views.controlz_home, name='controlz-home'),

	########## FirewallzI #############
	url(r'^firewallzi/$', views.firewallzi_home, name='firewallzi-home')
]