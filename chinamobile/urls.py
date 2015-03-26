from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('chinamobile.views',
    url(r'^test$', 'test', name='chinamobile_test'),
    url(r'^$', 'index', {'city_abbreviation': None, 'status': 1}, name='chinamobile_index'),
     url(r'^(?P<city_abbreviation>\w+)/$', 'index', {'status': 1}, name='chinamobile_city_index'),
)
