from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import Exists, F, FloatField, Q, QuerySet, Subquery
from django.db.models.functions import Greatest

from lib.search.search_vectors import get_search_vector_related_querysets
from services.search.base import SearchService
from services.search.models import SearchTextRequest
from tree.models import Ancestor


class SearchTextService(SearchService):

    default_order_by = settings.SEARCH_ORDER_BY_AGE

    order_by_options = settings.SEARCH_TEXT_ORDER_BY

    def get_queryset(self, search_request: SearchTextRequest, order_by: str) -> QuerySet:
        query = SearchQuery(search_request.text)
        related_querysets = get_search_vector_related_querysets(query)
        query_clause = Q(search_vector=query)
        rank_clause = {'rank_1': SearchRank(F('search_vector'), query)}
        for num, queryset in enumerate(related_querysets):
            query_clause |= Q(Exists(queryset))
            rank_clause['rank_{}'.format(num + 2)] = Subquery(
                queryset.values('rank')[:1],
                output_field=FloatField()
            )
        queryset = (
            Ancestor.objects
            .select_related('christian_name')
            .filter(query_clause)
            .annotate(**rank_clause)
            .annotate(rank=Greatest(*rank_clause.keys()))
            .with_age()
            .order_by(order_by)
        )
        return queryset
