#-*-coding:utf8;-*-
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
import pykx.djangokx as sns
from member.models import User
from deal.models import Category, City, Company, Comment, Deal, Local, Site, Transfer, Vote
from deal.func import get_city, set_city

@sns.require_login()
def index(request, city_abbreviation, status=1, template_name="kaixin001/index.html"):
    print "in"
    choose_city = request.GET.get('choose')
    city = get_city(request)
    if city_abbreviation is None:
        if city['id'] is None or choose_city is not None:
            template_name="www/city.html"
            return render_to_response(template_name, {
            }, context_instance=RequestContext(request))
    city = City.objects.get_city_by_abbreviation(city['abbreviation'])
    if city is None:
        raise Http404
    set_city(request, city.abbreviation)
    order = request.GET.get('order')
    if order == "" or order not in('current_price', '-current_price', 'volunteer', '-volunteer'):
        order = None
    is_today = request.GET.get('is_today')
    if is_today == "":
        is_today = None
    deals = Deal.objects.get_current_deals(city.id, status, order, is_today)
    comments = Comment.objects.all().order_by('-created_at')[:20]
    return render_to_response(template_name, {
	'city':city,
	'deals':deals,
	'status':status,
	'is_today':is_today,
	'order':order,
	'comments':comments,
    }, context_instance=RequestContext(request))

def deal(request, deal_id, template_name="kaixin001/deal.html"):
    deal = Deal.objects.get_deal_by_id(deal_id)
    if deal is None:
        raise Http404
    return render_to_response(template_name, {
        'deal':deal,
    }, context_instance=RequestContext(request))

def site(request, site_name, template_name="www/index.html"):
    city = get_city(request)
    try:
        site = Site.objects.get(name=site_name)
    except:
        raise Http404
    deals = Deal.objects.get_deals_by_site(city_id=city['id'], site=site)
    return render_to_response(template_name, {
        'site':site,
        'deals':deals,
    }, context_instance=RequestContext(request))

def search_post(request, template_name="kaixin001/index.html"):
    if request.method == "POST":
        search_keyword = request.POST['search_keyword']
        return HttpResponseRedirect(reverse("kaixin001_search", request.urlconf, args=(city_abbreviation,search_keyword,)))
    else:
        return HttpResponseRedirect(reverse("kaixin001_city_index"))

def search(request, keyword=None, template_name="kaixin001/index.html"):
    city = get_city(request)
    filter = {'city_id': (city['id'], settings.ALL_CITY_ID)}
    queryset = Deal.search.query(keyword).filter(**filter)
    queryset = queryset.order_by('status', '@weight', '@id')
    
    deals = queryset.select_related()
    
    return render_to_response(template_name, {
        'keyword':keyword,
        'deals':deals,
    }, context_instance=RequestContext(request))

def category(request, category_name=None, template_name="kaixin001/category.html"):
    city = get_city(request)
    try:
        category = Category.objects.get(id=category_name)
        #category = Category.objects.get(name=category_name)
    except:
        raise Http404
    
    order = request.GET.get('order')
    if order == "" or order not in('current_price', '-current_price', 'volunteer', '-volunteer'):
        order = None
            
    deals = Deal.objects.get_deals_by_category(city_id=city['id'], category=category, order=order)
    return render_to_response(template_name, {
        'category':category,
        'deals':deals,
        'order' : order
    }, context_instance=RequestContext(request))

def test(request, template_name="kaixin001/test.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

