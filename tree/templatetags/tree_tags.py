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
    marriages = [
        (marriage.ancestor, marriage.spouse, marriage.children)
        for marriage in helpers.get_marriages(ancestor)
    ]

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

    parents = helpers.get_parents(
        ancestor, context.get('flat_ancestors', [])
    )

    return render_to_string('templatetags/ancestor.html', {
        'root_ancestor': root_ancestor,
        'lineages': lineages,
        'ancestor': ancestor,
        'parents': parents,
        'css_class': css_class
    })
