from urllib.parse import parse_qs

from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from django import forms
from django.conf import settings
from django.urls import reverse, reverse_lazy

from lib.forms import AutoComplete, form_helper_factory
from scraper.models import Page


class CreateTreeForm(forms.Form):

    ancestor_id = forms.TypedChoiceField(choices=(), coerce=int, label='Ancestor')

    descendant_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        descendant = kwargs.pop('descendant')
        ancestors = kwargs.pop('ancestors')
        super().__init__(*args, **kwargs)
        self.initial['descendant_id'] = descendant.id
        self.fields['ancestor_id'].choices = [('', '----------')] + [
            (ancestor.id, str(ancestor))
            for ancestor in ancestors
        ]
        self.helper = form_helper_factory(
            self,
            ['ancestor_id', 'descendant_id'],
            'col-md-4',
            'Create tree',
            [('preview-btn', 'Preview tree', {'disabled': True})]
        )


class TaskForm(forms.Form):

    command = forms.ChoiceField(choices=[('', '----------')] + list(settings.AVAILABLE_COMMANDS))

    query_string = forms.CharField(
        required=False,
        label='Query string'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = form_helper_factory(
            self,
            [
                'command',
                FieldWithButtons(
                    'query_string',
                    StrictButton("Build", css_id='helper-btn', disabled=True)
                )
            ],
            'col-md-6',
            'Run task'
        )

    def clean(self):
        data = self.cleaned_data

        if data:
            data = {
                'command': data.get('command'),
                **parse_qs(data.get('query_string', ''))
            }

        return data

    @property
    def task_helpers(self):
        return {
            command: reverse('task_helper', kwargs={
                'command': command
            }) for command, _ in settings.AVAILABLE_COMMANDS
        }


def lookup_page(page_id):
    if not page_id:
        return

    return Page.objects.filter(pk=page_id).first()


class ScrapePageForm(forms.Form):

    page_id = forms.IntegerField(
        widget=AutoComplete(reverse_lazy('api:lookup-page'), lookup_func=lookup_page),
        label='Page'
    )

    depth = forms.IntegerField(
        min_value=2,
        label='Depth',
        required=False
    )

    direction = forms.ChoiceField(
        choices=settings.SCRAPE_DIRECTIONS,
        label='Direction',
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = form_helper_factory(
            self,
            ['page_id', 'depth', 'direction'],
            'col-md-6',
            'Build query string'
        )
