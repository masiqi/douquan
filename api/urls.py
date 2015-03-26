from django.conf.urls.defaults import *
from django_restapi.model_resource import Collection
from django_restapi.responder import XMLResponder
from django_restapi.receiver import FormReceiver
from django_restapi.authentication import HttpBasicAuthentication
from deal.models import Company, Deal
from deal.forms import ApiDealForm, ApiCompanyForm

deal_resource = Collection(
    queryset = Deal.objects.all(),
    permitted_methods = ('GET', 'POST'),
    #authentication = HttpBasicAuthentication(),
    receiver = FormReceiver(),
    responder = XMLResponder(paginate_by = 10),
    form_class = ApiDealForm,
)

company_resource = Collection(
    queryset = Company.objects.all(),
    permitted_methods = ('GET', 'POST'),
    #authentication = HttpBasicAuthentication(),
    receiver = FormReceiver(),
    responder = XMLResponder(paginate_by = 10),
    form_class = ApiCompanyForm,
)

urlpatterns = patterns('',
    url(r'^deal/(.*?)/?$', deal_resource),
    url(r'^company/(.*?)/?$', company_resource),
)