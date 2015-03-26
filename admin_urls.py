from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

from deal.feeds import LatestDeals, CategoryDeals, TagDeals, LocalDeals, SiteDeals, CompanyDeals

urlpatterns = patterns('',
    url(r'^deal/add_category/$', 'deal.admin_views.add_category', name='admin_add_category'),
    url(r'^deal/add_tag/$', 'deal.admin_views.add_tag', name='admin_add_tag'),                       
    (r'^', include(admin.site.urls)),
)
