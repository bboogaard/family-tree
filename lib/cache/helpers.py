import operator

from lib.cache.serializers import CacheKeySerializerFactory


def make_cache_key(key, args=None, kwargs=None):
    serialized = [key]
    if args:
        serialized.extend([_serialize(arg) for arg in args])
    if kwargs:
        serialized.extend(['{}={}'.format(key, _serialize(val)) for key, val in sorted(kwargs.items(), key=operator.itemgetter(0))])
    return ':'.join(serialized)


def _serialize(value):
    return CacheKeySerializerFactory.find_serializer(value).serialize(value)
