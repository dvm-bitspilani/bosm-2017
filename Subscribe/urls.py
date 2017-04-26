from django.conf.urls import url
from Subscribe import views

app_name = 'Subscribe'

urlpatterns = [
    #url(r'^subscribe$', views.subscribe, name='subscribe'),
    url(r'^$', views.index, name='index'),
    url(r'^download$', views.get_list, name='prc list'),
]
