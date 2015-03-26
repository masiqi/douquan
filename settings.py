# Django settings for tuangou project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'tuangou'             # Or path to database file if using sqlite3.
DATABASE_USER = 'tuangou'             # Not used with sqlite3.
DATABASE_PASSWORD = 'tuangou'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

DATABASE_OPTIONS = {
    "init_command": "SET storage_engine=INNODB",
}

#CACHE_MIDDLEWARE_SECONDS = 86400
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Hong_Kong'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'
DEFAULT_CHARSET = 'utf-8'

SITE_ID = 2

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/siqi/work/douquan'
PROJECT_ROOT = '/home/siqi/work/douquan'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'tdn&@#%!0iv=e40l%*276=4#q)78yo12vsj+0fcoj6cibf_xu6'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'member.middleware.AuthMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'multihost.MultiHostMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'pykx.djangokx.KaixinMiddleware',
    'py139.django139.ChinamobileMiddleware',
    'pyxn.djangoxn.XiaoneiMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'douquan.urls'

HOST_MIDDLEWARE_URLCONF_MAP = {
    "douquan.com": "douquan.www.urls",
    "www.douquan.com": "douquan.www.urls",
    "passport.douquan.com": "douquan.member.urls",
    "admin.douquan.com": "douquan.admin_urls",
    "i.douquan.com": "douquan.i.urls",
    "api.douquan.com": "douquan.api.urls",
    "app.douquan.com": "douquan.app.urls",
    "img.douquan.com": "douquan.img.urls",
    "crawler.douquan.com": "douquan.crawler.urls",
}

INTERNAL_IPS = ('1.1.1.2'),

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/home/siqi/work/douquan/templates',
    '/usr/local/lib/python2.6/site-packages/django_debug_toolbar-0.8.3-py2.6.egg/debug_toolbar/templates',
)

INSTALLED_APPS = (
    'grappelli',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.sitemaps',

    'debug_toolbar',

    'tagging',
    'pagination',
    'tabs',
    
    'www',
    'member',
    'app',
    'api',
    'deal',
    'crawler',
    'i',
    
    'kaixin001',
    'chinamobile',
    'renren',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
)

PROJECT_DOMAIN = '.douquan.com'
SESSION_COOKIE_DOMAIN = '.douquan.com'
SESSION_KEY = '_auth_user'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
LOGIN_URL = 'http://passport.douquan.com/login/'
ALL_CITY_ID = 1
DEFAULT_CITY_ID = 2
DEFAULT_FEEDS = 10
DEFAULT_ENTRIES = 10
DEFAULT_GOTO = 'http://www.douquan.com'
SITE_INDEX = 'http://www.douquan.com'
I_DOUQUAN_INDEX = 'http://i.douquan.com'
MEDIA_SAVE_DIRECTORY = '/deal_pic'
MEDIA_FAKE_DIRECTORY = '/media'
SPHINX_API_VERSION = 0x113

CSRF_COOKIE_DOMAIN = '.douquan.com'

CACHE_DEFINE = {
'DEFAULT_TIMEOUT':60,
'CATEGORY_COUNT':'douquan_category_count_%d',
'CATEGORY_COUNT_TIMEOUT':600,
'CITY_ABBREVIATION':'douquan_city_abbreviation_%s',
'CITY_ABBREVIATION_TIMEOUT':86400,
}

KAIXIN_API_KEY = '413095303505fa90a1a8976dd871acac'
KAIXIN_SECRET_KEY = '592f5cebf23d1727f76ac1583aa42571'
KAIXIN_APP_NAME = "douquan"
KAIXIN_CALLBACK_PATH = "/kaixin001/"
KAIXIN_INTERNAL = False
KAIXIN_EMAIL = '%s@sns_kaixin001.com'

CHINAMOBILE_API_KEY = '7ebbde64ed81a3d481dadca6161748c8'
CHINAMOBILE_SECRET_KEY = 'af51d055dd782172438c9e595658324a'
CHINAMOBILE_APP_NAME = "douquan"
CHINAMOBILE_CALLBACK_PATH = "/chinamobile/"
CHINAMOBILE_INTERNAL = True
CHINAMOBILE_EMAIL = '%s@sns_139.com'

XIAONEI_API_KEY = '419c4a7c205a4b89ac1d10512329351b'
XIAONEI_SECRET_KEY = 'f18ef4bf60d746ceae15bb976f5e9d9d'
XIAONEI_APP_NAME = "douquan"
XIAONEI_CALLBACK_PATH = "/renren/"
XIAONEI_INTERNAL = True
XIAONEI_EMAIL = '%s@sns_renren.com'
XIAONEI_PREINSTALL_PAGE = 'http://apps.renren.com/douquan/preinstall/'
