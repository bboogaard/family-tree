from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from api.serializers import CreateTreeSerializer


class TreeViewSet(CreateModelMixin, GenericViewSet):

    permission_classes = [IsAuthenticated]

    serializer_class = CreateTreeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
