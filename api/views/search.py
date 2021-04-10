from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.viewsets import GenericViewSet

from api.filters import SearchAncestorFilter, SearchNameFilter, SearchTextFilter
from api.renderers import HighlightBrowsableAPIRenderer, HighlightJsonRenderer
from api.serializers import AncestorSerializer, AncestorSearchAncestorSerializer, AncestorSearchTextSerializer
from tree.models import Ancestor


class SearchViewSet(ListModelMixin, GenericViewSet):

    queryset = Ancestor.objects.none()

    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    serializer_class = AncestorSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_renderer_context(self):
        context = super().get_renderer_context()
        if self.action == 'text':
            search_request = self.filter_backends[0]().get_search_request(
                self.request
            )
            context['search_query'] = search_request.text
        return context

    @action(methods=['get'], detail=False)
    def names(self, request, *args, **kwargs):
        self.filter_backends = [SearchNameFilter]
        return self.list(request, *args, **kwargs)

    @action(methods=['get'], detail=False, renderer_classes=[HighlightBrowsableAPIRenderer, HighlightJsonRenderer])
    def text(self, request, *args, **kwargs):
        self.serializer_class = AncestorSearchTextSerializer
        self.filter_backends = [SearchTextFilter]
        return self.list(request, *args, **kwargs)

    @action(methods=['get'], detail=False)
    def ancestors(self, request, *args, **kwargs):
        self.serializer_class = AncestorSearchAncestorSerializer
        self.filter_backends = [SearchAncestorFilter]
        return self.list(request, *args, **kwargs)
