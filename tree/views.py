"""
Views for the tree app.

"""
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from lib.auth import login_protected
from tree import models
from tree.helpers import get_lineages, get_marriages
from version import VERSION


class BaseTreeView(TemplateView):

    ancestor = None

    lineages = None

    template_name = 'tree.html'

    def get(self, request, *args, **kwargs):
        self.ancestor = self._get_ancestor(kwargs.get('ancestor'))
        self.lineages = self._get_lineages()
        if not self.lineages.root:
            raise Http404()
        if redirect_response := self.get_redirect():
            return redirect_response
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'root_ancestor': self.ancestor,
            'lineages': self.lineages
        })
        return context

    def get_redirect(self):
        pass

    @staticmethod
    def _get_ancestor(slug=None, fallback_root=True):
        if slug:
            kwargs = {
                'slug': slug
            }
        elif fallback_root:
            kwargs = {
                'is_root': True
            }
        else:
            raise Http404()

        return get_object_or_404(models.Ancestor, **kwargs)

    def _get_lineages(self):
        return get_lineages(self.ancestor)


class TreeView(BaseTreeView):

    def get_redirect(self):
        if self.kwargs.get('ancestor') and self.ancestor.is_root:
            return redirect(reverse('tree'), permanent=True)


@login_protected()
class PreviewTreeView(BaseTreeView):

    descendant = None

    def get(self, request, *args, **kwargs):
        self.descendant = self._get_ancestor(kwargs.get('descendant'))
        return super().get(request, *args, **kwargs)

    def _get_lineages(self):
        return get_lineages(self.ancestor, self.descendant)


def bio(request, ancestor):
    ancestor_obj = get_object_or_404(models.Ancestor, slug=ancestor)
    return render(
        request,
        'bio.html',
        {
            'ancestor': ancestor_obj,
            'bio': ancestor_obj.get_bio(),
            'marriages': get_marriages(ancestor_obj)
        }
    )


def version(request):
    content = 'Family Tree v. {}'.format(VERSION)
    return HttpResponse(content, content_type='text/plain')
