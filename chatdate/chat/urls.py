from django.conf.urls import patterns, include, url

urlpatterns = patterns('chat.views',
    url(r'karma', 'karma', name="karma"),
)