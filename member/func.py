from django.conf import settings
from django.http import HttpResponseRedirect
from member.models import User, Score, ScoreLog

def login(request, user):
    if user is None:
        user = request.myuser
        
    if settings.SESSION_KEY in request.session:
        if request.session[settings.SESSION_KEY] != user.id:
            try:
                del request.session[settings.SESSION_KEY]
            except KeyError:
                pass
    else:
        request.session.cycle_key()
    request.session[settings.SESSION_KEY] = user.id
    if hasattr(request, 'myuser'):
        request.myuser = user
    if request.POST.get('remember') is None:
        request.session.set_expiry(0)
    else:
        request.session.set_expiry(60 * 60 * 24 * 7 * 365)

def logout(request):
    try:
        del request.session[settings.SESSION_KEY]
    except KeyError:
        pass
    if hasattr(request, 'myuser'):
        request.myuser = None
        
def require_login(next=None, internal=None):
    def decorator(view):
        def newview(request, *args, **kwargs):
            next = newview.next
            internal = newview.internal

            try:
                user = request.myuser
            except:
                raise ImproperlyConfigured('Make sure you have the Auth middleware installed.')
            if user is None:
                return HttpResponseRedirect(settings.LOGIN_URL % request.current_url)
            return view(request, *args, **kwargs)
        newview.next = next
        newview.internal = internal
        return newview
    return decorator

def get_user(request):
    try:
        user_id = request.session[settings.SESSION_KEY]
        user = User.objects.get(pk=user_id)
    except KeyError:
        user = None
    return user

def profile(request, form):
    try:
        user_id = request.session[settings.SESSION_KEY]
        user = User.objects.get(pk=user_id)
    except KeyError:
        user = None
    try:
        user.name = form.cleaned_data['name']
        user.password = form.cleaned_data['password']
        user.save()
    except:
        pass        
    return user

def is_login(request):
    if get_user(request) is None:
        return False
    else:
        return True