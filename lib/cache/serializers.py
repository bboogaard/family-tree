from django.db.models import Model


class CacheKeySerializer(object):

    @staticmethod
    def serialize(value):
        return str(value)


class ModelCacheKeySerializer(CacheKeySerializer):

    @staticmethod
    def serialize(value):
        return CacheKeySerializer.serialize(value.pk)


class ListCacheKeySerializer(CacheKeySerializer):

    @staticmethod
    def serialize(value):
        value = list(value)
        result = []
        for val in value:
            result.append(
                CacheKeySerializerFactory.find_serializer(val).serialize(val)
            )
        return ':'.join(result)


class CacheKeySerializerFactory(object):

    @staticmethod
    def find_serializer(value):
        if isinstance(value, Model):
            return ModelCacheKeySerializer
        elif isinstance(value, (tuple, list)):
            return ListCacheKeySerializer
        else:
            return CacheKeySerializer
