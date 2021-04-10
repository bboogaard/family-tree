import operator
from abc import ABC
from typing import List, Tuple

from api.exceptions import Conflict
from tree.models import Ancestor, Lineage


class TreeService(ABC):

    _ancestors: List[Tuple[Ancestor, int]]

    @staticmethod
    def create(ancestor: Ancestor, descendant: Ancestor) -> Ancestor:
        if ancestor.get_lineage():
            raise Conflict()

        Lineage.objects.create(
            ancestor=ancestor,
            descendant=descendant
        )
        return ancestor

    def find(self, descendant: Ancestor) -> List[Ancestor]:
        self._ancestors = []
        self._find_ancestors(descendant)
        return list(
            map(
                lambda a: a[0],
                sorted(self._ancestors, key=operator.itemgetter(1), reverse=True)
            )
        )

    def _find_ancestors(self, descendant: Ancestor, generation: int = 0):
        candidates = list(filter(
            lambda a: a and a.was_married, [descendant.father, descendant.mother]
        ))
        if not candidates and generation:
            self._ancestors.append((descendant, generation))

        for candidate in candidates:
            self._find_ancestors(candidate, generation + 1)
