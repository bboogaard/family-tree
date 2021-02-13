"""
Helpers for the tree app.

"""
import re
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from django.urls import reverse
from django.utils.html import format_html

from lib.cache.decorators import cache_result
from services.lineage.service import LineageService
from tree.models import Ancestor
from tree.lineage import Lineages


re_bio_line = re.compile(r'^\*\s?([^:]+)\s?:\s(.*)$')


class LineageBuilder(object):

    def __init__(self):
        self._descendant = None
        self._generations = []

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

    @staticmethod
    def _get_children(ancestor):
        return list(ancestor.children.order_by_age())


def build_lineage(lineage):
    return LineageBuilder().build(lineage)


@cache_result('lineages', timeout=None)
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


@dataclass
class Marriage:
    ancestor: Ancestor
    spouse: Ancestor
    children: List[Ancestor]
    date_of_marriage: Optional[date]
    place_of_marriage: Optional[str]


def get_marriages(ancestor):
    marriages = []
    if ancestor.gender == 'm':
        for marriage in ancestor.marriages_of_husband.all():
            children = (
                ancestor.children_of_father
                .filter(mother=marriage.wife)
                .with_marriages()
                .order_by_age()
            )
            marriages.append(Marriage(
                ancestor,
                marriage.wife,
                children,
                marriage.date_of_marriage,
                marriage.place_of_marriage
            ))
    elif ancestor.gender == 'f':
        for marriage in ancestor.marriages_of_wife.all():
            children = (
                ancestor.children_of_mother
                .filter(father=marriage.husband)
                .with_marriages()
                .order_by_age()
            )
            marriages.append(Marriage(
                ancestor,
                marriage.husband,
                children,
                marriage.date_of_marriage,
                marriage.place_of_marriage
            ))
    return marriages


@cache_result('ancestor_url', timeout=None)
def ancestor_url(ancestor, root_only=False):
    lineage_service = LineageService()
    if not root_only:
        if root_ancestor := lineage_service.find_root(ancestor):
            return reverse(
                'ancestor_tree',
                kwargs={
                    'ancestor': root_ancestor.slug
                }
            )
    elif lineage_service.has_lineage(ancestor):
        return reverse(
            'ancestor_tree',
            kwargs={
                'ancestor': ancestor.slug
            }
        )


def get_bio_details(bio):
    lines = []
    for line in map(lambda ln: ln.strip(), bio.details.split('\n')):
        if not line:
            continue

        match = re_bio_line.match(line)
        if match is None:
            lines.append(('', line))
            continue

        lines.append((match.group(1), match.group(2)))
    return lines


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
