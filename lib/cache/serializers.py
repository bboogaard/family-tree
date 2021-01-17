from django.db.models import Model


class CacheKeySerializer(object):

    @staticmethod
    def serialize(value):
        return str(value)


class ModelCacheKeySerializer(CacheKeySerializer):

    @staticmethod
    def serialize(value):
        return CacheKeySerializer.serialize(value.pk)


class CacheKeySerializerFactory(object):

    @staticmethod
    def find_serializer(value):
        if isinstance(value, Model):
            return ModelCacheKeySerializer
        else:
            return CacheKeySerializer
