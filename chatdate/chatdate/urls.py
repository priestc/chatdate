from django.conf.urls import patterns, include, url
from socketio import sdjango
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('landing.urls')),
    url(r'^relationships\.json$', 'relationship.views.relationships', name='relationships'),
    url(r'^chat/', include('chat.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url("^socket\.io", include(sdjango.urls)),
)