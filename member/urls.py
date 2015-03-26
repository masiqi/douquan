from django.conf.urls.defaults import *

urlpatterns = patterns('member.views',
    url(r'^$', 'login', name='passport_index'),
    url(r'^register/$', 'register', name='passport_register'),
    url(r'^login/$', 'login', name='passport_login'),
    url(r'^logout/$', 'logout', name='passport_logout'),
    url(r'^active/$', 'active', name='passport_active'),
    url(r'^forget/$', 'forget', name='passport_forget'),
    url(r'^profile/$', 'profile', name='passport_profile'),
)
