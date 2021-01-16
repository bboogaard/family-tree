from functools import partial, wraps

from django.core.cache import caches
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from lib.cache.helpers import make_cache_key


def cache_result(key, timeout=DEFAULT_TIMEOUT, backend='default'):

    def decorator(func):

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            cache = caches[backend]
            return _get_func_result(key, timeout, cache, func, args, kwargs)

        return wrapped_func

    return decorator


def cache_method_result(key, timeout=DEFAULT_TIMEOUT, backend='default'):

    def decorator(func):

        @wraps(func)
        def wrapped_func(instance, *args, **kwargs):
            cache = caches[backend]
            return _get_func_result(key, timeout, cache, func, args, kwargs, instance)

        return wrapped_func

    return decorator


def _get_func_result(key, timeout, cache, func, args, kwargs, instance=None):
    cache_key = make_cache_key(key, args, kwargs)
    result = cache.get(cache_key)
    if result is None:
        f = partial(func, instance) if instance else func
        result = f(*args, **kwargs)
        cache.set(cache_key, result, timeout=timeout)
    return result
