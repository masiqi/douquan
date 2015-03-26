from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^kaixin001/', include('kaixin001.urls')),
    (r'^chinamobile/', include('chinamobile.urls')),
    (r'^renren/', include('renren.urls')),
)
