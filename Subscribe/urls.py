from django.conf.urls import url
from Subscribe import views
from django.views.generic import RedirectView

app_name = 'Subscribe'

urlpatterns = [
    #url(r'^subscribe$', views.subscribe, name='subscribe'),
    url(r'', RedirectView.as_view(url = '^$'))
    url(r'^$', views.index, name='index'),
    url(r'^2017/download$', views.get_list, name='pcr list'),
]
