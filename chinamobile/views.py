#-*-coding:utf8;-*-
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
import py139.django139 as sns
from member.models import User
from deal.models import Category, City, Company, Comment, Deal, Local, Site, Transfer, Vote
from deal.func import get_city, set_city

@sns.require_login()
def index(request, city_abbreviation, status=1, template_name="chinamobile/index.html"):
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

def test(request, template_name="chinamobile/test.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

