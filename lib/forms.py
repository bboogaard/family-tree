from typing import Any, Dict, List, Tuple

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Div, Layout, Submit
from django import forms
from django.conf import settings


def form_helper_factory(form: forms.Form, fields: List[Any], field_class: str = 'col-md-10',
                        submit_text: str = 'Submit',
                        buttons: List[Tuple[str, str, Dict]] = None) -> FormHelper:
    helper = FormHelper(form)
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-md-2'
    helper.field_class = field_class
    buttons = [
        Button(button_id, button_text, style="width:auto", **button_attrs)
        for button_id, button_text, button_attrs in buttons
    ] if buttons else []
    helper.layout = Layout(
        *fields,
        Div(
            Div(
                Submit('submit', submit_text, style="width:auto"),
                *buttons,
                css_class='col-md-offset-2',
                style='padding-left: 15px'
            ),
            css_class='form-group'
        )
    )
    return helper


class AutoComplete(forms.TextInput):

    template_name = 'forms/widgets/autocomplete.html'

    class Media:
        js = [settings.STATIC_URL + '/js/bootstrap3-typeahead.js']

    def __init__(self, lookup_url, lookup_func, attrs=None, *args, **kwargs):
        super().__init__(attrs)
        self.lookup_url = lookup_url
        self.lookup_func = lookup_func

    def value_from_datadict(self, data, files, name):
        return data.get(name + '-hidden')

    def get_context(self, name, value, attrs):
        attrs.update({
            'autocomplete': 'off'
        })
        hidden_value = self.format_value(value)
        value = self.lookup_func(value)
        context = super().get_context(name, value, attrs)
        context.update({
            'lookup_url': self.lookup_url,
            'value': value,
            'hidden_value': hidden_value
        })
        return context
