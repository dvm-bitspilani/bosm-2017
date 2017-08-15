from django.conf.urls import url
from . import views

app_name = 'registrations'

urlpatterns = [
	url(r'^$', views.index, name="index"),
	url(r'^email_test$', views.email_test,),
	url(r'^login/$', views.user_login, name="login"),
	url(r'^logout/$', views.user_logout, name="logout"),
	url(r'^signup/$', views.signup_view, name="signup"),
	url(r'^show_sports/$', views.show_sports, name="show"),
	url(r'^manage_sports/$', views.manage_sports, name="manage"),
	url(r'^email_confirm/(?P<token>\w+)/$', views.email_confirm, name="email_confirm"),
	url(r'^register_captain/(?P<event_id>\d+)/$', views.register_captain, name="register_captain"),
	url(r'^add_extra_templ/(?P<tc_id>\d+)$',views.add_extra_event_templ, name="add_extra_templ"),
	url(r'^add_extra/(?P<tc_id>\d+)/$',views.add_extra_event, name="add_extra_event"),
	url(r'^transport/$', views.transport, name="transport"),
	url(r'^api/paytm/$', views.paytm_req, name="paytm"),
	url(r'^api/paytm/(?P<token>\w+)/$', views.paytm_request, name="paytm-request"),
	url(r'^response/$', views.paytm_response, name="paytm-response"),
]