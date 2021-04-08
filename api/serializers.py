import itertools

from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from lib.search.search_vectors import get_search_vector_search_fields
from lib.search.serializers import search_vector_model_serializer_factory
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
            'api:trees-create-tree', args=[obj.pk]
        )


class ListTreeSerializer(serializers.ModelSerializer):

    ancestor = serializers.SerializerMethodField()

    url = serializers.SerializerMethodField()

    has_lineage = serializers.SerializerMethodField()

    class Meta:
        model = Ancestor
        fields = ['id', 'ancestor', 'url', 'has_lineage']

    @property
    def request(self):
        return self.context['request']

    def get_ancestor(self, obj):
        return str(obj)

    def get_url(self, obj):
        if not obj.get_lineage():
            return ''

        scheme = 'https' if self.request.is_secure() else 'http'
        return scheme + '://' + self.request.get_host() + reverse(
            'ancestor_tree', kwargs={
                'ancestor': obj.slug
            }
        )

    def get_has_lineage(self, obj):
        return obj.get_lineage() is not None


class CreateTreeSerializer(serializers.Serializer):

    ancestor_id = serializers.IntegerField()

    descendant_id = serializers.IntegerField()

    @property
    def request(self):
        return self.context['request']

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
