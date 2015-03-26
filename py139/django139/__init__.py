import logging
import py139

from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from member.models import User

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

__all__ = ['Chinamobile', 'ChinamobileMiddleware', 'get_chinamobile_client', 'require_login', 'require_add']

_thread_locals = local()

class Chinamobile(py139.Chinamobile):
    def redirect(self, url):
        """
        Helper for Django which redirects to another page. If inside a
        canvas page, writes a <kx:redirect> instead to achieve the same effect.

        """
        return HttpResponse('<kx:redirect url="%s" />' % (url, ))

def get_chinamobile_client():
    """
    Get the current chinamobile object for the calling thread.

    """
    try:
        return _thread_locals.chinamobile
    except AttributeError:
        raise ImproperlyConfigured('Make sure you have the chinamobile middleware installed.')


def require_login(next=None, internal=None):
    """
    Decorator for Django views that requires the user to be logged in.
    The chinamobileMiddleware must be installed.

    Standard usage:
        @require_login()
        def some_view(request):
            ...

    Redirecting after login:
        To use the 'next' parameter to redirect to a specific page after login, a callable should
        return a path relative to the Post-add URL. 'next' can also be an integer specifying how many
        parts of request.path to strip to find the relative URL of the canvas page. If 'next' is None,
        settings.callback_path and settings.app_name are checked to redirect to the same page after logging
        in. (This is the default behavior.)
        @require_login(next=some_callable)
        def some_view(request):
            ...
    """
    def decorator(view):
        def newview(request, *args, **kwargs):
            next = newview.next
            internal = newview.internal

            try:
                kx = request.chinamobile
            except:
                raise ImproperlyConfigured('Make sure you have the chinamobile middleware installed.')

            if internal is None:
                internal = request.chinamobile.internal

            if callable(next):
                next = next(request.path)
            elif isinstance(next, int):
                next = '/'.join(request.path.split('/')[next + 1:])
            elif next is None and kx.callback_path and request.path.startswith(kx.callback_path):
                next = request.path[len(kx.callback_path):]
            elif not isinstance(next, str):
                next = ''

            if not kx.check_session(request):
                #If user has never logged in before, the get_login_url will redirect to the TOS page
#                logging.debug('user never logged in, redirect to login url')
                return kx.redirect(kx.get_login_url(next=next))

	    kx.get_uid(request)
	    if not hasattr(request, '_cached_myuser'):
	        sns_userinfo = kx.users.getInfo(kx.uid)[0]
	        user, created = User.objects.get_or_create(email=settings.CHINAMOBILE_EMAIL % kx.  uid, defaults={'email':settings.CHINAMOBILE_EMAIL % kx.uid, 'name':sns_userinfo["username"], 'password':'123qwe'})
	        if not created:
                    if user.name != sns_userinfo["username"]:
                        user.name = sns_userinfo["username"]
                        user.save()
                request._cached_myuser = user
                request.myuser = user
            else:
                request.myuser = request._cached_myuser
            return view(request, *args, **kwargs)
        newview.next = next
        newview.internal = internal
        return newview
    return decorator


