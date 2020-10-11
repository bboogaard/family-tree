"""
Tags for rendering the tree.

"""
import itertools

from django import template
from django.template.loader import render_to_string

from tree import models, helpers


register = template.Library()


@register.inclusion_tag('templatetags/tree.html', takes_context=True)
def render_tree(context, ancestor, descendant):
    marriages = []

    if ancestor.gender == 'm':
        for marriage in ancestor.marriages_of_husband.all():
            children = (
                ancestor.children_of_father
                .filter(mother=marriage.wife)
                .with_marriages()
                .order_by_age()
            )
            marriages.append((ancestor, marriage.wife, children))
    elif ancestor.gender == 'f':
        for marriage in ancestor.marriages_of_wife.all():
            children = (
                ancestor.children_of_mother
                .filter(father=marriage.husband)
                .with_marriages()
                .order_by_age()
            )
            marriages.append((ancestor, marriage.husband, children))

    root_ancestor = context.get('root_ancestor', ancestor)

    flat_ancestors = context.get('flat_ancestors', [])
    flat_ancestors.extend(
        itertools.chain.from_iterable(
            [(ancestor, spouse) for ancestor, spouse, _ in marriages]
        )
    )

    context.update({
        'marriages': marriages,
        'root_ancestor': root_ancestor,
        'descendant': descendant,
        'flat_ancestors': flat_ancestors
    })
    return context


@register.simple_tag(takes_context=True)
def render_ancestor(context, ancestor, css_class=None):
    root_ancestor = context.get('root_ancestor')
    lineages = context.get('lineages')
    if not root_ancestor or not lineages:
        return ''

    descendant = None
    if ancestor != root_ancestor:
        lineage = lineages.get(ancestor.pk)
        if lineage:
            descendant = lineage.descendant

    parent = helpers.get_parent(
        ancestor, context.get('flat_ancestors', [])
    )
    if parent:
        parent_lineage = lineages.get(parent.pk)
        if parent_lineage:
            parent = {
                'instance': parent,
                'descendant': parent_lineage.descendant
            }
        else:
            parent = None

    return render_to_string('templatetags/ancestor.html', {
        'ancestor': ancestor,
        'descendant': descendant,
        'parent': parent,
        'css_class': css_class
    })
