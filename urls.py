"""familytree URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from tree.views import bio, CreateTreeView, TreeView, PreviewTreeView, version

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^stamboom/$', TreeView.as_view(), name='tree'),
    re_path(r'^stamboom/about', version, name='about'),
    re_path(r'^stamboom/(?P<ancestor>[^/]+)/$', TreeView.as_view(), name='ancestor_tree'),
    re_path(r'^stamboom/(?P<ancestor>[^/]+)/persoonlijke-gegevens$', bio,
            name='ancestor_bio'),
    re_path(r'^tree/preview/(?P<ancestor>[^/]+)/(?P<descendant>[^/]+)$', PreviewTreeView.as_view(), name='preview_tree'),
    re_path(r'^tree/create/(?P<pk>[^/]+)$', CreateTreeView.as_view(), name='create_tree'),
    re_path(r'^api/v1/', include('api.urls', namespace='api')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls))
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.PRODUCTION_ENV:

    def trigger_error(request):
        division_by_zero = 1 / 0

    urlpatterns += [
        path('sentry-debug/', trigger_error),
    ]
