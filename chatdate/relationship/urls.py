from django.conf.urls import patterns, include, url

urlpatterns = patterns('relationship.views',
    url(r'^.json$', 'relationships', name='relationships'),
    url(r'block$', "block_user", name="block"),
)