from django.conf.urls import url
from pcradmin import views

app_name = 'pcradmin'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^sportlimit/$',views.sport_limit, name='sport_limit'),
    url(r'^sportlimit/(?P<event_id>\d+)/$', views.sport_limit_change, name="sport_limit_change"),
    url(r'^email_select/$', views.email_select, name="email_select"),
    url(r'^email_compose/(?P<gl_id>\d+)/$', views.email_compose, name="email_compose"),
    url(r'^status_change/$', views.status_change, name="status_change"),
    url(r'^confirm_events/(?P<gl_id>\d+)/$',views.confirm_events, name = "confirm_events"),
    url(r'^list_team_captains/$', views.list_tc, name="list_tc"),
    url(r'^search_team_captain/$', views.search_tc, name="search_tc"),
]
