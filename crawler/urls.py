from django.conf.urls.defaults import *

urlpatterns = patterns('crawler.views',
    url(r'^$', 'index', name='crawler_index'),
    url(r'^show/(?P<storage_id>\d+)$', 'read_storage', name='crawler_read_storage'),
)