#-*-coding:utf8;-*-
from deal.models import Deal, Site, Tagging, City
from django.db.models import Count
from tagging.models import Tag
from django.conf import settings
import re

def deal_filter(keyword, url):
    rt = []
    site_id = 0
    try:
        deal = Deal.objects.get(url=url)
        return [deal]
    except:
        pass
    sites = Site.objects.all()
    for site in sites:
        if url.find(site.url) != -1:
            site_id = site.id
    if site_id == 0:
        queryset = queryset = Deal.search.query('@name '+keyword)
    else:
        filter = {'site_id': site_id}
        queryset = queryset = Deal.search.query('@name '+keyword).filter(**filter)
    if len(queryset) > 0:
	return queryset.select_related()
    queryset = ''
    keywords = split_word(keyword)
    key = ''
    for k in keywords:
	key += k + '|'
    if len(key) != 0 and key[len(key) - 1] == '|':
	key = key[:len(key)-1] 
    if site_id == 0:
        queryset = queryset = Deal.search.query('@name '+key)
    else:
        filter = {'site_id': site_id}
        queryset = queryset = Deal.search.query('@name '+key).filter(**filter)
    return queryset.select_related()

def is_cn_char(i):
    return 0x4e00<=ord(i)<0x9fa6

def is_alnum(i):
    if re.search('[\w]', i) is None:
        return False
    else:
        return True

def split_word(word):
    rt = []
    i = 0
    while i < len(word):
        t = ''
        k = word[i]
        if is_alnum(k):
            t += k
            while i + 1 != len(word) and is_alnum(word[i + 1]):
                t += word[i + 1]
                i += 1
        elif is_cn_char(k):
            t += k
            if i + 1 != len(word) and is_cn_char(word[i + 1]):
                t += word[i + 1]
        i += 1
        if len(t) > 1:
            rt.append(t)
    return rt

def add_tagging(user_id, deal_id, tag_string):
    tags = tag_string.split(' ')
    for t in tags:
	tag, created = Tag.objects.get_or_create(name=t, defaults={'name':t})
	try:
	    tagging = Tagging(user_id=user_id, deal_id=deal_id, tag=tag)
	    tagging.save()
	except:
	    pass
    return ''

def get_user_tagging(user_id, count = 10):
    return Tagging.objects.filter(user__id=user_id).annotate(count_tag = Count('tag')).order_by('-count_tag')[:count]

def get_deal_tagging(deal_id, count = 10):
    return Tagging.objects.filter(deal__id=deal_id).annotate(count_tag = Count('tag')).order_by('-count_tag')[:count]


def get_city(request):
    city_id = request.session.get('city_id', None)
    city_abbreviation = request.session.get('city_abbreviation', None)
    """
    if city_abbreviation != request.META.get('SUB_DOMAIN'):
        city_abbreviation = request.META.get('SUB_DOMAIN')
        city = City.objects.get(abbreviation=city_abbreviation)
        city_id = city.id
        request.session['city_id'] = city_id
        request.session['city_abbreviation'] = city_abbreviation
    """
    if city_abbreviation is None:
        city_domain = None
    else:
        city_domain = city_abbreviation + settings.PROJECT_DOMAIN
    return {'id':city_id, 'abbreviation':city_abbreviation, 'domain':city_domain}

def set_city(request, city_abbreviation):
    city = City.objects.get(abbreviation=city_abbreviation)
    city_id = city.id
    request.session['city_id'] = city_id
    request.session['city_abbreviation'] = city_abbreviation
    city_domain = city_abbreviation + settings.PROJECT_DOMAIN
    return {'id':city_id, 'abbreviation':city_abbreviation, 'domain':city_domain, 'name':city.name}

