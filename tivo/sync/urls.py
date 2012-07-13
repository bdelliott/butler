from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # Download show content info from the TiVo:
    url(r'^job$', 'sync.views.job', name='job'),

    # Process queue of items to be downloaded and re-encoded:
    url(r'^process_queue$', 'sync.views.process_queue', name='process_queue'),
)
