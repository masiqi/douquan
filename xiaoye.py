from settings import *
import sys
from os.path import abspath, dirname, join

MEDIA_ROOT = '/home/xiaoye/workspace/douquan/site_media'
ADMIN_MEDIA_ROOT = '/home/xiaoye/workspace/douquan/admin_media/'
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/home/xiaoye/workspace/douquan/templates',
)
DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'douquan'             # Or path to database file if using sqlite3.
DATABASE_USER = 'douquan'             # Not used with sqlite3.
DATABASE_PASSWORD = 'douquan'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''
PROJECT_ROOT = '/home/xiaoye/workspace/douquan'
sys.path.insert(0, join(PROJECT_ROOT, "libs/"))

#DEBUG = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG
#TEMPLATE_DEBUG = False
