"""
Helpers for the tree app.

"""
from django.urls import reverse
from django.utils.html import format_html

from tree.lineage import Lineages


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


def get_lineages(ancestor):
    return Lineages(ancestor)


def get_parents(descendant, visible_ancestors):
    father, father_link = _get_parent(descendant.father, visible_ancestors)
    mother, mother_link = _get_parent(descendant.mother, visible_ancestors)
    if not father and not mother or (not father_link and not mother_link):
        return None

    return {
        'father': father,
        'mother': mother
    }


def _get_parent(parent, visible_ancestors):
    if not parent:
        return None, False

    template_kwargs = {
        'name': parent.get_fullname(),
        'age': parent.get_age()
    }
    if all([parent not in visible_ancestors, parent.get_lineage()]):
        template = '<a href="{url}">{name} ({age})</a>'
        template_kwargs['url'] = reverse('ancestor_tree', kwargs={
            'ancestor': parent.slug
        })
        has_link = True
    else:
        template = '{name} ({age})'
        has_link = False

    return format_html(template.format(**template_kwargs)), has_link
