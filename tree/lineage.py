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


class LineageBuilder(object):

    def __init__(self):
        self._descendant = None
        self._generations = []

    def build(self, ancestor, descendant):
        self._generations = []
        self._get_generations(ancestor, descendant, 1)
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

    @staticmethod
    def _get_children(ancestor):
        return list(ancestor.children.order_by_age())


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

    @cache_method_result('lineage-objects', key_attrs=['ancestor'],
                         timeout=None)
    def _get_objects(self, descendants=None):
        queryset = (
            models.Lineage.objects
            .select_related(
                'ancestor',
                'descendant'
            )
            .prefetch_related(
                'generations'
            )
        )
        if descendants is None:
            queryset = queryset.for_ancestor(self.ancestor)
        else:
            queryset = queryset.for_ancestor_and_descendants(
                self.ancestor, descendants
            )
        objects = list(queryset)

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


class PlanLineages(Lineages):

    def __init__(self, ancestor, descendant):
        super().__init__(ancestor)
        self.descendant = descendant
        self._generations = []

    def _get_objects(self, generations=None):
        generations = LineageBuilder().build(self.ancestor, self.descendant)
        descendants = [ancestor for ancestor, _ in generations]
        objects = super()._get_objects(descendants)
        root_lineage = Lineage(self.ancestor, self.descendant, descendants)
        objects.update({
            self.ancestor.pk: root_lineage
        })
        return objects


class LineagesFactory:

    @classmethod
    def create(cls, ancestor, descendant=None):
        return Lineages(ancestor) if not descendant else PlanLineages(
            ancestor, descendant
        )
