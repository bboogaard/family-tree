import itertools

from django.urls import reverse
from rest_framework import serializers

from lib.search.search_vectors import get_search_vector_search_fields
from lib.search.serializers import search_vector_model_serializer_factory
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
