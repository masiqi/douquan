class LazyUser(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_myuser'):
            from member.func import get_user
            request._cached_myuser = get_user(request)
        return request._cached_myuser


class AuthMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        request.__class__.myuser = LazyUser()
        return None
