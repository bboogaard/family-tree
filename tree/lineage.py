"""
Contains a wrapper to hold lineage data.

"""
from lib.cache.decorators import cache_method_result
from tree import models


class Lineage(object):

    def __init__(self, ancestor, descendant, generations):
        self.ancestor = ancestor
        self.descendant = descendant
        self.generations = generations

    def __contains__(self, item):
        return item in self.generations


class Lineages(object):
    """A wrapper to hold and find lineage data."""

    def __init__(self, ancestor):
        self.ancestor = ancestor
        self._objects = None

    def __getitem__(self, item):
        return self.objects[item]

    def __contains__(self, item):
        return item in self.objects

    def get(self, item):
        return self.objects.get(item)

    @property
    def root(self):
        return self.get(self.ancestor.pk)

    @property
    def objects(self):
        if self._objects is None:
            self._objects = self._get_objects()
        return self._objects

    @cache_method_result('lineage-objects', key_attrs=['ancestor'], timeout=None)
    def _get_objects(self):
        objects = list(
            models.Lineage.objects
            .select_related(
                'ancestor',
                'descendant'
            )
            .prefetch_related(
                'generations'
            )
            .for_ancestor(self.ancestor)
        )

        return {
            lineage.ancestor.pk: Lineage(
                lineage.ancestor,
                lineage.descendant,
                [
                    generation.ancestor
                    for generation in lineage.generations.all()
                ]
            )
            for lineage in objects
        }
