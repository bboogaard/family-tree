"""
Views for the tree app.

"""
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.base import ContextMixin, TemplateResponseMixin, View

from lib.api import call_api
from lib.auth import login_protected
from services.tree.service import TreeService
from tree import forms, models
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


@login_protected()
class CreateTreeView(ContextMixin, TemplateResponseMixin, View):

    template_name = 'create_tree.html'

    def dispatch(self, request, *args, **kwargs):
        self.descendant = get_object_or_404(models.Ancestor, pk=self.kwargs['pk'])
        self.ancestors = TreeService().find(self.descendant)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.get_form(descendant=self.descendant, ancestors=self.ancestors)
        context = self.get_context_data(descendant=self.descendant, form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST, descendant=self.descendant, ancestors=self.ancestors)
        if form.is_valid():
            response_status, response_data = call_api('trees', form.cleaned_data, self.request.user)
            if response_status == 201:
                return redirect(request.path)

            context = self.get_context_data(
                descendant=self.descendant,
                form=form,
                response_status=response_status,
                response_data=response_data
            )
        else:
            context = self.get_context_data(descendant=self.descendant, form=form)

        return self.render_to_response(context)

    def get_form(self, data=None, **kwargs):
        return forms.CreateTreeForm(data, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'name': 'Ancestors of {}'.format(self.descendant),
            'breadcrumblist': [
                ('Ancestors of {}'.format(self.descendant), self.request.path)
            ],
            'preview_urls': {
                ancestor.pk: reverse(
                    'preview_tree', kwargs={
                        'ancestor': ancestor.slug,
                        'descendant': self.descendant.slug
                    }
                )
                for ancestor in self.ancestors
            }
        })
        return context


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
