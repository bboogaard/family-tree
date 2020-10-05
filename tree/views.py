"""
Views for the tree app.

"""
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

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

    ancestor_obj = get_object_or_404(models.Ancestor, **kwargs)
    lineage = ancestor_obj.get_lineage()

    if not descendant:
        if not lineage:
            raise Http404()
        descendant_obj = lineage.descendant
    else:
        descendant_obj = get_object_or_404(models.Ancestor, slug=descendant)

    if ancestor and descendant:
        if lineage and lineage.descendant == descendant_obj:
            if ancestor_obj.is_root:
                return redirect(reverse('tree'), permanent=True)
            else:
                return redirect(reverse('ancestor_tree', kwargs={
                    'ancestor': ancestor
                }), permanent=True)
    elif ancestor:
        if ancestor_obj.is_root:
            return redirect(reverse('tree'), permanent=True)

    return render(
        request,
        'tree.html',
        {
            'root_ancestor': ancestor_obj,
            'descendant': descendant_obj
        }
    )
