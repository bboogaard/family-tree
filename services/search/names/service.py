from django.conf import settings
from django.db.models import Exists, OuterRef, Q, QuerySet, Subquery
from django.db.models.functions import Greatest
from ngram import NGram

from services.search.base import SearchService
from services.search.models import SearchNameRequest
from tree.models import Ancestor, ChristianName, NameNGram


class SearchNameService(SearchService):

    default_order_by = settings.SEARCH_ORDER_BY_AGE

    order_by_options = settings.SEARCH_NAME_ORDER_BY

    def get_queryset(self, search_request: SearchNameRequest, order_by: str) -> QuerySet:
        self._update(search_request)
        min_score = settings.NAME_NGRAM_MIN_SCORE
        queryset = (
            Ancestor.objects
            .select_related('christian_name')
            .filter(Exists(
                ChristianName.objects.filter(
                    Q(
                        pk=OuterRef('christian_name')
                    ) | Q(
                        alias_for=OuterRef('christian_name')
                    ) | Q(
                        aliases=OuterRef('christian_name')
                    ),
                    ngrams__search_query__iexact=search_request.name,
                    ngrams__score__gte=min_score
                )
            ))
            .annotate(
                name_score=Subquery(
                    NameNGram.objects.filter(
                        christian_name=OuterRef('christian_name'),
                        search_query__iexact=search_request.name
                    ).values('score')[:1]
                )
            )
            .annotate(
                alias_score=Subquery(
                    NameNGram.objects.filter(
                        christian_name__alias_for=OuterRef('christian_name'),
                        search_query__iexact=search_request.name
                    ).values('score')[:1]
                )
            )
            .annotate(
                score=Greatest('name_score', 'alias_score')
            )
            .with_age()
            .order_by(order_by)
        )
        return queryset

    @staticmethod
    def _update(search_request: SearchNameRequest):
        if NameNGram.objects.filter(search_query__iexact=search_request.name).count():
            return

        search_query = search_request.name.lower()
        name_ngrams = []
        for name in ChristianName.objects.all():
            if name.female_name:
                score_female = NGram.compare(
                    search_query, name.female_name.lower(), N=3)
            else:
                score_female = 0
            if name.male_name:
                score_male = NGram.compare(
                    search_query, name.male_name.lower(), N=3)
            else:
                score_male = 0
            score = int(max(score_female, score_male) * 100)
            name_ngrams.append(NameNGram(
                search_query=search_query,
                score=score,
                christian_name=name
            ))
        NameNGram.objects.bulk_create(name_ngrams)
