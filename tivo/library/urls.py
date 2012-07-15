from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # View index of library items:
    url(r'^$', 'library.views.index', name='index'),
)
