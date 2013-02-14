from django.conf.urls import patterns, include, url

urlpatterns = patterns('landing.views',
    url(r'^$', 'landingpage', name='landingpage'),
    url(r'^one$', 'register_start', name='register_start'),
    url(r'^logout/$', 'logout', name='logout'),
)