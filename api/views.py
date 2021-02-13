from rest_framework.generics import GenericAPIView
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response

from api.filters import SearchNameFilter, SearchTextFilter
from api.renderers import HighlightBrowsableAPIRenderer, HighlightJsonRenderer
from api.serializers import AncestorSerializer, AncestorSearchTextSerializer
from tree.models import Ancestor


class SearchView(GenericAPIView):

    queryset = Ancestor.objects.none()

    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    serializer_class = AncestorSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class SearchNamesView(SearchView):

    filter_backends = [SearchNameFilter]


class SearchTextView(SearchView):

    filter_backends = [SearchTextFilter]

    renderer_classes = [HighlightBrowsableAPIRenderer, HighlightJsonRenderer]

    serializer_class = AncestorSearchTextSerializer

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['search_query'] = self.filter_backends[0]().get_search_query(
            self.request
        )
        return context
