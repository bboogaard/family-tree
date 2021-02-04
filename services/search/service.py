from abc import ABC

from django.conf import settings
from django.db.models import OuterRef, Q, QuerySet, Subquery
from django.db.models.functions import Greatest
from ngram import NGram

from tree.models import Ancestor, ChristianName, NameNGram


class SearchService(ABC):

    def search(self, search_query: str,
               order_by: str = settings.SEARCH_ORDER_BY_AGE) -> QuerySet:
        choices = [key for key, val in settings.SEARCH_ORDER_BY]
        order_by = order_by if order_by in choices else \
            settings.SEARCH_ORDER_BY_AGE

        self._update(search_query)
        min_score = settings.NAME_NGRAM_MIN_SCORE
        queryset = (
            Ancestor.objects
            .select_related('christian_name')
            .filter(
                Q(
                    christian_name__ngrams__search_query__iexact=search_query,
                    christian_name__ngrams__score__gte=min_score
                ) | Q(
                    christian_name__alias_for__ngrams__search_query__iexact=(
                        search_query),
                    christian_name__alias_for__ngrams__score__gte=min_score
                )
            )
            .annotate(
                name_score=Subquery(
                    NameNGram.objects.filter(
                        christian_name=OuterRef('christian_name'),
                        search_query__iexact=search_query
                    ).values('score')[:1]
                )
            )
            .annotate(
                alias_score=Subquery(
                    NameNGram.objects.filter(
                        christian_name__alias_for=OuterRef('christian_name'),
                        search_query__iexact=search_query
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
    def _update(search_query: str):
        if NameNGram.objects.filter(search_query__iexact=search_query).count():
            return

        search_query = search_query.lower()
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


search_service = SearchService()
