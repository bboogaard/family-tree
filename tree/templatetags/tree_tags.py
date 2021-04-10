"""
Tags for rendering the tree.

"""
import itertools

from django import template
from django.template.loader import render_to_string
from django.urls import reverse

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


@register.inclusion_tag('templatetags/bio.html')
def render_bio(ancestor):
    bio = ancestor.get_bio()

    if not bio:
        return {
            'ancestor': ancestor,
            'lines': []
        }

    lines = helpers.get_bio_details(bio)

    return {
        'ancestor': ancestor,
        'lines': lines
    }


@register.simple_tag()
def ancestor_url(ancestor, fallback_to_bio=True):
    result = helpers.ancestor_url(ancestor)
    if not result and fallback_to_bio:
        result = reverse(
            'ancestor_bio',
            kwargs={
                'ancestor': ancestor.slug
            }
        )
    return result
