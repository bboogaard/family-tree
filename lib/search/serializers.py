from typing import List, Optional, Tuple, Type

from django.db.models import Model
from rest_framework.serializers import ModelSerializer, SerializerMetaclass

from lib.search.search_vectors import get_search_vector_search_fields


def search_vector_model_serializer_factory(
        model: Type[Model],
        related_models: Optional[List[Tuple[str, Type[Model], bool]]] = None,
        exclude_fields: List[str] = None,
        extra_fields: List[str] = None):
    fields = list(filter(
        lambda f: f not in exclude_fields if exclude_fields else f,
        get_search_vector_search_fields(model)
    ))
    attrs = {}
    if related_models:
        for field, related_model, many in related_models:
            attrs[field] = search_vector_model_serializer_factory(
                related_model)(many=many)
            fields.append(field)
    if extra_fields:
        fields.extend(extra_fields)
    attrs.update({
        'Meta': type(
            'Meta', (SerializerMetaclass,), {'model': model, 'fields': fields}
        )
    })

    return type(
        model.__name__ + 'Serializer', (ModelSerializer,),
        attrs
    )
