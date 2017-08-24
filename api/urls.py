from django.conf.urls import url
from api import views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

app_name = 'api'

urlpatterns = [
   	url(r'^$', views.index, name='index'),
    url(r'^register$', views.create_user, name='register'),
    url(r'^login$', views.user_login, name='login'),
    url(r'^show_sports$', views.show_sports, name='show_sports'),
    url(r'^manage_sports$', views.manage_sports, name='manage_sports'),
    url(r'^register_captain$', views.register_captain, name='register_captain'),
    url(r'^add_events/(?P<tc_id>\d+)$', views.add_events, name='add_events'),
    url(r'^add_extra_event/(?P<tc_id>\d+)$', views.add_extra_event, name='add_extra_event'),
    url(r'^api_token', obtain_jwt_token),
    url(r'^api_token_refresh', refresh_jwt_token),
    url(r'^api_test', views.api_test),
    url(r'^logout$', views.user_logout, name='logout'),
]