def require_add(next=None, internal=None, on_install=None):
    """
    Decorator for Django views that requires application installation.
    The chinamobileMiddleware must be installed.
   
    Standard usage:
        @require_add()
        def some_view(request):
            ...

    Redirecting after installation:
        To use the 'next' parameter to redirect to a specific page after login, a callable should
        return a path relative to the Post-add URL. 'next' can also be an integer specifying how many
        parts of request.path to strip to find the relative URL of the canvas page. If 'next' is None,
        settings.callback_path and settings.app_name are checked to redirect to the same page after logging
        in. (This is the default behavior.)
        @require_add(next=some_callable)
        def some_view(request):
            ...

    Post-install processing:
        Set the on_install parameter to a callable in order to handle special post-install processing.
        The callable should take a request object as the parameter.
        @require_add(on_install=some_callable)
        def some_view(request):
            ...
    """
    def decorator(view):
        def newview(request, *args, **kwargs):
            next = newview.next
            internal = newview.internal

            try:
                kx = request.chinamobile
            except:
                raise ImproperlyConfigured('Make sure you have the chinamobile middleware installed.')

            if internal is None:
                internal = request.chinamobile.internal

            if callable(next):
                next = next(request.path)
            elif isinstance(next, int):
                next = '/'.join(request.path.split('/')[next + 1:])
            elif next is None and kx.callback_path and request.path.startswith(kx.callback_path):
                next = request.path[len(kx.callback_path):]
            else:
                next = ''

            if not kx.check_session(request):
                if kx.added:
                    if request.method == 'GET' and kx.app_name:
                        return kx.redirect('%s%s' % (kx.get_app_url(), next))
                    return kx.redirect(kx.get_login_url(next=next))
                else:
                    return kx.redirect(kx.get_add_url(next=next))

            if not kx.added:
                return kx.redirect(kx.get_add_url(next=next))

            if 'installed' in request.GET and callable(on_install):
                on_install(request)

            if internal and request.method == 'GET' and kx.app_name:
                return kx.redirect('%s%s' % (kx.get_app_url(), next))

            return view(request, *args, **kwargs)
        newview.next = next
        newview.internal = internal
        return newview
    return decorator

# try to preserve the argspecs
try:
    import decorator
except ImportError:
    pass
else:
    def updater(f):
        def updated(*args, **kwargs):
            original = f(*args, **kwargs)
            def newdecorator(view):
                return decorator.new_wrapper(original(view), view)
            return decorator.new_wrapper(newdecorator, original)
        return decorator.new_wrapper(updated, f)
    require_login = updater(require_login)
    require_add = updater(require_add)

class ChinamobileMiddleware(object):
    def __init__(self, api_key=None, secret_key=None, app_name=None, callback_path=None, internal=None):
        self.api_key = api_key or settings.CHINAMOBILE_API_KEY
        self.secret_key = secret_key or settings.CHINAMOBILE_SECRET_KEY
        self.app_name = app_name or getattr(settings, 'CHINAMOBILE_APP_NAME', None)
        self.callback_path = callback_path or getattr(settings, 'CHINAMOBILE_CALLBACK_PATH', None)
        self.internal = internal or getattr(settings, 'CHINAMOBILE_INTERNAL', True)
        self.proxy = None
        if getattr(settings, 'USE_HTTP_PROXY', False):
            self.proxy = settings.HTTP_PROXY

    def process_request(self, request):
        _thread_locals.chinamobile = request.chinamobile = Chinamobile(self.api_key, self.secret_key, app_name=self.app_name, callback_path=self.callback_path, internal=self.internal, proxy=self.proxy)
        if not self.internal and 'chinamobile_session_key' in request.session and 'chinamobile_user_id' in request.session:
            print('process_request: %s' % request.session)
            request.chinamobile.session_key = request.session['chinamobile_session_key']
            request.chinamobile.uid = request.session['chinamobile_user_id']

        """
	if not hasattr(request, '_cached_myuser'):
	    sns_userinfo = request.chinamobile.users.getInfo(request.chinamobile.uid)[0]

	    user, created = User.objects.get_or_create(email=settings.CHINAMOBILE_EMAIL % kx.  uid, defaults={'email':settings.CHINAMOBILE_EMAIL % request.chinamobile.uid, 'name':sns_userinfo["name"], 'password':'123qwe'})
	    if not created:
                if user.name != sns_userinfo["name"]:
                    user.name = sns_userinfo["name"]
                    user.save()
                    request._cached_myuser = user
                    request.myuser = user
                else:
		    request.myuser = request._cached_myuser
        """

    def process_response(self, request, response):
        if not self.internal and request.chinamobile.session_key and request.chinamobile.uid:
            request.session['chinamobile_session_key'] = request.chinamobile.session_key
            request.session['chinamobile_user_id'] = request.chinamobile.uid
        return response
