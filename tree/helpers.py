"""
Helpers for the tree app.

"""
from django.core.exceptions import ObjectDoesNotExist


class LineageBuilder(object):

    def __init__(self):
        self._descendant = None
        self._generations = []
        self._cache = {}

    def build(self, lineage):
        self._generations = []
        self._get_generations(lineage.ancestor, lineage.descendant, 1)
        return self._generations

    def _get_generations(self, ancestor, descendant, generation):
        children = self._get_children(ancestor)
        if not children:
            return

        if descendant not in children:
            for child in children:
                if self._is_ancestor(child, descendant):
                    self._generations.append((child, generation))
                    self._get_generations(child, descendant, generation + 1)
                    break

    def _is_ancestor(self, candidate, descendant):
        self._descendant = None
        self._get_descendant(candidate, descendant)
        return self._descendant is not None

    def _get_descendant(self, candidate, descendant):
        children = self._get_children(candidate)
        if not children:
            return

        if descendant not in children:
            for child in children:
                self._get_descendant(child, descendant)
        else:
            self._descendant = descendant

    def _get_children(self, ancestor):
        children = self._cache.get(ancestor.pk)
        if not children:
            children = list(ancestor.children.order_by_age())
            self._cache[ancestor.pk] = children

        return children


def build_lineage(lineage):
    return LineageBuilder().build(lineage)


def get_parent(descendant, visible_ancestors):
    try:
        parent = descendant.father
    except ObjectDoesNotExist:
        return

    if parent in visible_ancestors:
        return

    return parent
