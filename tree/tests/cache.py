from django.core.cache.backends.base import BaseCache, DEFAULT_TIMEOUT


class TestCache(BaseCache):

    def __init__(self, location, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entries = {}

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        key = self.make_key(key, version)
        self.validate_key(key)
        self.entries[key] = value
        return True

    def get(self, key, default=None, version=None):
        key = self.make_key(key, version)
        self.validate_key(key)
        return default

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        self.add(key, value, timeout, version)

    def touch(self, key, timeout=DEFAULT_TIMEOUT, version=None):
        self.validate_key(key)
        return False

    def delete(self, key, version=None):
        key = self.make_key(key, version)
        self.validate_key(key)
        try:
            del self.entries[key]
        except KeyError:
            pass

    def clear(self):
        self.entries = {}

    def get_entry(self, key, default=None, version=None):
        key = self.make_key(key, version)
        self.validate_key(key)
        return self.entries.get(key, default)
