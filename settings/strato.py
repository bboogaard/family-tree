from settings.base import *

ALLOWED_HOSTS = ['127.0.0.1']

# Site url
SITE_URL = 'https://py-wikkel.nl'

STATIC_URL = 'https://py-wikkel.nl/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

# django-debug-toolbar

# E-mail (Add user/pass...)
EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_HOST_PORT = 587
