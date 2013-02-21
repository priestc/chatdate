from django.conf.urls import patterns, include, url
from socketio import sdjango
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'chatdate.views.landingpage'),
    url(r'^relationships\.json$', 'relationship.views.relationships', name='relationships'),
    url(r'^chat/', include('chat.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r"^socket\.io", include(sdjango.urls)),
    url(r'^register$', 'chatdate.views.register_start', name='register_start'),
    url(r'^logout/$', 'chatdate.views.logout', name='logout'),
    url(r"^update_profile$", "chatdate.views.update_profile", name="update_profile"),
)