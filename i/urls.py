from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('i.views',
    url(r'^$', 'index', name='i_index'),
    url(r'^(?P<user_id>\d+).html$', 'user', name='i_user'),
    url(r'^bind/$', 'bind', name='i_bind'),
    url(r'^(?P<user_id>\d+)/link/$', 'link', name='i_link'),
    url(r'^(?P<user_id>\d+)/p/$', 'promotion', {'city_abbreviation': None}, name='i_promotion'),
    url(r'^(?P<user_id>\d+)/p/(?P<city_abbreviation>\w+)/$', 'promotion', name='i_promotion'),
    url(r'^(?P<user_id>\d+)/transfer/$', 'transfer', name='i_transfer'),
    url(r'^mydeal/$', 'mydeal', name='i_mydeal'),
    url(r'^mydeal_add/$', 'mydeal_add', name='i_mydeal_add'),
    url(r'^mydeal_del/(?P<id>\d+)$', 'mydeal_del', name='i_mydeal_del'),
    url(r'^mydeal_edit/(?P<id>\d+)$', 'mydeal_edit', name='i_mydeal_edit'),
    url(r'^mydeal_change_status/(?P<id>\d+)$', 'mydeal_change_status', name='i_mydeal_change_status'),
    url(r'deal_review_info_(?P<deal_id>\d+).html$', 'deal_review_info', name='i_deal_review_info'),
)