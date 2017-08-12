from django.conf.urls import url
from pcradmin import views

app_name = 'pcradmin'

handler404 = 'views.custom_page_not_found'
handler403 = 'views.custom_permission_denied'
handler400 = 'views.custom_bad_request'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^sportlimit/$',views.sport_limit, name='sport_limit'),
    url(r'^sportlimit/(?P<event_id>\d+)/$', views.sport_limit_change, name="sport_limit_change"),
    url(r'^email_select/$', views.email_select, name="email_select"),
    url(r'^email_compose/(?P<gl_id>\d+)/$', views.email_compose, name="email_compose"),
    url(r'^status_change/$', views.status_change, name="status_change"),
    url(r'^confirm_events/(?P<gl_id>\d+)/$',views.confirm_events, name = "confirm_events"),
    url(r'^list_team_gleaders/$', views.list_gl, name="list_gl"),
    url(r'^list_team_captains/(?P<gl_id>\d+)/$', views.list_tc, name="list_tc"),
    url(r'^search_team_captain/$', views.search_tc, name="search_tc"),
    url(r'^stats/college/$', views.stats, name="stats_collegewise", kwargs={'order':'Collegewise'}),
    url(r'^stats/sport/$', views.stats, name="stats_sportwise", kwargs={'order':'Sportwise'}),
    url(r'^stats/sport_college/$', views.stats, name="stat_sport_college", kwargs={'order':'both'}),
    url(r'^stats/sport_college/(?P<gl_id>\d+)/$', views.stats),
    url(r'^get_list/$', views.get_list, name="get_list"),
    url(r'^get_captain_list/(?P<gl_id>\d+)/$', views.get_list_captains, name="get_list_captains"),
    url(r'^get_gleaders_list/$', views.get_list_gleaders, name="get_list_gleaders"),
    url(r'^logout/$', views.user_logout, name = 'logout'),
    #url(r'^logout/$', views.user_logout, name="logout"),
    # url(r'')
]
