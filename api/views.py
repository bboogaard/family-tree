from rest_framework.generics import GenericAPIView
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response

from api.filters import SearchFilter
from api.serializers import AncestorSerializer
from tree.models import Ancestor


class SearchNamesView(GenericAPIView):

    filter_backends = [SearchFilter]

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
