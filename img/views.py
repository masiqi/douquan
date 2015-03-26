#-*-coding:utf8;-*-
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse

def show(request, template_name="kaixin001/test.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
