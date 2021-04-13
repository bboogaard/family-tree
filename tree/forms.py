from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Div, Layout, Submit
from django import forms


class CreateTreeForm(forms.Form):

    ancestor_id = forms.TypedChoiceField(choices=(), coerce=int)

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
        self.helper = FormHelper(self)
        self.helper.template_pack = 'bootstrap3'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-4'
        self.helper.layout = Layout(
            'ancestor_id',
            'descendant_id',
            Div(
                Div(
                    Submit('submit', 'Create tree', style="width:auto"),
                    Button('preview-btn', 'Preview tree', style="width:auto", disabled=True),
                    css_class='col-md-offset-2',
                    style='padding-left: 15px'
                ),
                css_class='form-group'
            )
        )
