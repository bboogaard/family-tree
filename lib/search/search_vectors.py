from functools import partial
from typing import List, Type

from django.contrib.postgres.search import SearchQuery, SearchRank, \
    SearchVector, SearchVectorField
from django.db.models import F, Model, OuterRef, QuerySet
from django.db.models.signals import post_save


class SearchVectorHandler:

    def __init__(self, model: Type[Model], search_fields: List[str],
                 foreign_keys: List[str] = None):
        self.model = model
        self.search_fields = search_fields
        self.foreign_keys = foreign_keys
        post_save.connect(
            partial(self.update_search_vector, handler=self),
            sender=model,
            weak=False
        )

    @staticmethod
    def update_search_vector(sender, **kwargs):
        created = kwargs.get('created')
        if created:
            return

        instance = kwargs.get('instance')
        handler = kwargs.get('handler')
        handler.model.objects.filter(pk=instance.pk).update(
            search_vector=SearchVector(*handler.search_fields))

    def update_all(self):
        for instance in self.model.objects.all():
            instance.search_vector = SearchVector(*self.search_fields)
            instance.save()


class SearchVectorRegistry:

    def __init__(self):
        self.handlers = {}

    def register(self, model: Type[Model], search_fields: List[str],
                 foreign_keys: List[str] = None):
        self.handlers[model] = SearchVectorHandler(
            model, search_fields, foreign_keys)

    def update(self):
        for model, handler in self.handlers.items():
            print("Updating search vector field for {}".format(
                model._meta.verbose_name))
            handler.update_all()

    def get_related_querysets(self, search_query: SearchQuery) -> \
            List[QuerySet]:
        querysets = []
        for model, handler in self.handlers.items():
            if not handler.foreign_keys:
                continue

            for foreign_key in handler.foreign_keys:
                querysets.append(
                    model.objects
                    .filter(**{
                        foreign_key: OuterRef('id')
                    })
                    .filter(
                        search_vector=search_query
                    )
                    .annotate(
                        rank=SearchRank(F('search_vector'), search_query))
                )
        return querysets


search_vector_registry = SearchVectorRegistry()


def register_search_vector(model: Type[Model], search_fields: List[str],
                           foreign_keys: List[str] = None):
    field = model._meta.get_field('search_vector')
    if not field or not isinstance(field, SearchVectorField):
        raise ValueError("{} has no search vector field named 'search_vector'")

    search_vector_registry.register(model, search_fields, foreign_keys)


def get_search_vector_related_querysets(search_query: SearchQuery) -> \
        List[QuerySet]:
    return search_vector_registry.get_related_querysets(search_query)
