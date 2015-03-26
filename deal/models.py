#-*-coding:utf8;-*-
import time
from django.db import models
from django.contrib import admin
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from member.models import User
from djangosphinx.models import SphinxSearch
from tagging.fields import TagField
from tagging.models import Tag, TaggedItem

from datetime import datetime, date, timedelta

STATUS_CHOICE = (
    (1, u'available'),
    (2, u'failed'),
    (3, u'accomplish'),
)

PUBLISH_STATUS_CHOICE = (
    (1, u'create'),
    (2, u'publish'),
    (3, u'delete'),
)

TRANSFER_TYPE_CHOICE = (
    (1, u'转让'),
    (2, u'求购'),
)

TRANSFER_STATUS_CHOICE = (
    (1, u'available'),
    (2, u'invalid'),
)

EXCHANGE_CHOICE = (
    (1, u'是'),
    (2, u'否'),
)

class Category(models.Model):
    name = models.CharField('name', max_length=32, db_index=True)

    def __unicode__(self):
        return self.name

    def deal_count(self):
	count = cache.get(settings.CACHE_DEFINE['CATEGORY_COUNT'] % self.id)
	if count is None:
	    count = Deal.objects.filter(category__id=self.id).count()
	    cache.set(settings.CACHE_DEFINE['CATEGORY_COUNT'] % self.id, count, settings.CACHE_DEFINE['CATEGORY_COUNT_TIMEOUT'])
	return count
    
