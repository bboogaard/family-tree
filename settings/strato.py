from settings.base import *

ALLOWED_HOSTS = ['127.0.0.1']

# Site url
SITE_URL = 'http://py-wikkel.nl'

STATIC_URL = 'http://py-wikkel.nl/static/'

# django-debug-toolbar

# E-mail (Add user/pass...)
EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_HOST_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
