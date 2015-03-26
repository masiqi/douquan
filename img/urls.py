from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r"^media/(?P<path>.*)$", "my_media_serve.serve", {"document_root": settings.MEDIA_ROOT, "compress": True}),
    #(r"^media/(?P<path>.*)$", "dynamic_media_serve.serve", {"document_root": settings.MEDIA_ROOT, "compress": True}),
)
