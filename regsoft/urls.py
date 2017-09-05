from django.conf.urls import url
from . import views

app_name = 'regsoft'

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^test$', views.home, name='home'),	

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
	url(r'^recnacc/firewallz_approved/$', views.firewallz_approved, name='firewallz_approved'),
	
	########## Controlz #############
	url(r'^controlz/$', views.controlz_home, name='controlz-home'),

	########## FirewallzI #############
	#url(r'^firewallzi/$', views.firewallzi_home, name='firewallzi-home')
	url(r'^logout/$', views.user_logout, name='user-logout'),

]