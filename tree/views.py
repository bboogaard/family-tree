"""
Views for the tree app.

"""
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from tree import models
from tree.helpers import get_lineages
from version import VERSION


def tree(request, ancestor=None):
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
    lineages = get_lineages(ancestor_obj)

    if not lineages.root:
        raise Http404()

    if ancestor and ancestor_obj.is_root:
        return redirect(reverse('tree'), permanent=True)

    return render(
        request,
        'tree.html',
        {
            'root_ancestor': ancestor_obj,
            'lineages': lineages
        }
    )


def version(request):
    content = 'Family Tree v. {}'.format(VERSION)
    return HttpResponse(content, content_type='text/plain')
