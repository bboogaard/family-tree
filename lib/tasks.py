import background

from django.conf import settings


def task(func):
    return background.task(func) if settings.ASYNC_TASKS else func
