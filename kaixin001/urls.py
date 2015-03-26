from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('kaixin001.views',
    url(r'^test$', 'test', name='my_test'),
    url(r'^$', 'index', {'city_abbreviation': None, 'status': 1}, name='kaixin001_index'),
    url(r'^(?P<city_abbreviation>\w+)/$', 'index', {'status': 1}, name='kaixin001_city_index'),
    url(r'^(?P<city_abbreviation>\w+)/list/$', 'index', {'status': 3}, name='kaixin001_city_list'),
    url(r'^search.html$', 'search_post', name='kaixin001_search_post'),
    url(r'^s_(?P<keyword>.*).html$', 'search', name='kaixin001_search'),
    url(r'^d_(?P<deal_id>\d+).html$', 'deal', name='kaixin001_deal'),
    url(r'^site_(?P<site_name>\S+).html$', 'site', name='kaixin001_site'),
    url(r'^catgory_(?P<category_name>.*).html$', 'category', name='kaixin001_category'),
)
