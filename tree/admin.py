"""
Django-admin integration for the tree app.

"""
from django import forms
from django.contrib import admin
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from nested_inline.admin import NestedStackedInline, NestedModelAdmin

from tree import models


class AncestorField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return obj.get_fullname() + ' ' + obj.get_age()


class MaleField(AncestorField):

    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = models.Ancestor.objects.filter(gender='m')
        super().__init__(*args, **kwargs)


class FemaleField(AncestorField):

    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = models.Ancestor.objects.filter(gender='f')
        super().__init__(*args, **kwargs)


class MarriageForm(forms.ModelForm):

    class Meta:
        model = models.Marriage
        fields = '__all__'
        field_classes = {
            'husband': MaleField,
            'wife': FemaleField
        }


class MarriageOfHusbandInLine(NestedStackedInline):

    model = models.Marriage

    extra = 0

    fk_name = 'husband'

    form = MarriageForm


class MarriageOfWifeInLine(NestedStackedInline):

    model = models.Marriage

    extra = 0

    fk_name = 'wife'

    form = MarriageForm


class GenerationInLine(NestedStackedInline):

    extra = 0

    model = models.Generation

    read_only_fields = ['lineage', 'ancestor', 'generation']


class LineageForm(forms.ModelForm):

    class Meta:
        model = models.Lineage
        fields = '__all__'
        field_classes = {
            'ancestor': AncestorField,
            'descendant': AncestorField
        }


class LineageInLine(NestedStackedInline):

    model = models.Lineage

    extra = 0

    fk_name = 'ancestor'

    form = LineageForm

    inlines = [GenerationInLine]


admin.site.register(models.BioLink)


class BioInLine(NestedStackedInline):

    extra = 0

    model = models.Bio


admin.site.register(models.Bio)


class AncestorForm(forms.ModelForm):

    class Meta:
        model = models.Ancestor
        fields = '__all__'
        field_classes = {
            'father': MaleField,
            'mother': FemaleField
        }


class AncestorFilter(admin.SimpleListFilter):

    def lookups(self, request, model_admin):
        return [
            (obj.pk, obj.get_fullname() + ' ' + obj.get_age())
            for obj in self.ancestor_queryset.all()
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{
                '{}__pk'.format(self.related_field): self.value()
            })

        return queryset


class FatherFilter(AncestorFilter):

    ancestor_queryset = models.Ancestor.objects.filter(gender='m')

    parameter_name = 'father'

    related_field = 'father'

    title = 'Vader'


class MotherFilter(AncestorFilter):

    ancestor_queryset = models.Ancestor.objects.filter(gender='f')

    parameter_name = 'mother'

    related_field = 'mother'

    title = 'Moeder'


class AncestorAdmin(NestedModelAdmin):

    inlines = [
        MarriageOfHusbandInLine, MarriageOfWifeInLine, LineageInLine, BioInLine
    ]

    list_display = ['get_fullname', 'get_age', 'slug']

    list_filter = [FatherFilter, MotherFilter, 'lineage']

    form = AncestorForm


admin.site.register(models.Ancestor, AncestorAdmin)


class LineageAdmin(admin.ModelAdmin):

    form = LineageForm

    def clear_caches(self, request, queryset):
        for lineage in queryset:
            cache.delete('lineages:{}'.format(lineage.ancestor_id))
            cache.delete('lineage-objects:ancestor={}'.format(lineage.ancestor_id))
            cache.delete(
                make_template_fragment_key('tree', [lineage.ancestor_id])
            )

    actions = [clear_caches]


admin.site.register(models.Lineage, LineageAdmin)
