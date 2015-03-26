from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404
from django.conf import settings
from deal.models import City, Category, Deal, Local, Site, Company
from tagging.models import Tag

class BaseFeed(Feed):
    title = ""
    link = "/"
    description = "feeds"
    #title_template = "feeds/latest_entries_title.html"

    def get_object(self, request, city_abbreviation):
        self.request = request
        self.city_abbreviation = city_abbreviation
        return get_object_or_404(City, abbreviation=city_abbreviation)
        
    def items(self, obj):
        return Deal.objects.get_current_deals(obj.id)[:settings.DEFAULT_FEEDS]

    def description(self, obj):
        return obj.name
    
    def item_description(self, item):
        return item.detail
    
    def item_link(self, item):
        return "http://%s%s" % (self.request.META.get('HTTP_HOST'), reverse("www_deal", args=[self.city_abbreviation, item.id]))

class LatestDeals(BaseFeed):
    pass

class CategoryDeals(BaseFeed):
    def get_object(self, request, city_abbreviation, category_id):
        self.request = request
        self.city_abbreviation = city_abbreviation
        try:
            self.category = Category.objects.get(pk=category_id)
        except:
            raise Http404()
        return get_object_or_404(City, abbreviation=city_abbreviation)
        
    def description(self, obj):
        return obj.name + '_' + self.category.name
    
    def items(self, obj):
        return Deal.objects.get_deals_by_category(city_id=obj.id, category=self.category)[:settings.DEFAULT_FEEDS]

class TagDeals(BaseFeed):
    def get_object(self, request, city_abbreviation, tag_id):
        self.request = request
        self.city_abbreviation = city_abbreviation
        try:
            self.tag = Tag.objects.get(pk=tag_id)
        except:
            raise Http404
        return get_object_or_404(City, abbreviation=city_abbreviation)
        
    def description(self, obj):
        return obj.name + '_' + self.tag.name
    
    def items(self, obj):
        return Deal.objects.get_deals_by_tag(city_id=obj.id, tag=self.tag)[:settings.DEFAULT_FEEDS]

class LocalDeals(BaseFeed):
    def get_object(self, request, city_abbreviation, local_id):
        self.request = request
        self.city_abbreviation = city_abbreviation
        try:
            self.local = Local.objects.get(pk=local_id)
        except:
            raise Http404
        return get_object_or_404(City, abbreviation=city_abbreviation)
    
    def description(self, obj):
        return obj.name + '_' + self.local.name
    
    def items(self, obj):
        return Deal.objects.get_deals_by_local(city_id=obj.id, local=self.local)[:settings.DEFAULT_FEEDS]

class SiteDeals(BaseFeed):
    def get_object(self, request, city_abbreviation, site_id):
        self.request = request
        self.city_abbreviation = city_abbreviation
        try:
            self.site = Site.objects.get(pk=site_id)
        except:
            raise Http404
        return get_object_or_404(City, abbreviation=city_abbreviation)
        
    def description(self, obj):
        return obj.name + '_' + self.site.name
    
    def items(self, obj):
        return Deal.objects.get_deals_by_site(city_id=obj.id, site=self.site)[:settings.DEFAULT_FEEDS]

class CompanyDeals(BaseFeed):
    def get_object(self, request, city_abbreviation, company_id):
        self.request = request
        self.city_abbreviation = city_abbreviation
        try:
            self.company = Company.objects.get(pk=company_id)
        except:
            raise Http404
        return get_object_or_404(City, abbreviation=city_abbreviation)
        
    def description(self, obj):
        return obj.name + '_' + self.company.name
    
    def items(self, obj):
        return Deal.objects.get_deals_by_company(city_id=obj.id, copmpany=self.company)[:settings.DEFAULT_FEEDS]