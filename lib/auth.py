from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


def login_protected():
    return method_decorator(login_required(login_url='/admin/login'), name='dispatch')
