from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('renren.views',
    url(r'^test/$', 'test', name='my_test'),
    url(r'^preinstall/$', 'preinstall', name='renren_preinstall'),
    url(r'^$', 'index', {'city_abbreviation': None, 'status': 1}, name='renren_index'),
    url(r'^(?P<city_abbreviation>\w+)/$', 'index', {'status': 1}, name='renren_city_index'),
)
