from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from member.models import User
from member.func import get_user

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

def require_login(next=None, internal=None):
    def decorator(view):
        def newview(request, *args, **kwargs):
            next = newview.next
            internal = newview.internal

            if get_user(request) is None:
                return HttpResponseRedirect(settings.LOGIN_URL+'?goto='+request.current_url)
            return view(request, *args, **kwargs)
        newview.next = next
        newview.internal = internal
        return newview
    return decorator
