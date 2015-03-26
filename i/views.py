#-*-coding:utf8;-*-
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from member.models import User
from deal.models import Deal, City, Deal, Site, Promotion, Transfer
from deal.func import deal_filter
from i.func import is_owner
from i.models import Mydeal
from i.forms import MydealAddStepOneForm, MydealAddStepTwoForm
from www.views import get_city
from www.func import _deal_review_info
import member as sns

#@sns.require_login()
def index(request, template_name="i/index.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

def user(request, user_id, template_name="i/user.html"):
    city = get_city(request)
    user = User.objects.get_user_by_id(user_id)
    if user is None:
        raise Http404
    owner = is_owner(request, user_id)
    mydeals = Mydeal.objects.filter(user=user, type=1)
    
    return render_to_response(template_name, {
        'city':city,
        'user':user,
        'is_owner':owner,
        'mydeals': mydeals,
    }, context_instance=RequestContext(request))

@sns.require_login()
def bind(request, template_name="i/bind.html"):
    sites = Site.objects.get_all_sites()
    promotions = Promotion.objects.get_promotions_by_user(request.myuser.id)
    user_promotions = []
    for site in sites:
        value = site.__dict__
        has_promotion = False
        for promotion in promotions:
            if promotion.site == site:
                has_promotion = True
                value['promotion'] = promotion.url
                break
        if not has_promotion:
            value['promotion'] = None
        user_promotions.append(value)
    return render_to_response(template_name, {
        'promotions':user_promotions,
    }, context_instance=RequestContext(request))

def link(request, user_id, template_name="i/index.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

def transfer(request, user_id, template_name="i/transfer.html"):
    user = User.objects.get_user_by_id(user_id)
    if user is None:
        raise Http404
    owner = is_owner(request, user_id)
    transfers = Transfer.objects.get_transfers_by_user(user_id)
    return render_to_response(template_name, {
        'user':user,
        'is_owner':owner,
        'transfers':transfers,
    }, context_instance=RequestContext(request))

def promotion(request, user_id, city_abbreviation, template_name="i/promotion.html"):
    if city_abbreviation is None:
        city_id = settings.DEFAULT_CITY_ID
    else:
        city = City.objects.get_city_by_abbreviation(city_abbreviation)
        if city is None:
            raise Http404
        city_id = city.id
    user = User.objects.get_user_by_id(user_id)
    if user is None:
        raise Http404
    promotions = Promotion.objects.get_promotions_by_user(user.id)
    promotion_sites = []
    promotion_links = []
    for promotion in promotions:
        promotion_sites.append(promotion.site)
        promotion_links.append((promotion.site.id, promotion.url))
    deals = Deal.objects.get_current_deals(city_id, status=1)
    return render_to_response(template_name, {
        'user':user,
        'promotion_sites':promotion_sites,
        'promotion_links':promotion_links,
        'deals':deals,
	'city':city,
    }, context_instance=RequestContext(request))
    
@sns.require_login()
def mydeal(request, template_name="i/mydeal.html"):
    city = get_city(request)
    mydeals = Mydeal.objects.filter(user=request.myuser)
    return render_to_response(template_name, {
            'city': city,
            'mydeals' : mydeals,
    }, context_instance=RequestContext(request))

@sns.require_login()
def mydeal_add(request, template_name="i/mydeal_add.html"):
    city = get_city(request)
    if request.method == "POST":
        step = request.POST['step']
        if step == '1':
            # 通过我的团购链接添加，进入这里，取搜索接口，列出可能正确的团购
            form1 = MydealAddStepOneForm(request.POST)
            if form1.is_valid():
                form2 = MydealAddStepTwoForm(initial={'step': 2, 
                                                      'name':form1.cleaned_data['name'], 
                                                      'url' : form1.cleaned_data['url']})
                
                deal_suggests = deal_filter(form1.cleaned_data['name'], form1.cleaned_data['url'])
                
                return render_to_response(template_name, {
                    'city' : city,
                    'form' : form2,
                    'deal_suggests' : deal_suggests,
                }, context_instance=RequestContext(request))
            else:
                return render_to_response(template_name, {
                    'form' : form1,
                }, context_instance=RequestContext(request))                
        elif step == '2':
            # save info
            form2 = MydealAddStepTwoForm(request.POST)
            if form2.is_valid():
                mydeal_info = form2.save(commit=False)
                mydeal_info.user_id = request.myuser.id
                if form2.cleaned_data['deal'] is not None:
                    try:
                        deal = Deal.objects.get(pk=form2.cleaned_data['deal'])
                        mydeal_info.deal = deal
                        mydeal_info.save()
                    except:
                        pass
                else:
                    mydeal_info.save()
                return HttpResponseRedirect(reverse("i_mydeal"))
            else:
                return render_to_response(template_name, {
                    'form' : form2,
                }, context_instance=RequestContext(request))                
        else:
            #error
            pass
    else:
        try:
            deal_id = int(request.GET['deal_id'])
        except:
            deal_id = None
            
        if deal_id is not None:
            # got deal_id, goto step 2
            try:
                deal = Deal.objects.get(pk=deal_id)
            except:
                raise Http404
            form = MydealAddStepTwoForm(initial={'step': 2, 
                                                 'deal': deal_id, 
                                                 'name':deal.name, 
                                                 'url' : deal.url,
                                                 'site': deal.site.name,
                                                 'price': deal.current_price, })
            return render_to_response(template_name, {
                'form' : form,
            }, context_instance=RequestContext(request))
        else:
            form = MydealAddStepOneForm(initial={'step': 1})
            return render_to_response(template_name, {
                'form' : form,
            }, context_instance=RequestContext(request))

@sns.require_login()
def mydeal_edit(request, id=None, template_name="i/mydeal_edit.html"):
    city = get_city(request)
    if request.method == "POST":
        try:
            mydeal_info = Mydeal.objects.get(id=id)
        except:
            raise Http404
        form = MydealAddStepTwoForm(request.POST)
        if form.is_valid():
            mydeal_info.name = form.cleaned_data['name']
            mydeal_info.url = form.cleaned_data['url']
            mydeal_info.site = form.cleaned_data['site']
            mydeal_info.price = form.cleaned_data['price']
            mydeal_info.account = form.cleaned_data['account']
            mydeal_info.type = form.cleaned_data['type']
            mydeal_info.status = form.cleaned_data['status']
            mydeal_info.used_at = form.cleaned_data['used_at']
            mydeal_info.limit = form.cleaned_data['limit']
            mydeal_info.deadline = form.cleaned_data['deadline']
            mydeal_info.reserve = form.cleaned_data['reserve']
            mydeal_info.save()
            return HttpResponseRedirect(reverse("i_mydeal"))
        else:
            return render_to_response(template_name, {
                'form' : form,
            }, context_instance=RequestContext(request))            
    else:
        mydeal_id = id
        try:
            mydeal = Mydeal.objects.get(id=mydeal_id)
        except:
            raise Http404
       
       	if mydeal.deal is not None:
	        form = MydealAddStepTwoForm(initial={'step': 2,
	                                             'deal': mydeal.deal.id, 
	                                             'name': mydeal.name, 
	                                             'url' : mydeal.url,
	                                             'site': mydeal.site,
	                                             'price': mydeal.price, 
	                                             'account': mydeal.account,
	                                             'type': mydeal.type,
	                                             'status': mydeal.status,
	                                             'limit': mydeal.limit,
	                                             'used_at': mydeal.used_at,
	                                             'deadline': mydeal.deadline,
                                                 'reserve': mydeal.reserve, })        
	        return render_to_response(template_name, {
	            'form' : form,
	        }, context_instance=RequestContext(request))
	else:
		deal_suggests = deal_filter(mydeal.name, mydeal.url)
	        form = MydealAddStepTwoForm(initial={'step': 2,
	                                             'name': mydeal.name, 
	                                             'url' : mydeal.url,
	                                             'site': mydeal.site,
	                                             'price': mydeal.price, 
	                                             'account': mydeal.account,
	                                             'type': mydeal.type,
	                                             'status': mydeal.status,
	                                             'limit': mydeal.limit,
	                                             'used_at': mydeal.used_at,
	                                             'deadline': mydeal.deadline,
                                                 'reserve': mydeal.reserve, })        
	        return render_to_response(template_name, {
	            'form' : form,
		    'deal_suggests' : deal_suggests,
		    'city': city,
	        }, context_instance=RequestContext(request))

@sns.require_login()
def mydeal_del(request, id=None, template_name="i/mydeal_del.html"):
    try:
        mydeal = Mydeal.objects.get(id=id)
        mydeal.delete()
    except:
        raise Http404
    return HttpResponseRedirect(reverse("i_mydeal"))

@sns.require_login()
def mydeal_change_status(request, id=None, template_name="i/mydeal_add.html"):
    try:
        mydeal = Mydeal.objects.get(id=id)
        mydeal.status = 2
        mydeal.save()
    except:
        raise Http404
    return HttpResponseRedirect(reverse("i_mydeal"))

def deal_review_info(request, deal_id):
    return _deal_review_info(request, deal_id)
