"""
Views for the tree app.

"""
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.views.generic import TemplateView

from lib.auth import login_protected
from lib.views import CallApiView, FormView
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


class CreateTreeView(CallApiView):

    endpoint = reverse_lazy('api:trees-list')

    expected_status = 201

    form_class = forms.CreateTreeForm

    template_name = 'create_tree.html'

    def dispatch(self, request, *args, **kwargs):
        self.descendant = get_object_or_404(models.Ancestor, pk=self.kwargs['pk'])
        self.ancestors = TreeService().find(self.descendant)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, data=None, **kwargs):
        return forms.CreateTreeForm(
            data, descendant=self.descendant, ancestors=self.ancestors, **kwargs
        )

    def get_title(self):
        return 'Ancestors of {}'.format(self.descendant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'descendant': self.descendant,
            'ancestors': self.ancestors,
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


class RunTaskView(CallApiView):

    form_class = forms.TaskForm

    endpoint_method = 'get'

    template_name = 'run_task.html'

    title = 'Run task'

    def get_endpoint(self, data):
        command = data.pop('command')
        return reverse('api:tasks-run-command', kwargs={
            'command': command
        })

    def send_messages(self):
        messages.add_message(self.request, messages.INFO, 'Task started')


@login_protected()
class TaskHelper(FormView):

    redirect_url = reverse_lazy('run_task')

    template_name = 'task_helper.html'

    title = 'Task helper'

    def dispatch(self, request, command, *args, **kwargs):
        self.command = command
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        data = {
            key: val for key, val in form.cleaned_data.items() if val is not None
        }
        params = {
            'command': self.command,
            'query_string': urlencode(data)
        }
        return redirect(
            self.get_redirect_url() + '?' + urlencode(params)
        )

    def get_form_class(self):
        if self.command == 'scrape_page':
            return forms.ScrapePageForm

        raise NotImplementedError()

    def get_redirect_url(self):
        return self.redirect_url


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
