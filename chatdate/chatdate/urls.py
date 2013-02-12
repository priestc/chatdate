from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('landing.urls')),
    url(r"", include('django_socketio.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^chat/', include('chat.urls')),
    url(r'^admin/', include(admin.site.urls)),
)