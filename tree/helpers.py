"""
Helpers for the tree app.

"""
from tree.models import Ancestor


class LineageFinder(object):

    def __init__(self):
        self._descendant = None

    def find(self, ancestor, descendant):
        result = []
        for candidate in Ancestor.objects.with_children().all():
            if self._is_ancestor(candidate, descendant):
                result.append(candidate)
        return result

    def _is_ancestor(self, candidate, descendant):
        self._descendant = None
        self._get_descendant(candidate, descendant)
        return self._descendant is not None

    def _get_descendant(self, candidate, descendant):
        children = list(candidate.children.all())
        if not children:
            return

        if descendant not in children:
            for child in children:
                self._get_descendant(child, descendant)
        else:
            self._descendant = descendant


def get_lineage(ancestor, descendant):
    return LineageFinder().find(ancestor, descendant)


def get_parent(descendant, visible_ancestors):
    try:
        parent = descendant.father
    except Ancestor.DoesNotExist:
        return

    if parent in visible_ancestors:
        return

    return parent
