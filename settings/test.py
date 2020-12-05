from settings.base import *


CACHES = {
    'default': {
        'BACKEND': 'tree.tests.cache.TestCache'
    }
}
