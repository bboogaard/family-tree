from abc import ABC

from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet


class SearchService(ABC):

    default_order_by = None

    order_by_options = None

    def search(self, search_query: str, order_by: str = '') -> QuerySet:
        if self.default_order_by is None:
            raise ImproperlyConfigured("{} expects a 'default_order_by' attribute".format(
                self.__class__
            ))
        if self.order_by_options is None:
            raise ImproperlyConfigured("{} expects a 'order_by_options' attribute".format(
                self.__class__
            ))

        choices = [key for key, val in self.order_by_options]
        order_by = order_by if order_by in choices else self.default_order_by

        queryset = self.get_queryset(search_query, order_by)
        return queryset

    def get_queryset(self, search_query: str, order_by: str = '') -> QuerySet:
        raise NotImplementedError()
