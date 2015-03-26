from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^tuangou/', include('tuangou.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # aUncomment the next line to enable the admin:
    #(r'^admin/', include(admin.site.urls)),
    #(r'^api/', include('api.urls')),
    #(r'^app/', include('app.urls')),
    #(r'^passport/', include('passport.urls')),
    #(r'^', include('www.urls')),
)
