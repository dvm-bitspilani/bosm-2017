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
    
    url(r'^stats/$', views.stats, name="stats_page"),
    url(r'^stats/(?P<order>\w+)/$', views.stats_order, name="stats"),
    url(r'^stats/college/(?P<gl_id>\d+)/$', views.stats_college, name="collegewise"),
    url(r'^stats/sport/(?P<e_id>\d+)/$', views.stats_sport, name="sportwise"),
    url(r'show_participants/(?P<gl_id>\d+)/(?P<event_id>\d+)/$', views.show_participants, name='show_participants'),
    # url(r'^stats/total_players_registered/$', views.total_players_registered, name="total_players_registered"),

    url(r'^get_list/$', views.get_list, name="get_list"),
    url(r'^get_captain_list/(?P<gl_id>\d+)/$', views.get_list_captains, name="get_list_captains"),
    url(r'^get_gleaders_list/$', views.get_list_gleaders, name="get_list_gleaders"),
    url(r'^final_list_download/$', views.final_list_download, name="final_list_download"),
    url(r'^final_confirmation/$', views.final_confirmation, name="final_confirmation"),
    url(r'^final_confirmation_email/(?P<gl_id>\d+)/$', views.final_confirmation_email, name="final_confirmation_email"),
    url(r'^logout/$', views.user_logout, name = 'logout'),
    url(r'^change_paid/$', views.change_paid, name='change_paid'),
    url(r'^change_paid_college/(?P<gl_id>\d+)/$', views.change_paid_college, name='change_paid_college'),
    url(r'^edit/$', views.edit, name='edit-show_gl'),
    url(r'^edit/(?P<gl_id>\d+)/$', views.edit, name='edit-show_participants'),
    url(r'^edit_participant/(?P<part_id>)/$', views.edit_participant, name='edit_participant'),

]
