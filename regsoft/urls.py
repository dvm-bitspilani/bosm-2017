from django.conf.urls import url
from . import views

app_name = 'regsoft'

urlpatterns = [
	
	url(r'^$', views.index, name='index'),
	url(r'^test/$', views.home, name='home'),	
	url(r'^get_barcode/$', views.get_barcode, name='get_barcode'),
	########## Firewallz #############

	url(r'^firewallz/$', views.firewallzo_home, name='firewallz-home'),
	url(r'^firewallz/swap/$', views.firewallz_swap, name='firewallz_swap'),

	########## RecNAcc #############
	url(r'^recnacc/$', views.recnacc_home, name='recnacc-home'),
	url(r'^recnacc/college/(?P<gl_id>\d+)/$', views.recnacc_college, name='recnacc-college'),
	url(r'^recnacc/team/(?P<tc_id>\d+)/$', views.recnacc_team, name='recnacc-team'),
	url(r'^recnacc/change/$',views.recnacc_change, name='change'),
	url(r'^recnacc/college_vs_bhavan/$', views.college_vs_bhavan, name='college_vs_bhavan'),
	url(r'^recnacc/all_bhavans/$', views.all_bhavans, name='all_bhavans'),
	url(r'^recnacc/bhavan_details/(?P<b_id>\d+)/$', views.bhavan_details, name='bhavan_details'),
	url(r'^recnacc/firewallz_approved/$', views.firewallz_approved, name='firewallz_approved'),
	
	########## Controlz #############
	url(r'^controlz/$', views.controlz_home, name='controlz-home'),
	url(r'^controlz/edit/(?P<part_id>\d+)/$', views.controlz_edit, name='controlz_edit'),
	url(r'^controlz/add/(?P<gl_id>\d+)/$', views.controlz_add, name='controlz_add'),
	url(r'^controlz/delete/$', views.controlz_delete, name='controlz_delete'),

	url(r'^controlz/create_bill/(?P<tc_id>\d+)/$', views.create_bill, name='create_bill'),
	url(r'^controlz/print_bill/(?P<tc_id>\d+)/$', views.print_bill, name='print_bill'),
	url(r'^controlz/view_captain_controlz/(?P<gl_id>\d+)/$', views.view_captain_controlz, name='view_captain_controlz'),
	url(r'^controlz/event_details/$', views.get_details, name='get_details'),

	########## FirewallzI #############
	#url(r'^firewallzi/$', views.firewallzi_home, name='firewallzi-home')
	url(r'^logout/$', views.user_logout, name='user-logout'),

]