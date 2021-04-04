from django import forms


class SearchAncestorForm(forms.Form):

    has_children = forms.NullBooleanField()

    lastname = forms.CharField(required=False)

    birthyear_from = forms.IntegerField(required=False)

    birthyear_to = forms.IntegerField(required=False)

    def clean(self):
        data = self.cleaned_data

        if data:
            if data.get('birthyear_from') and data.get('birthyear_to'):
                if data.get('birthyear_to') < data.get('birthyear_from'):
                    raise forms.ValidationError(
                        "'Birth year to' should be after 'Birth year from'",
                        code='invalid'
                    )

        return data