class AutoCategory(models.Model):
    keyword = models.CharField('keyword', max_length=255, unique=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    power = models.IntegerField('power')
    
    def __unicode__(self):
	return self.keyword
    
class Company(models.Model):
    name = models.CharField('name', max_length=255, db_index=True)
    address = models.CharField('address', max_length=255)
    phone = models.CharField('phone', max_length=32)
    url = models.URLField('url', max_length=255, blank=True, null=True)
    
    def __unicode__(self):
        return self.name
    
class CityManager(models.Manager):
    def get_city_by_abbreviation(self, city_abbreviation):
	city = cache.get(settings.CACHE_DEFINE['CITY_ABBREVIATION'] % city_abbreviation)
	if city is None:
            try:
                city = self.get(abbreviation=city_abbreviation)
            except City.DoesNotExist:
                city = None
	    cache.set(settings.CACHE_DEFINE['CITY_ABBREVIATION'] % city_abbreviation, city, settings.CACHE_DEFINE['CITY_ABBREVIATION_TIMEOUT'])
	return city

class City(models.Model):
    name = models.CharField('name', max_length=255, db_index=True)
    abbreviation = models.CharField('abbreviation', max_length=6, unique=True, db_index=True)
    
    objects = CityManager()
    
    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
    
    def __unicode__(self):
        return self.name    
        
class LocalManager(models.Manager):
    def get_local_by_city_id(self, city_id):
        return self.filter(city__id=city_id)
            
class Local(models.Model):
    city = models.ForeignKey(City, db_index=True, verbose_name='city', related_name = 'local')
    name = models.CharField('name', max_length=255, db_index=True)
    
    objects = LocalManager()
    
    class Meta:
        verbose_name = 'Local'
        verbose_name_plural = 'Locals'
        
    def __unicode__(self):
        return self.name  

class SiteManager(models.Manager):
    def get_all_sites(self):
        return self.all()
    
class Site(models.Model):
    name = models.CharField('name', max_length=32)
    url = models.URLField('url', max_length=255)
    default_promotion = models.URLField('default promotion', max_length=255)
    username = models.CharField('username', max_length=32)
    password = models.CharField('password', max_length=32)
    money = models.IntegerField('money')

    objects = SiteManager()
    
    def __unicode__(self):
        return self.name

class DealManager(models.Manager):
    def get_current_deals(self, city_id = None, status = None, order = None, is_today = None):
        queryset = self.filter(city__id__in=(city_id, settings.ALL_CITY_ID), publish_status=1)
        if status is not None:
            queryset = queryset.filter(status=status)
    	if is_today is not None:
    	    queryset = queryset.filter(created_at__gte=date.today())
    	if order is not None and order in ('current_price', '-current_price', 'volunteer', '-volunteer'):
    	    queryset = queryset.order_by(order)
    	else:
    	    queryset = queryset.order_by('-created_at')
        return queryset.select_related('site')
    
    def get_deals_by_city(self, city_id = None):
	return self.filter(city__id__in=(city_id, settings.ALL_CITY_ID), publish_status=1)

    def get_deals_by_tag(self, city_id = None, tag = None, order = None):
        queryset = self.filter(deal_tagging__tag=tag).distinct().order_by("-id")
	"""
        queryset = TaggedItem.objects.get_by_model(Deal, tag).order_by("-id")
	"""
        if city_id is not None:
            queryset = queryset.filter(city__id__in=(city_id, settings.ALL_CITY_ID))
        if order is not None and order in ('current_price', '-current_price', 'volunteer', '-volunteer'):
            queryset = queryset.order_by(order)
        else:
            queryset = queryset.filter(publish_status=1)
            queryset = queryset.order_by('status')
        return queryset
    
    def get_deals_by_category(self, city_id = None, category = None, except_deal_id = None, order = None):
        queryset = self.all()
        if city_id is not None:
            queryset = queryset.filter(city__id__in=(city_id, settings.ALL_CITY_ID))
        if category is not None:
            queryset = queryset.filter(category=category)
        if except_deal_id is not None:
            queryset = queryset.exclude(id=except_deal_id)
        if order is not None and order in ('current_price', '-current_price', 'volunteer', '-volunteer'):
            queryset = queryset.order_by(order)
        else:
        	queryset = queryset.filter(publish_status=1)
        	queryset = queryset.order_by('status')
        return queryset
    
    def get_deals_by_site(self, city_id = None, site = None):
        queryset = self.all()
        if city_id is not None:
            queryset = queryset.filter(city__id__in=(city_id, settings.ALL_CITY_ID))
        if site is not None:
            queryset = queryset.filter(site=site)
	queryset = queryset.filter(publish_status=1)
	queryset = queryset.order_by('status')
        return queryset
    
    def get_deals_by_company(self, city_id = None, company = None):
        queryset = self.all()
        if city_id is not None:
            queryset = queryset.filter(city__id__in=(city_id, settings.ALL_CITY_ID))
        if company is not None:
            queryset = queryset.filter(companies=company)
	queryset = queryset.filter(publish_status=1)
        return queryset
    
    def get_deals_by_local(self, city_id = None, local = None):
        queryset = self.all()
        if city_id is not None:
            queryset = queryset.filter(city__id__in=(city_id, settings.ALL_CITY_ID))
        if local is not None:
            queryset = queryset.filter(local=local)
	queryset = queryset.filter(publish_status=1)
	queryset = queryset.order_by('status')
        return queryset
    
    def get_deals_by_date(self, city_id = None, date = None, status = None, order = None):
        queryset = self.filter(city__id__in=(city_id, settings.ALL_CITY_ID), publish_status=1)
        if status is not None:
            queryset = queryset.filter(status=status)
	if date is not None:
	    queryset = queryset.filter(created_at__range=(date, date + timedelta(days=1)))
	if order is not None and order in ('current_price', '-current_price', 'volunteer', '-volunteer'):
	    queryset = queryset.order_by(order)
	else:
	    queryset = queryset.order_by('-created_at')
        return queryset.select_related('site')
    
    def get_deals_by_status(self, city_id = None, status = None):
        return ""
    
    def get_deal_by_id(self, deal_id):
        try:
            return self.get(pk=deal_id)
        except Deal.DoesNotExist:
            return None
        
    def get_deal_by_url(self, url):
        try:
            return self.get(url=url)
        except Deal.DoesNotExist:
            return None
    
class Deal(models.Model):
    name = models.CharField('name', max_length=255)
    category = models.ForeignKey(Category, blank=True, null=True)
    site = models.ForeignKey(Site, db_index=True)
    detail = models.TextField('detail')
    current_price = models.DecimalField('current price', max_digits=10, decimal_places=2)
    original_price = models.DecimalField('original price', max_digits=10, decimal_places=2)
    min_actor = models.IntegerField('min actor', blank=True, null=True)
    max_actor = models.IntegerField('max actor', blank=True, null=True)
    #city = models.ForeignKey(City, db_index=True, verbose_name='city', related_name = 'deal', blank=True, null=True)
    #local = models.ForeignKey(Local, db_index=True, verbose_name='local', related_name = 'deal', blank=True, null=True)
    city = models.ManyToManyField(City, db_index=True, blank=True, null=True)
    local = models.ManyToManyField(Local, db_index=True, blank=True, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICE, db_index=True, default='1')
    publish_status = models.SmallIntegerField(choices=PUBLISH_STATUS_CHOICE, db_index=True, default='1')
    created_at = models.DateTimeField('create date', db_index=True, auto_now_add=True)
    publish_at = models.DateTimeField('publish date', db_index=True, blank=True, null=True)
    begin_at = models.DateTimeField('begin date', db_index=True, blank=True, null=True)
    end_at = models.DateTimeField('end date', db_index=True, blank=True, null=True)
    accomplish_at = models.DateTimeField('accomplish date', blank=True, null=True)
    updated_at = models.DateTimeField('update date', auto_now=True)
    companies = models.ManyToManyField(Company, blank=True, null=True)
    company_name = models.CharField('company_name', max_length=255)
    company_detail = models.TextField('company_detail')
    volunteer = models.IntegerField('volunteer', default='0')
    url = models.URLField('url', max_length=255, unique=True, verify_exists=False)
    buy_url = models.URLField('buy_url', max_length=255, verify_exists=False, blank=True, null=True)
    logo = models.CharField('logo', max_length=255, blank=True, null=True)
    
    tags = TagField(null=True, blank=True)
    
    objects = DealManager()
    search = SphinxSearch(index="tuangou_deals_main", mode='SPH_SORT_EXTENDED',)
    
    def __unicode__(self):
        return self.name
    
    def get_saving(self):
        return self.original_price - self.current_price
    
    def get_discount(self):
        try:
            x = self.current_price / self.original_price * 10
        except:
            x = 0
        return x
    
    def get_litpic_path(self):
        try:
            pic = Picture.objects.get(deal=self, is_main=True)
            path = pic.path
        except:
            path = "/site_media/images/img-no.gif"
        return path
    
    def get_rest_time(self):
        now = datetime.now()
        rest_day = self.end_at - now
        result = {'day': rest_day.days, 'hour': rest_day.seconds / 3600, 'minute': (rest_day.seconds % 3600) / 60}
        return result
    
    def get_comments_count(self):
        return Comment.objects.get_comments_counts(self.id)
    
    def get_up_vote_count(self):
        return Vote.objects.filter(deal__id=self.id, score='1').count()
    
    def get_dw_vote_count(self):
        return Vote.objects.filter(deal__id=self.id, score='-1').count()
    
    def get_main_city(self):
	try:
            return self.city.values()[0]
	except:
	    city = City.objects.get(id=settings.ALL_CITY_ID)
	    return city.__dict__

    def get_absolute_url(self):
	city = self.get_main_city()
	return "/%s/d_%d.html" % (city['abbreviation'], self.id)
    
class AutoCategoryAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'power')

class DealAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'tags', 'site', 'url',)
    list_filter = ('status', 'category', 'site')
    search_fields = ['name']
    actions = ['add_category', 'add_tag']

    class Media:
        js = ['/admin_media/jquery/jquery-1.4.2.min.js', '/admin_media/tinymce/jscripts/tiny_mce/tiny_mce.js', '/admin_media/tinymce_setup/tinymce_setup.js',]
    
    def add_category(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect(reverse('admin_add_category') + ("?ids=%s" % ",".join(selected)))
    add_category.short_description = u"给团购信息添加分类"
    
    def add_tag(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect(reverse('admin_add_tag') + ("?ids=%s" % ",".join(selected)))
    add_tag.short_description = u"给团购信息添加标签"        

class CommentManager(models.Manager):
    def get_comments_by_deal_id(self, deal_id = None):
        return self.filter(deal__id=deal_id)
    
    def get_comments_counts(self, deal_id = None):
        try:
            return self.filter(deal__id=deal_id).count()
        except:
            return 0
    
class Comment(models.Model):
    user = models.ForeignKey(User, db_index=True, related_name='user_comment')
    deal = models.ForeignKey(Deal, db_index=True, related_name='deal_comment')
    replay = models.CharField('replay', max_length=255, blank=True, null=True)
    created_at = models.DateTimeField('create date', db_index=True, auto_now_add=True)

    objects = CommentManager()
    
    def __unicode__(self):
        return self.user.name + '_' + self.deal.name
    
class Tagging(models.Model):
    user = models.ForeignKey(User, db_index=True, related_name='user_tagging')
    deal = models.ForeignKey(Deal, db_index=True, related_name='deal_tagging')
    tag = models.ForeignKey(Tag, db_index=True, related_name="tag_tagging")
    
    class Meta:
        unique_together = (("user", "deal", "tag"),)
    
class Vote(models.Model):
    user = models.ForeignKey(User, db_index=True, related_name='user_vote')
    deal = models.ForeignKey(Deal, db_index=True, related_name='deal_vote')
    score = models.SmallIntegerField(db_index=True)
    created_at = models.DateTimeField('create date', db_index=True, auto_now_add=True)
    
    def __unicode__(self):
        return self.user.name + '_' + self.deal.name

    class Meta:
        unique_together = (("user", "deal"),)
    
class PromotionManager(models.Manager):
    def get_promotions_by_user(self, user_id = None):
        return self.filter(user__id = user_id)
    
class Promotion(models.Model):
    user = models.ForeignKey(User, db_index=True, related_name='user_promotion')
    site = models.ForeignKey(Site, related_name='site_promotion')
    url = models.URLField('url', max_length=255)
    
    objects = PromotionManager()
    
    def __unicode__(self):
        return self.user.name + '_' + self.site.name

    class Meta:
        unique_together = (("user", "site"),)

class TransferManager(models.Manager):
    def get_transfers_by_city(self, city_id = None):
        return self.filter(deal__city__id__in=(city_id, settings.ALL_CITY_ID))
    
    def get_transfers_by_deal(self, deal_id = None):
        return self.filter(deal__id = deal_id)
    
    def get_transfers_by_user(self, user_id = None):
        return self.filter(user__id = user_id)
    
    def get_transfers_by_category(self, city_id = None, category = None):
        queryset = self.all()
        if city_id is not None:
            queryset = queryset.filter(deal__city__id__in=(city_id, settings.ALL_CITY_ID))
        if category is not None:
            queryset = queryset.filter(category=category)
        return queryset
    
    def get_transfers_by_tag(self, city_id = None, tag = None):
        queryset = TaggedItem.objects.get_by_model(Transfer, tag).order_by("-id")
        if city_id is not None:
            queryset = queryset.filter(deal__city__id__in=(city_id, settings.ALL_CITY_ID))
        return queryset
    
    def get_transfer_by_id(self, transfer_id):
        try:
            return self.get(pk=transfer_id)
        except Transfer.DoesNotExist:
            return None
    
class UserCity(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name = 'city_user')
    city = models.ForeignKey(City, db_index=True, verbose_name='city', related_name = 'user_city')
    
    def __unicode__(self):
	return self.user.name + '_' + self.city.name

class Transfer(models.Model):
    user = models.ForeignKey(User, db_index=True, related_name='user_transfer')
    deal = models.ForeignKey(Deal, db_index=True, null=True, blank=True, related_name='deal_transfer')
    name = models.CharField('name', max_length=255)
    category = models.ForeignKey(Category, blank=True, null=True)
    detail = models.TextField('detail')
    price = models.DecimalField('price', max_digits=10, decimal_places=2)
    count = models.IntegerField('count')
    type = models.SmallIntegerField(choices=TRANSFER_TYPE_CHOICE, db_index=True, default='1')
    status = models.SmallIntegerField(choices=TRANSFER_STATUS_CHOICE, db_index=True, default='1')
    created_at = models.DateTimeField('create date', db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField('update date', auto_now=True)
    tags = TagField(null=True, blank=True)
    contact = models.CharField('contact', max_length=255)
    city = models.ForeignKey(City, db_index=True, related_name='city_transfer')
        
    objects = TransferManager()
    
    def __unicode__(self):
        return self.name + '_' + self.user.name
    
"""
class Picture(models.Model):
    deal = models.ForeignKey(Deal, db_index=True, related_name='deal_picture')
    name = models.CharField('name', max_length=255)
    path = models.ImageField('path', max_length=255, upload_to='deal_pic/%Y/%m/%d', delete=True)
    is_main = models.BooleanField('is main', db_index=True)
    created_at = models.DateTimeField('create date', db_index=True, auto_now_add=True)

    def __unicode__(self):
        return self.deal.name + '_' + self.name
"""

class SiteJoin(models.Model):
    site_name = models.CharField('site name', max_length=255)
    site_domain = models.CharField('site domain', max_length=64)
    online_date = models.DateField('online date')
    owner = models.CharField('owner', max_length=255)
    email = models.EmailField('email')
    im = models.CharField('im', max_length=32, blank=True, null=True)
    phone = models.CharField('phone', max_length=32, blank=True, null=True)
    address = models.CharField('address', max_length=255, blank=True, null=True)
    exchange = models.SmallIntegerField(choices=EXCHANGE_CHOICE, default='1')
    created_at = models.DateTimeField('create date', db_index=True, auto_now_add=True)

    def __unicode__(self):
        return self.site_name    

class ContactUs(models.Model):
    title = models.CharField('title', max_length=255)
    content = models.TextField('content')
    created_at = models.DateTimeField('create date', db_index=True, auto_now_add=True)

admin.site.register(Category)
admin.site.register(Deal, DealAdmin)
admin.site.register(Site)
admin.site.register(Comment)
admin.site.register(City)
admin.site.register(Local)
admin.site.register(Promotion)
admin.site.register(Company)
admin.site.register(UserCity)
admin.site.register(Transfer)
#admin.site.register(Picture)
admin.site.register(Vote)
admin.site.register(AutoCategory, AutoCategoryAdmin)
admin.site.register(SiteJoin)
admin.site.register(ContactUs)
