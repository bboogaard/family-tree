import itertools

from django.conf import settings
from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from api.exceptions import InvalidCommand
from api.tasks import scrape_page
from lib.search.search_vectors import get_search_vector_search_fields
from lib.search.serializers import search_vector_model_serializer_factory
from scraper.models import Page
from services.tree.service import TreeService
from tree.models import Ancestor, Bio, BioLink, ChristianName, Marriage


class AncestorSerializer(serializers.ModelSerializer):

    ancestor = serializers.SerializerMethodField()

    url = serializers.SerializerMethodField()

    class Meta:
        model = Ancestor
        fields = ['ancestor', 'url']

    @property
    def request(self):
        return self.context['request']

    def get_ancestor(self, obj):
        return str(obj)

    def get_url(self, obj):
        scheme = 'https' if self.request.is_secure() else 'http'
        return scheme + '://' + self.request.get_host() + reverse(
            'ancestor_bio', kwargs={
                'ancestor': obj.slug
            }
        )


class AncestorSearchTextSerializer(AncestorSerializer):

    christian_name = search_vector_model_serializer_factory(ChristianName)()

    bio = search_vector_model_serializer_factory(
        Bio, [('links', BioLink, True)], ['details'], ['rendered_details'])()

    marriages = search_vector_model_serializer_factory(Marriage)(many=True)

    class Meta(AncestorSerializer.Meta):
        fields = list(itertools.chain.from_iterable([
            AncestorSerializer.Meta.fields,
            ['christian_name'],
            get_search_vector_search_fields(Ancestor),
            ['bio', 'marriages']
        ]))


class AncestorSearchAncestorSerializer(AncestorSerializer):

    create_tree_url = serializers.SerializerMethodField()

    class Meta(AncestorSerializer.Meta):
        fields = AncestorSerializer.Meta.fields + ['create_tree_url']

    def get_create_tree_url(self, obj):
        scheme = 'https' if self.request.is_secure() else 'http'
        return scheme + '://' + self.request.get_host() + reverse(
            'create_tree', kwargs={
                'pk': obj.pk
            }
        )


class CreateTreeSerializer(serializers.Serializer):

    ancestor_id = serializers.IntegerField(write_only=True)

    descendant_id = serializers.IntegerField(write_only=True)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        try:
            data['ancestor'] = Ancestor.objects.get(pk=data['ancestor_id'])
        except Ancestor.DoesNotExist:
            raise NotFound()

        try:
            data['descendant'] = Ancestor.objects.get(pk=data['descendant_id'])
        except Ancestor.DoesNotExist:
            raise NotFound()

        return data

    def create(self, validated_data):
        ancestor = validated_data['ancestor']
        descendant = validated_data['descendant']
        return TreeService().create(ancestor, descendant)


class ScrapePageSerializer(serializers.Serializer):

    page_id = serializers.IntegerField(write_only=True)

    depth = serializers.IntegerField(default=2, write_only=True)

    direction = serializers.ChoiceField(
        choices=settings.SCRAPE_DIRECTIONS,
        default=settings.SCRAPE_DIRECTION_DOWN,
        write_only=True
    )

    def create(self, validated_data):
        page_id = validated_data['page_id']
        depth = validated_data['depth']
        direction = validated_data['direction']
        scrape_page(page_id, depth, direction)
        return True


def task_serializer_factory(command):
    if command == 'scrape_page':
        return ScrapePageSerializer

    raise InvalidCommand()


class PageSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ['id', 'name']

    def get_name(self, obj):
        if ancestor := obj.ancestor:
            return str(ancestor)

        return obj.name
