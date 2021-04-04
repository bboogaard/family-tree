from django.conf import settings
from django.db.models import Case, CharField, IntegerField, F, Q, QuerySet, Value, When
from django.db.models.functions import Concat, Extract

from services.search.base import SearchService
from services.search.models import SearchAncestorRequest
from tree.models import Ancestor


class SearchAncestorService(SearchService):

    default_order_by = settings.SEARCH_ORDER_BY_AGE

    order_by_options = settings.SEARCH_ANCESTOR_ORDER_BY

    def get_queryset(self, search_request: SearchAncestorRequest, order_by: str) -> QuerySet:
        queryset = (
            Ancestor.objects
            .with_has_children()
            .with_age()
            .order_by(order_by)
        )
        if search_request.has_children is not None:
            queryset = queryset.filter(has_children=search_request.has_children)
        if search_request.lastname:
            queryset = (
                queryset.annotate(
                    lastname_with_middlename=Concat(
                        'middlename', Value(' '), 'lastname',
                        output_field=CharField()
                    )
                )
                .filter(
                    Q(lastname__icontains=search_request.lastname) | Q(
                        lastname_with_middlename__icontains=search_request.lastname
                    )
                )
            )
        if search_request.birthyear_from or search_request.birthyear_to:
            queryset = queryset.annotate(
                birthyear_default=Case(
                    When(birthyear__isnull=False, then=F('birthyear')),
                    When(birthdate__isnull=False, then=Extract('birthdate', 'year')),
                    output_field=IntegerField(),
                    default=None
                )
            )
            if search_request.birthyear_from:
                queryset = queryset.filter(
                    birthyear_default__gte=search_request.birthyear_from
                )
            if search_request.birthyear_to:
                queryset = queryset.filter(
                    birthyear_default__lt=search_request.birthyear_to
                )
        return queryset
