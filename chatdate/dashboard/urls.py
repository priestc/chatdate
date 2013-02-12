from django.conf.urls import patterns, include, url

urlpatterns = patterns('dashboard.views',
    url(r'^$', 'dashboard', name='dashboard'),
)