from django.conf.urls import patterns, include, url

urlpatterns = patterns('chat.views',
    url(r'^$', 'start_chat', name='chat'),
    url(r'still_here', 'still_here_short_poll', name="still_here"),
)