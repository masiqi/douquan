#-*-coding:utf8;-*-
import base64
import time, datetime
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from deal.models import Category, City, Company, Comment, Deal, Local, Site, Transfer, Vote
from i.models import Mydeal
from deal.forms import WriteCommentForm, WriteTransferForm, WriteReviewForm, SiteJoinForm, ContactUsForm, DealTransferAddStepOneForm, DealTransferAddStepTwoForm
from deal.func import add_tagging, get_user_tagging, get_deal_tagging, get_city, set_city, deal_filter
from www.func import _deal_review_info
from member.func import is_login
from tagging.models import Tag, TaggedItem
import member as sns
import json

def index(request, city_abbreviation, status=1, template_name="www/index.html"):
    """
    subdomain = request.META.get('SUB_DOMAIN')
    if subdomain == "www":
        if request.session.get('city_abbreviation', None) is None:
            template_name="www/city.html"
            return render_to_response(template_name, {
            }, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect('http://'+request.session.get('city_abbreviation')+settings.PROJECT_DOMAIN)
    """
    choose_city = request.GET.get('choose')
    city = get_city(request)
    if city_abbreviation is None:
        if city['id'] is None or choose_city is not None:
            template_name="www/city.html"
            return render_to_response(template_name, {
            }, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(reverse("www_city_index", request.urlconf, args=(city['abbreviation'],)))
        
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if city is None:
        raise Http404
    
    city = set_city(request, city_abbreviation)
    order = request.GET.get('order')
    if order == "" or order not in('current_price', '-current_price', 'volunteer', '-volunteer'):
        order = None
    is_today = request.GET.get('is_today')
    if is_today == "":
        is_today = None
    deals = Deal.objects.get_current_deals(city['id'], status, order, is_today)
    
    comments = Comment.objects.all().select_related().order_by('-created_at')[:20]
    
    return render_to_response(template_name, {
        'city':city,
        'deals':deals,
        'status':status,
        'is_today' : is_today,
        'order' : order,
        'comments': comments,
        #'deals':deal_list,
    }, context_instance=RequestContext(request))


def search_post(request, city_abbreviation, template_name="www/index.html"):
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if request.method == "POST":
        search_keyword = request.POST['search_keyword']
        url = "/" + city.abbreviation + "/s_" + search_keyword + ".html"
        return HttpResponseRedirect(reverse("www_search", request.urlconf, args=(city_abbreviation,search_keyword,)))
    else:
        return HttpResponseRedirect(reverse("www_city_index", request.urlconf, args=(city['abbreviation'],)))    

def search(request, city_abbreviation, keyword=None, template_name="www/index.html"):
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if city is None:
        raise Http404
    filter = {'city_id': (city.id, settings.ALL_CITY_ID)}
    queryset = Deal.search.query(keyword).filter(**filter)
    queryset = queryset.order_by('status', '@weight', '@id')
    
    deals = queryset.select_related()
    
    return render_to_response(template_name, {
        'keyword':keyword,
        'deals':deals,
        'city':city,
    }, context_instance=RequestContext(request))

def transfer(request, city_abbreviation, transfer_id, template_name="www/transfer.html"):
    transfer = Transfer.objects.get_transfer_by_id(transfer_id)
    if transfer is None:
        raise Http404
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if city is None:
        raise Http404
    return render_to_response(template_name, {
        'deal':transfer.deal,
        'city':city,
        'transfer':transfer,
    }, context_instance=RequestContext(request))

def transfer_index(request, city_abbreviation, template_name="www/transfer_index.html"):
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if city is None:
        raise Http404
    transfers = Transfer.objects.get_transfers_by_city(city.id)
    return render_to_response(template_name, {
        'city':city,
        'transfers':transfers,
    }, context_instance=RequestContext(request))

def deal(request, city_abbreviation, deal_id, form_class=WriteCommentForm, template_name="www/deal.html"):
    deal = Deal.objects.get_deal_by_id(deal_id)
    if deal is None:
        raise Http404
    #city = get_city(request)
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if city is None:
        raise Http404
    form = form_class(initial={'deal':deal.id})
    return render_to_response(template_name, {
        'city':city,
        'deal':deal,
        'form':form,
        'is_login':is_login(request),
    }, context_instance=RequestContext(request))

#@sns.require_login()
def deal_vote(request, city_abbreviation, deal_id, template_name="www/deal_transfer.html"):
    score = request.GET.get('score')
    if score != '1' and score != '-1':
	return HttpResponse(json.dumps({'status':0, 'reason':'illegal score'}), mimetype='text/html')
    deal = Deal.objects.get_deal_by_id(deal_id)
    if deal is None:
	return HttpResponse(json.dumps({'status':0, 'reason':'deal does not exist'}), mimetype='text/html')
    if request.myuser is None:
	return HttpResponse(json.dumps({'status':0, 'reason':'need login'}), mimetype='text/html')
    user_id = request.myuser.id
    vote, created = Vote.objects.get_or_create(user__id=user_id, deal=deal, defaults={'user_id':user_id, 'deal':deal, 'score':score})
    if created:
	return HttpResponse(json.dumps({'status':1, 'reason':'success'}), mimetype='text/html')
    else:
	return HttpResponse(json.dumps({'status':0, 'reason':'you have voted before'}), mimetype='text/html')
    
def deal_review_info(request, deal_id):
    return _deal_review_info(request, deal_id)
    
@sns.require_login()
def deal_transfer(request, city_abbreviation, deal_id, form_class=WriteTransferForm, template_name="www/deal_transfer.html"):
    deal = Deal.objects.get_deal_by_id(deal_id)
    if deal is None:
        raise Http404
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if deal is None:
        raise Http404
    if request.method == "GET":
        type = request.GET.get('type', 1)
        form = form_class(initial={'deal':deal.id, 'type':type})
        return render_to_response(template_name, {
            'city':city,
            'deal':deal,
            'form':form,
        }, context_instance=RequestContext(request))
    else:
        form = form_class(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.user_id = request.myuser.id
            transfer.name = deal.name
            transfer.detail = deal.detail
            transfer.category = deal.category
            transfer.tags = deal.tags
            transfer.status = deal.status
            transfer.save()
            return HttpResponseRedirect(reverse("www_deal", request.urlconf, args=(city_abbreviation, transfer.deal_id))) 
        else:
            return render_to_response(template_name, {
                'city':city,
                'deal':deal,
                'form':form,
            }, context_instance=RequestContext(request))

@sns.require_login()
def deal_transfer_add(request, city_abbreviation, template_name="www/deal_transfer_add.html"):
    if request.method == "POST":
        step = request.POST['step']
        if step == '1':
            form1 = DealTransferAddStepOneForm(request.POST)
            if form1.is_valid():
                form2 = DealTransferAddStepTwoForm(initial={'step': 2, 
                                                      'name':form1.cleaned_data['name'],
                                                      'city': city_abbreviation,
                                                      })
                #deal_suggests = deal_filter(form1.cleaned_data['name'], '')
                deal_suggests = []
                
                return render_to_response(template_name, {
                    'form' : form2,
                    'deal_suggests' : deal_suggests,
                    'city' : city_abbreviation,
                }, context_instance=RequestContext(request))
            else:
                return render_to_response(template_name, {
                    'form' : form1,
                }, context_instance=RequestContext(request))
        elif step == '2':
            # save info
            form2 = DealTransferAddStepTwoForm(request.POST)
            if form2.is_valid():
                transfer = form2.save(commit=False)
                transfer.user_id = request.myuser.id
                if form2.cleaned_data['deal'] is not None:
                    try:
                        deal = Deal.objects.get(pk=form2.cleaned_data['deal'])
                        transfer.deal = deal
                    except:
                        raise Http404
                try:
                    city = City.objects.get(abbreviation=form2.cleaned_data['city'])
                    transfer.city = city
                    transfer.save()
                except:
                    raise Http404
                transfer.save()
                return HttpResponseRedirect(reverse("www_transfer_index", request.urlconf, args=(city_abbreviation,)))
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
            form = DealTransferAddStepTwoForm(initial={'step': 2, 
                                                 'deal': deal_id, 
                                                 'name':deal.name,
                                                 'price': deal.current_price, 
                                                 'city': city_abbreviation, })
            return render_to_response(template_name, {
                'form' : form,
            }, context_instance=RequestContext(request))
        else:
            form = DealTransferAddStepOneForm(initial={'step': 1})
            return render_to_response(template_name, {
                'form' : form,
            }, context_instance=RequestContext(request))

def deal_comment(request, city_abbreviation, deal_id, form_class=WriteCommentForm, template_name="www/deal_comment.html"):
    deal = Deal.objects.get_deal_by_id(deal_id)
    if deal is None:
        raise Http404
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if deal is None:
        raise Http404
    form = form_class(initial={'deal':deal.id})
    comments = Comment.objects.get_comments_by_deal_id(deal.id)
    return render_to_response(template_name, {
        'city':city,
        'deal':deal,
        'form':form,
        'comments':comments,
        'is_login':is_login(request),
    }, context_instance=RequestContext(request))
        
@sns.require_login()
def write_comment(request, city_abbreviation, template_name="blog/write_blog.html", form_class=WriteCommentForm):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user_id = request.myuser.id
            comment.save()
            return HttpResponseRedirect(reverse("www_deal", request.urlconf, args=(city_abbreviation, comment.deal_id))) 
        else:
            raise Http404
    else:
        return HttpResponseRedirect(reverse("www_index"))

@sns.require_login()
def write_review(request, form_class=WriteReviewForm):
    city = get_city(request)
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            deal_id = form.cleaned_data['deal_id']
            mydeal_id = form.cleaned_data['mydeal_id']
            act = form.cleaned_data['act']
            vote = form.cleaned_data['vote']
            tags = form.cleaned_data['tag']
            comment = form.cleaned_data['comment']
            if act == 'used':
                try:
                    mydeal = Mydeal.objects.get(id=mydeal_id)
                    mydeal.status = 2
                    mydeal.save()
                except:
                    raise Http404
                if deal_id is not None or deal_id != '':
                    try:
                        deal = Deal.objects.get(pk=deal_id)
                    except:
                        raise Http404
                    if tags is not None or tags != '':
                        add_tagging(request.myuser.id, deal.id, tags)
                    if comment is not None or comment != '':
                        comment_form = WriteCommentForm({'deal':deal.id,
                                                         'user':request.myuser.id,
                                                         'replay':comment})
                        if comment_form.is_valid():
                            comment = comment_form.save(commit=False)
                            comment.user_id = request.myuser.id
                            comment.save()
                        else:
                            raise Http404
                return HttpResponseRedirect(settings.I_DOUQUAN_INDEX + reverse("i_mydeal", 'douquan.i.urls'))
            elif act == 'paid':
                try:
                    deal = Deal.objects.get(pk=deal_id)
                except:
                    raise Http404
                if vote == 0:
                    score = '1'
                elif vote == 1:
                    score = '-1'
                else:
                    score = None
                if score is not None:
                    vote, created = Vote.objects.get_or_create(user__id=request.myuser.id, deal=deal, defaults={'user_id':request.myuser.id, 'deal':deal, 'score':score})
                if tags is not None and tags != '':
                    add_tagging(request.myuser.id, deal.id, tags)
                if comment is not None and comment != "":
                    comment_form = WriteCommentForm({'deal':deal.id,
                                                     'user':request.myuser.id,
                                                     'replay':comment})
                    if comment_form.is_valid():
                        comment = comment_form.save(commit=False)
                        comment.user_id = request.myuser.id
                        comment.save()
                    else:
                        raise Http404
                return HttpResponseRedirect(reverse("www_deal", request.urlconf, args=(city['abbreviation'], deal_id)))                        
            elif act == 'wish':
                pass
            else:
                pass
            return HttpResponseRedirect(reverse("www_deal", request.urlconf, args=(city['abbreviation'], deal_id)))
        else:
            raise Http404
    else:
        return HttpResponseRedirect(reverse("www_index"))

def user(request, user_id, template_name="www/index.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

def category(request, city_abbreviation, category_name=None, template_name="www/category.html"):
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if city is None:
        raise Http404
    try:
        category = Category.objects.get(id=category_name)
        #category = Category.objects.get(name=category_name)
    except:
        raise Http404
    
    order = request.GET.get('order')
    if order == "" or order not in('current_price', '-current_price', 'volunteer', '-volunteer'):
        order = None
            
    deals = Deal.objects.get_deals_by_category(city_id=city.id, category=category, order=order)
    return render_to_response(template_name, {
        'city':city,
        'category':category,
        'deals':deals,
        'order' : order
    }, context_instance=RequestContext(request))

def date(request, city_abbreviation, date=None, template_name="www/index.html"):
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if city is None:
        raise Http404
    order = request.GET.get('order')
    try:
        t = time.strptime(date, '%Y-%m-%d')
	y,m,d = t[0:3]
        deals = Deal.objects.get_deals_by_date(city_id=city.id, date=datetime.datetime(y,m,d), order=order)
    except:
        raise Http404
    return render_to_response(template_name, {
        'city':city,
        'deals':deals,
    }, context_instance=RequestContext(request))

def tag(request, city_abbreviation, tag_name=None, template_name="www/tag.html"):
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if city is None:
        raise Http404
    try:
        tag = Tag.objects.get(id=tag_name)
        #tag = Tag.objects.get(name=tag_name)
    except:
        raise Http404
    
    order = request.GET.get('order')
    if order == "" or order not in('current_price', '-current_price', 'volunteer', '-volunteer'):
        order = None    
    
    deals = Deal.objects.get_deals_by_tag(city_id=city.id, tag=tag, order=order)
    return render_to_response(template_name, {
        'city':city,
        'tag':tag,
        'deals':deals,
        'order' : order,
    }, context_instance=RequestContext(request))

def city(request, city_id, template_name="www/index.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

def site(request, city_abbreviation, site_name, template_name="www/index.html"):
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if city is None:
        raise Http404
    try:
        site = Site.objects.get(name=site_name)
    except:
        raise Http404
    deals = Deal.objects.get_deals_by_site(city_id=city.id, site=site)
    return render_to_response(template_name, {
        'city':city,
        'site':site,
        'deals':deals,
    }, context_instance=RequestContext(request))

def company(request, city_abbreviation, company_id, template_name="www/index.html"):
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if city is None:
        raise Http404
    try:
        company = Company.objects.get(pk=company_id)
    except:
        raise Http404
    deals = Deal.objects.get_deals_by_company(city_id=city.id, company=company)
    return render_to_response(template_name, {
        'city':city,
        'company':company,
        'deals':deals,
    }, context_instance=RequestContext(request))

def test(request, template_name="www/test.html"):
    from deal.func import deal_filter
    deals = deal_filter(request.GET.get('k'), request.GET.get('u'))
    return render_to_response(template_name, {
        'deals':deals,
    }, context_instance=RequestContext(request))

def local(request, city_abbreviation, local_name, template_name="www/local.html"):
    city = City.objects.get_city_by_abbreviation(city_abbreviation)
    if city is None:
        raise Http404
    try:
        local = Local.objects.get(name=local_name)
    except:
        raise Http404
    deals = Deal.objects.get_deals_by_local(city_id=city.id, local=local)
    return render_to_response(template_name, {
        'city':city,
        'local':local,
        'deals':deals,
    }, context_instance=RequestContext(request))

def list_city(request, template_name="www/city.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

def external_url(request, url):
    return HttpResponseRedirect(base64.b64decode(url))
    
def site_join(request,form_class=SiteJoinForm, template_name="www/site_join.html"):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return render_to_response(template_name, {
                    'form' : form,
                    'result': 1,
            }, context_instance=RequestContext(request))            
        else:
            return render_to_response(template_name, {
                    'form': form,
            }, context_instance=RequestContext(request))             
    else:
        form = form_class()
        return render_to_response(template_name, {
                'form': form,
        }, context_instance=RequestContext(request))    

def contact_us(request, form_class=ContactUsForm, template_name="www/contact_us.html"):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return render_to_response(template_name, {
                    'form' : form,
                    'result': 1,
            }, context_instance=RequestContext(request))            
        else:
            return render_to_response(template_name, {
                    'form': form,
            }, context_instance=RequestContext(request))             
    else:
        form = form_class()
        return render_to_response(template_name, {
                'form': form,
        }, context_instance=RequestContext(request))