from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from crawler.func import CrawlerTask, CrawlerStorage

def index(request, template_name="www/test.html"):
    ct = CrawlerTask(2, True)
    ct.run()
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

def read_storage(request, storage_id, template_name="www/test.html"):
    cs = CrawlerStorage(storage_id)
    return render_to_response(template_name, {
        'content':cs.storage2string()
    }, context_instance=RequestContext(request))
