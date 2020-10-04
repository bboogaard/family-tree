"""
Tags for rendering the tree.

"""
import itertools

from django import template

from tree import helpers


register = template.Library()


@register.inclusion_tag('templatetags/tree.html', takes_context=True)
def render_tree(context, ancestor, lineage):
    if ancestor.gender == 'm':
        marriages = []
        for marriage in ancestor.marriages_of_husband.all():
            children = ancestor.children_of_father.filter(
                mother=marriage.wife
            ).order_by_age()
            marriages.append((ancestor, marriage.wife, children))
    elif ancestor.gender == 'f':
        marriages = []
        for marriage in ancestor.marriages_of_wife.all():
            children = ancestor.children_of_father.filter(
                father=marriage.husband
            ).order_by_age()
            marriages.append((ancestor, marriage.husband, children))

    flat_ancestors = context.get('flat_ancestors', [])
    flat_ancestors.extend(
        itertools.chain.from_iterable(
            [(ancestor, spouse) for ancestor, spouse, _ in marriages]
        )
    )

    print(lineage)

    context.update({
        'marriages': marriages,
        'lineage': lineage,
        'flat_ancestors': flat_ancestors
    })
    return context


@register.inclusion_tag('templatetags/ancestor.html', takes_context=True)
def render_ancestor(context, ancestor, css_class=None):
    root_ancestor = context['root_ancestor']
    descendant = context['descendant']
    lineage = ancestor.get_lineage()

    if lineage and ancestor != root_ancestor \
            or lineage.descendant != descendant:
        descendant = lineage.descendant
    else:
        descendant = None

    parent = helpers.get_parent(
        ancestor, context.get('flat_ancestors', [])
    )
    if parent:
        parent_lineage = parent.get_lineage()
        if parent_lineage:
            parent = {
                'instance': parent,
                'descendant': parent_lineage.descendant
            }
        else:
            parent = None

    return {
        'ancestor': ancestor,
        'descendant': descendant,
        'parent': parent,
        'css_class': css_class
    }
