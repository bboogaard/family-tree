from django.conf import settings
from django.template import loader
from rest_framework.filters import SearchFilter as BaseSearchFilter
from rest_framework.settings import api_settings

from services.search.service import search_service


class SearchFilter(BaseSearchFilter):

    ordering_param = api_settings.ORDERING_PARAM

    def get_search_query(self, request):
        search_param = self.search_param
        search_query = request.query_params.get(search_param, '')
        search_query = search_query.replace('\x00', '')
        # strip null characters
        return search_query

    def get_order_by(self, request):
        ordering_param = self.ordering_param
        order_by = request.query_params.get(
            ordering_param, settings.SEARCH_ORDER_BY_AGE)
        return order_by

    def filter_queryset(self, request, queryset, view):
        search_query = self.get_search_query(request)
        if not search_query:
            return queryset

        order_by = self.get_order_by(request)
        return search_service.search(search_query, order_by)

    def to_html(self, request, queryset, view):
        search_query = self.get_search_query(request)
        order_by = self.get_order_by(request)
        context = {
            'ordering_param': self.ordering_param,
            'order_by': order_by,
            'order_by_options': settings.SEARCH_ORDER_BY,
            'request': request,
            'search_param': self.search_param,
            'search_query': search_query
        }
        template = loader.get_template(self.template)
        return template.render(context)
