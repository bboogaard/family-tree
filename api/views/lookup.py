from django_filters.rest_framework.backends import DjangoFilterBackend
from django.db.models import Model
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from api.filters import search_filterset_factory
from api.serializers import PageSerializer
from scraper.models import Page


class LookupViewSet(ListModelMixin, GenericViewSet):

    filter_backends = [DjangoFilterBackend]

    @action(methods=['get'], detail=False, url_path='page')
    def page(self,request, *args, **kwargs):
        self.filterset_class = search_filterset_factory(Page, ['name'], max_results=10)
        self.serializer_class = PageSerializer
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        if self.action == 'page':
            return Page.objects.all()

        raise NotImplementedError()
