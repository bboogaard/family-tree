from settings.base import *

ALLOWED_HOSTS = ['127.0.0.1']

# Site url
SITE_URL = 'https://py-wikkel.nl'

STATIC_URL = 'https://py-wikkel.nl/static/'

STATIC_ROOT = '/home/bboogaard/media/py-wikkel/staticfiles'

# django-debug-toolbar

# E-mail (Add user/pass...)
EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_HOST_PORT = 587

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://bdf806f0125c4e1db409a1fc40f6058d@o480290.ingest.sentry.io/5527044",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

PRODUCTION_ENV = True

