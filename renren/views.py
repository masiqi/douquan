#-*-coding:utf8;-*-
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
import pyxn.djangoxn as sns
from member.models import User
from deal.models import Category, City, Company, Comment, Deal, Local, Site, Transfer, Vote, UserCity

@csrf_exempt
@sns.require_add()
def index(request, city_abbreviation, status=1, template_name="renren/index.html"):
    if city_abbreviation is None:
	try:
	    city = request.myuser.city_user.city
	except:
            template_name="renren/city.html"
            return render_to_response(template_name, {
            }, context_instance=RequestContext(request))
    else:
        city = City.objects.get_city_by_abbreviation(city_abbreviation)
	try:
	    c = request.myuser.city_user.city
	    if c != city:
		request.myuser.city_user.city = city
		request.myuser.city_user.save()
	except:
	    request.myuser.city_user = UserCity(user=request.myuser, city=city)
	    request.myuser.city_user.save()
    if city is None:
        raise Http404
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

def preinstall(request, template_name="renren/preinstall.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

def test(request, template_name="kaixin001/test.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

