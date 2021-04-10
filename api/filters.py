from dacite import from_dict
from dataclasses import asdict

from django.core.exceptions import ImproperlyConfigured
from django.template import loader
from django.utils.functional import cached_property
from rest_framework.filters import BaseFilterBackend
from rest_framework.settings import api_settings

from api.forms import SearchAncestorForm
from services.search.ancestors.service import SearchAncestorService
from services.search.models import EmptySearchRequest, SearchAncestorRequest, SearchNameRequest, \
    SearchTextRequest
from services.search.names.service import SearchNameService
from services.search.text.service import SearchTextService


class SearchFilter(BaseFilterBackend):

    max_results: int = 100

    ordering_param = api_settings.ORDERING_PARAM

    search_service_class = None

    template = None

    @cached_property
    def search_service(self):
        if self.search_service_class is None:
            raise ImproperlyConfigured(
                "{} expects a 'search_service_class' attribute".format(
                    self.__class__
                )
            )

        return self.search_service_class()

    def get_search_request(self, request):
        raise NotImplementedError()

    def get_order_by(self, request):
        ordering_param = self.ordering_param
        order_by = request.query_params.get(
            ordering_param, self.search_service.default_order_by)
        return order_by

    def filter_queryset(self, request, queryset, view):
        search_request = self.get_search_request(request)
        if not search_request:
            return queryset

        order_by = self.get_order_by(request)
        return self.search_service.search(search_request, order_by)[:self.max_results]

    def to_html(self, request, queryset, view):
        search_request = self.get_search_request(request)
        order_by = self.get_order_by(request)
        context = self.get_context_data(**{
            'ordering_param': self.ordering_param,
            'order_by': order_by,
            'order_by_options': self.search_service.order_by_options,
            'request': request,
            'search_request': search_request
        })
        template = loader.get_template(self.template)
        return template.render(context)

    def get_context_data(self, **kwargs):
        return kwargs


class SingleSearchFilter(SearchFilter):

    search_param = None

    search_request_class = None

    template = 'search/single.html'

    def get_search_request(self, request):
        search_query = request.query_params.get(self.search_param, '')
        search_query = search_query.replace('\x00', '')
        # strip null characters
        return from_dict(self.search_request_class, {
            self.search_param: search_query
        })

    def get_context_data(self, **kwargs):
        search_request = kwargs['search_request'] or EmptySearchRequest()
        kwargs.update({
            'search_param': self.search_param,
            'search_query': asdict(search_request).get(self.search_param, '')
        })
        return kwargs


class SearchNameFilter(SingleSearchFilter):

    search_param = 'name'

    search_request_class = SearchNameRequest

    search_service_class = SearchNameService


class SearchTextFilter(SingleSearchFilter):

    search_param = 'text'

    search_request_class = SearchTextRequest

    search_service_class = SearchTextService

    def filter_queryset(self, request, queryset, view):
        queryset = super().filter_queryset(request, queryset, view)
        queryset = (
            queryset
            .prefetch_related(
                'bio__links',
                'marriages_of_husband',
                'marriages_of_wife'
            )
        )
        return queryset


class MultiSearchFilter(SearchFilter):

    form_class = None

    search_request_class = None

    def get_search_request(self, request):
        search_values = {}
        for key, val in request.query_params.items():
            search_values[key] = val.replace('\x00', '') if val else ''
        form = self.form_class(search_values)
        if form.is_valid():
            return from_dict(self.search_request_class, form.cleaned_data)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'search_values': asdict(kwargs['search_request'])
        })
        return kwargs


class SearchAncestorFilter(MultiSearchFilter):

    form_class = SearchAncestorForm

    search_request_class = SearchAncestorRequest

    search_service_class = SearchAncestorService

    template = 'search/ancestor.html'
