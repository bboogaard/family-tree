"""
Tags for rendering the tree.

"""
import itertools

from django import template
from django.template.loader import render_to_string

from tree import helpers


register = template.Library()


@register.inclusion_tag('templatetags/tree.html', takes_context=True)
def render_tree(context, ancestor):
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

    flat_ancestors = context.get('flat_ancestors', [])
    flat_ancestors.extend(
        itertools.chain.from_iterable(
            [(ancestor, spouse) for ancestor, spouse, _ in marriages]
        )
    )

    context.update({
        'marriages': marriages,
        'flat_ancestors': flat_ancestors
    })
    return context


@register.simple_tag(takes_context=True)
def render_ancestor(context, ancestor, css_class=None):
    root_ancestor = context.get('root_ancestor')
    lineages = context.get('lineages')
    if not root_ancestor or not lineages:
        return ''

    parent = helpers.get_parent(
        ancestor, context.get('flat_ancestors', [])
    )

    return render_to_string('templatetags/ancestor.html', {
        'root_ancestor': root_ancestor,
        'lineages': lineages,
        'ancestor': ancestor,
        'parent': parent,
        'css_class': css_class
    })
