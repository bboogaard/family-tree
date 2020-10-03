"""
Views for the tree app.

"""
from django.shortcuts import get_object_or_404, render

from tree import helpers, models


def tree(request, ancestor=None, descendant=None):
    """Build and render the tree."""
    if not ancestor:
        kwargs = {
            'is_root': True
        }
    else:
        kwargs = {
            'slug': ancestor
        }

    ancestor = get_object_or_404(models.Ancestor, **kwargs)

    if not descendant:
        lineage = get_object_or_404(models.Lineage, ancestor=ancestor)
        descendant = lineage.descendant
        lineage = helpers.get_lineage(ancestor, lineage.descendant)
    else:
        descendant = get_object_or_404(models.Ancestor, slug=descendant)
        lineage = helpers.get_lineage(ancestor, descendant)

    return render(
        request,
        'tree.html',
        {
            'root_ancestor': ancestor,
            'descendant': descendant,
            'lineage': lineage
        }
    )
