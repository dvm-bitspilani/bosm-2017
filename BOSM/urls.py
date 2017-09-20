from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from app.views import index
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^intro/', include('Subscribe.urls')),
    url(r'^pcradmin/', include('pcradmin.urls')),
    url(r'^registrations/', include('registrations.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^regsoft/', include('regsoft.urls')),
    url(r'^app',index),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)