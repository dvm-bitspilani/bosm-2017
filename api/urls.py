from django.conf.urls import url
from api import views

app_name = 'api'

urlpatterns = [
   	url(r'^$', views.index, name='index'),
    url(r'^register$', views.create_user, name='register'),
    url(r'^login$', views.user_login, name='login'),
    url(r'^logout$', views.user_logout, name='logout'),
]