from settings.base import *


CACHES = {
    'default': {
        'BACKEND': 'tree.tests.cache.TestCache'
    }
}

API_URL = 'http://testserver/api/v1/'
