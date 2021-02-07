from django.core.exceptions import ImproperlyConfigured
from django.template import loader
from django.utils.functional import cached_property
from rest_framework.filters import SearchFilter as BaseSearchFilter
from rest_framework.settings import api_settings

from services.search.names.service import SearchNameService


class SearchFilter(BaseSearchFilter):

    ordering_param = api_settings.ORDERING_PARAM

    search_service_class = None

    @cached_property
    def search_service(self):
        if self.search_service_class is None:
            raise ImproperlyConfigured("{} expects a 'search_service_class' attribute".format(
                self.__class__
            ))

        return self.search_service_class()

    def get_search_query(self, request):
        search_param = self.search_param
        search_query = request.query_params.get(search_param, '')
        search_query = search_query.replace('\x00', '')
        # strip null characters
        return search_query

    def get_order_by(self, request):
        ordering_param = self.ordering_param
        order_by = request.query_params.get(
            ordering_param, self.search_service.default_order_by)
        return order_by

    def filter_queryset(self, request, queryset, view):
        search_query = self.get_search_query(request)
        if not search_query:
            return queryset

        order_by = self.get_order_by(request)
        return self.search_service.search(search_query, order_by)

    def to_html(self, request, queryset, view):
        search_query = self.get_search_query(request)
        order_by = self.get_order_by(request)
        context = {
            'ordering_param': self.ordering_param,
            'order_by': order_by,
            'order_by_options': self.search_service.order_by_options,
            'request': request,
            'search_param': self.search_param,
            'search_query': search_query
        }
        template = loader.get_template(self.template)
        return template.render(context)


class SearchNameFilter(SearchFilter):

    search_service_class = SearchNameService
