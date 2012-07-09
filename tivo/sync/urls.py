from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # Examples:
    url(r'^job$', 'sync.views.job', name='job'),
)
