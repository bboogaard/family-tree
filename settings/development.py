from settings.base import *

DEBUG = True

INSTALLED_APPS += ['debug_toolbar']

INTERNAL_IPS = ['127.0.0.1']

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
