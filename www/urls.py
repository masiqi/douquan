from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap
from deal.feeds import LatestDeals, CategoryDeals, TagDeals, LocalDeals, SiteDeals, CompanyDeals
from deal.models import Deal, City

info_dict = {
    'queryset':Deal.objects.filter(publish_status=1),
    'date_field':'updated_at',
}

sitemaps = {
    'flatpages':FlatPageSitemap,
    #'deal':GenericSitemap(info_dict, priority=0.8),
}

for city in City.objects.all():
    sitemaps[city.abbreviation] = GenericSitemap({'queryset':Deal.objects.get_deals_by_city(city.id), 'date_field':'updated_at',}, priority=0.8)

urlpatterns = patterns('www.views',
    url(r'^test$', 'test', name='my_test'),
    url(r'^$', 'index', {'city_abbreviation': None, 'status': 1}, name='www_index'),
    url(r'^(?P<city_abbreviation>\w+)/$', 'index', {'status': 1}, name='www_city_index'),
    url(r'^(?P<city_abbreviation>\w+)/list/$', 'index', {'status': 3}, name='www_city_list'),
    url(r'^(?P<city_abbreviation>\w+)/s_(?P<keyword>.*).html$', 'search', name='www_search'),
    url(r'^(?P<city_abbreviation>\w+)/search.html$', 'search_post', name='www_search_post'),
    url(r'^(?P<city_abbreviation>\w+)/d_(?P<deal_id>\d+).html$', 'deal', name='www_deal'),
    url(r'^(?P<city_abbreviation>\w+)/transfer.html$', 'transfer_index', name='www_transfer_index'),
    url(r'^(?P<city_abbreviation>\w+)/transfer_(?P<transfer_id>\d+).html$', 'transfer', name='www_transfer'),
    url(r'^(?P<city_abbreviation>\w+)/vote_(?P<deal_id>\d+).html$', 'deal_vote', name='www_vote'),
    url(r'^(?P<city_abbreviation>\w+)/deal_transfer_add.html$', 'deal_transfer_add', name='www_deal_transfer_add'),
    url(r'^(?P<city_abbreviation>\w+)/deal_transfer_(?P<deal_id>\d+).html$', 'deal_transfer', name='www_deal_transfer'),
    url(r'^(?P<city_abbreviation>\w+)/deal_comment_(?P<deal_id>\d+).html$', 'deal_comment', name='www_deal_comment'),
    url(r'^(?P<city_abbreviation>\w+)/catgory_(?P<category_name>.*).html$', 'category', name='www_category'),
    url(r'^(?P<city_abbreviation>\w+)/date_(?P<date>.*).html$', 'date', name='www_date'),
    url(r'^(?P<city_abbreviation>\w+)/tag_(?P<tag_name>.*).html$', 'tag', name='www_tag'),
    url(r'^city/(?P<city_name>.*).html$', 'city', name='www_city'),
    url(r'^set_city/(?P<city_abbreviation>\d+)/$', 'set_city', name='www_set_city'),
    url(r'^(?P<city_abbreviation>\w+)/write_comment/$', 'write_comment', name='www_write_comment'),
    url(r'^write_review$', 'write_review', name='www_write_review'),
    url(r'^(?P<city_abbreviation>\w+)/local_(?P<local_name>.*).html$', 'local', name='www_local'),
    url(r'^(?P<city_abbreviation>\w+)/site_(?P<site_name>\S+)/$', 'site', name='www_site'),
    url(r'^(?P<city_abbreviation>\w+)/company_(?P<company_id>\S+)/$', 'company', name='www_company'),
    url(r'external_url/(?P<url>.*)$', 'external_url', name='external_url'),
    url(r'join.html$', 'site_join', name='www_site_join'),
    url(r'contact.html$', 'contact_us', name='www_contact_us'),
    url(r'deal_review_info_(?P<deal_id>\d+).html$', 'deal_review_info', name='www_deal_review_info'),
)

urlpatterns += patterns('',
    url(r'^(?P<city_abbreviation>\w+)/feeds/deals/$', LatestDeals(), name='feed_deals'),
    url(r'^(?P<city_abbreviation>\w+)/feeds/category_(?P<category_id>\d+)/$', CategoryDeals(), name='feed_category'),
    url(r'^(?P<city_abbreviation>\w+)/feeds/tag_(?P<tag_id>\d+)/$', TagDeals(), name='feed_tag'),
    url(r'^(?P<city_abbreviation>\w+)/feeds/local_(?P<local_id>\d+)/$', LocalDeals(), name='feed_local'),
    (r'^(?P<city_abbreviation>\w+)/feeds/site_(?P<site_id>\d+)/$', SiteDeals()),
    (r'^(?P<city_abbreviation>\w+)/feeds/company_(?P<company_id>\d+)/$', CompanyDeals()),
    (r"^media/(?P<path>.*)$", "dynamic_media_serve.serve", {"document_root": settings.MEDIA_ROOT, "compress": True}),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

urlpatterns += patterns('',
    (r'^grappelli/', include('grappelli.urls')),
)
