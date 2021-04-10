import operator
from abc import ABC
from typing import List

from django.db.models import QuerySet
from django.utils.functional import cached_property

from .models import Lineage
from tree.models import Ancestor, Lineage as LineageModel


class LineageService(ABC):

    @cached_property
    def lineages(self) -> List[Lineage]:
        lineages = []
        queryset = self.get_queryset()
        for lineage in queryset.all():
            lineages.append(Lineage.from_lineage(lineage))
        return lineages

    def get_queryset(self) -> QuerySet:
        return (
            LineageModel.objects
            .select_related(
                'ancestor',
                'descendant'
            )
            .prefetch_related(
                'generations'
            )
        )

    def find_root(self, ancestor: Ancestor) -> Ancestor:
        candidates = [ancestor] + [
            ancestor.get_spouse(marriage)
            for marriage in ancestor.marriages.all()
        ] + list(filter(None, [ancestor.father, ancestor.mother]))
        for candidate in candidates:
            if lineage := self._find_lineage(candidate):
                return lineage.generations[0]

    def has_lineage(self, ancestor: Ancestor) -> bool:
        return bool(
            next(
                filter(
                    lambda a: a == ancestor,
                    map(lambda l: l[0], self.lineages)
                ),
                None
            )
        )

    def _find_lineage(self, ancestor: Ancestor) -> Lineage:
        lineages = []
        for lineage in self.lineages:
            if ancestor in lineage.generations:
                lineages.append((lineage, lineage.generations.index(ancestor)))
        lineages = list(sorted(lineages, key=operator.itemgetter(1)))
        return lineages[0][0] if lineages else None
