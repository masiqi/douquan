#-*-coding:utf8;-*-
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import admin

from deal.models import Deal, Category
from deal.forms import AdminAddCateForm, AdminAddTagForm
import admin_urls

def add_category(request, form_class=AdminAddCateForm, template_name="admin/add_category.html"):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            ids = form.cleaned_data.get('ids')
            category = form.cleaned_data.get('category')
            id_list = ids.split(',')
            for id in id_list:
                deal = Deal.objects.get(pk=id)
                deal.category = category
                deal.save()
            return HttpResponseRedirect(reverse('admin:index', urlconf=admin_urls) + "deal/deal")
        else:
            ids = request.POST['ids']
            condition = 'id IN (' + ids + ')'
            deals = Deal.objects.extra(where=[condition])           
            return render_to_response(template_name, {
                'deals' : deals,                
                'form' : form,
            }, context_instance=RequestContext(request))            
    else:
        ids = request.GET['ids']
        condition = 'id IN (' + ids + ')'
        deals = Deal.objects.extra(where=[condition])
        form = form_class(initial={'ids': ids})
        return render_to_response(template_name, {
            'deals' : deals,                                      
            'form' : form,
        }, context_instance=RequestContext(request))
    
def add_tag(request, form_class=AdminAddTagForm, template_name="admin/add_tag.html"):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            ids = form.cleaned_data.get('ids')
            tag = form.cleaned_data.get('tag')
            id_list = ids.split(',')
            for id in id_list:
                deal = Deal.objects.get(pk=id)
                deal.tags = tag
                deal.save()
            return HttpResponseRedirect(reverse('admin:index', urlconf=admin_urls) + "deal/deal")        
    else:
        ids = request.GET['ids']
        condition = 'id IN (' + ids + ')'
        deals = Deal.objects.extra(where=[condition])
        form = form_class(initial={'ids': ids})
    return render_to_response(template_name, {
        'form' :  form,
        'deals' : deals,
    }, context_instance=RequestContext(request))    