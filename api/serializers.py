from django.urls import reverse
from rest_framework import serializers

from tree.models import Ancestor


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
