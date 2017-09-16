from django.conf.urls import url
from . import views

app_name = 'regsoft'

urlpatterns = [
	
	url(r'^$', views.index, name='index'),
	# url(r'^test/$', views.home, name='home'),	
	url(r'^get_barcode/$', views.get_barcode, name='get_barcode'),
	########## Firewallz #############

	url(r'^firewallz/$', views.firewallzo_home, name='firewallz-home'),
	url(r'^firewallz/swap/$', views.firewallz_swap, name='firewallz_swap'),
	url(r'^firewallz/edit/(?P<part_id>\d+)/$', views.firewallz_edit, name='firewallz_edit'),
	url(r'^firewallz/add/(?P<gl_id>\d+)/$', views.firewallz_add, name='firewallz_add'),
	url(r'^firewallz/delete/$', views.firewallz_delete, name='firewallz_delete'),
	url(r'^firewallz/edit_tc/(?P<tc_id>\d+)/$', views.firewallz_edit_tc, name='firewallz_edit_tc'),

	########## RecNAcc #############
	url(r'^recnacc/$', views.recnacc_home, name='recnacc-home'),
	url(r'^recnacc/college/(?P<gl_id>\d+)/$', views.recnacc_college, name='recnacc-college'),
	url(r'^recnacc/change/$',views.recnacc_change, name='change'),
	url(r'^recnacc/college_vs_bhavan/$', views.college_vs_bhavan, name='college_vs_bhavan'),
	url(r'^recnacc/all_bhavans/$', views.all_bhavans, name='all_bhavans'),
	url(r'^recnacc/bhavan_details/(?P<b_id>\d+)/$', views.bhavan_details, name='bhavan_details'),
	url(r'^recnacc/firewallz_approved/$', views.firewallz_approved, name='firewallz_approved'),
	url(r'^recnacc/checkout/$', views.recnacc_checkout, name="recnacc_checkout"),
	url(r'^recnacc/checkout/(?P<gl_id>\d+)/$', views.recnacc_checkout_id, name="recnacc_checkout_id"),
	
	########## Controlz #############
	url(r'^controlz/$', views.controlz_home, name='controlz-home'),
	# url(r'^controlz/team_list/(?P<tc_id>\d+)/$', views.show_team_list, name='show_team_list'),
	# url(r'^controlz/view_captain/(?P<tc_id>\d+)/$', views.view_captain, name='view_captain'),
	url(r'^controlz/get_captains/$', views.get_captains, name='get_captains'),
	url(r'^controlz/create_bill/(?P<gl_id>\d+)/$', views.create_bill, name='create_bill'),
	url(r'^controlz/recnacc_list/(?P<gl_id>\d+)/$', views.recnacc_list, name='recnacc_list'),
	url(r'^controlz/generate_recnacc_list/$', views.generate_recnacc_list, name='generate_recnacc_list'),
	url(r'^controlz/view_bills/(?P<gl_id>\d+)/$', views.view_bills, name='view_bills'),
	url(r'^controlz/bill_details/(?P<b_id>\d+)/$', views.bill_details, name='bill_details'),
	url(r'^controlz/delete_bill/(?P<b_id>\d+)/$', views.delete_bill, name='delete_bill'),
	url(r'^controlz/print_bill/(?P<b_id>\d+)/$', views.print_bill, name='print_bill'),
	# url(r'^controlz/view_captain_controlz/(?P<gl_id>\d+)/$', views.view_captain_controlz, name='view_captain_controlz'),
	url(r'^controlz/edit/(?P<part_id>\d+)/$', views.controlz_edit, name='controlz_edit'),
	url(r'^controlz/add/(?P<gl_id>\d+)/$', views.controlz_add, name='controlz_add'),
	url(r'^controlz/delete/$', views.controlz_delete, name='controlz_delete'),
	url(r'^controlz/event_details/$', views.get_details, name='get_details'),
	url(r'^controlz/edit_tc/(?P<tc_id>\d+)/$', views.controlz_edit_tc, name='controlz_edit_tc'),

	########## FirewallzI #############
	#url(r'^firewallzi/$', views.firewallzi_home, name='firewallzi-home')
	url(r'^contacts/$', views.contacts, name='contacts'),
	url(r'^logout/$', views.user_logout, name='user-logout'),

]