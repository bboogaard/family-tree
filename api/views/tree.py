from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import GenericViewSet

from api.serializers import CreateTreeSerializer, ListTreeSerializer
from lib.views import HTMLMixin, ValidateMixin
from services.tree.service import TreeService
from tree.models import Ancestor


class TreeViewSet(HTMLMixin, ValidateMixin, GenericViewSet):

    descendant = None

    permission_classes = [IsAuthenticated]

    renderer_classes = [TemplateHTMLRenderer]

    serializer_class = ListTreeSerializer

    template_name = 'tree/descendant.html'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(methods=['get', 'post'], detail=True, url_path='create')
    def create_tree(self, request, pk, *args, **kwargs):
        self.descendant = get_object_or_404(Ancestor, pk=pk)
        if request.data:
            self.serializer_class = CreateTreeSerializer
            if not (error_response := self.process_serializer(request.data)):
                return redirect(
                    reverse('api:trees-create-tree', args=[self.descendant.pk])
                )

            return error_response

        ancestors = TreeService().find(self.descendant)
        return self.render_descendant(ancestors)

    def render_descendant(self, ancestors, status=HTTP_200_OK, errors=None):
        return self.render_response(
            ancestors, ListTreeSerializer, many=True, extra_context={
                'name': 'Ancestors of {}'.format(self.descendant),
                'descendant': self.descendant,
                'breadcrumblist': [
                    ('Ancestors of {}'.format(self.descendant), self.request.path)
                ],
                'errors': errors
            },
            status=status
        )

    def handle_errors(self, errors):
        ancestors = TreeService().find(self.descendant)
        return self.render_descendant(
            ancestors, status=HTTP_400_BAD_REQUEST, errors=errors
        )
