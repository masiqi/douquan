import base64
from django.template import Node, Template, Context, Variable, TemplateSyntaxError
from django.template import Library
from django.conf import settings
from django.utils.encoding import smart_str

register = Library()

class URLNode(Node):
    def __init__(self, domain, view_name, args, kwargs, asvar):
        self.domain = domain 
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        from django.core.urlresolvers import reverse, NoReverseMatch
        try:
            domain = context[self.domain]
        except:
            domain = self.domain
        urlconf = settings.HOST_MIDDLEWARE_URLCONF_MAP.get(domain)
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        # Try to look up the URL twice: once given the view name, and again
        # relative to what we guess is the "main" app. If they both fail,
        # re-raise the NoReverseMatch unless we're using the
        # {% url ... as var %} construct in which cause return nothing.
        url = ''
        try:
            url = reverse(self.view_name, urlconf=urlconf, args=args, kwargs=kwargs, current_app=context.current_app)
        except NoReverseMatch, e:
            if settings.SETTINGS_MODULE:
                project_name = settings.SETTINGS_MODULE.split('.')[0]
                try:
                    url = reverse(project_name + '.' + self.view_name,
                              args=args, kwargs=kwargs, current_app=context.current_app)
                except NoReverseMatch:
                    if self.asvar is None:
                        # Re-raise the original exception, not the one with
                        # the path relative to the project. This makes a
                        # better error message.
                        raise e
            else:
                if self.asvar is None:
                    raise e

        url = "http://" + domain + url
        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url

def myurl(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                                  " (path to a view)" % bits[0])
    domain = bits[1]
    viewname = bits[2]
    args = []
    kwargs = {}
    asvar = None

    if len(bits) > 3:
        bits = iter(bits[3:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(","):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return URLNode(domain, viewname, args, kwargs, asvar)
myurl = register.tag(myurl)

@register.filter
def base64encode(value):
    try:
        url = base64.b64encode(value)
    except:
	url = value
    return url
base64encode.is_safe = True
