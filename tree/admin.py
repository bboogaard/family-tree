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

    raw_id_fields = ['wife']


class MarriageOfWifeInLine(NestedStackedInline):

    model = models.Marriage

    extra = 0

    fk_name = 'wife'

    form = MarriageForm

    raw_id_fields = ['husband']


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

    raw_id_fields = ['descendant']


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

    title = 'Voorouder'

    parameter_name = 'ancestor_id'

    field_name = 'id'

    def lookups(self, request, model_admin):
        value = self.value_as_list()
        if value:
            return [
                (str(ancestor.pk), str(ancestor))
                for ancestor in models.Ancestor.objects.filter(pk__in=value)
            ]

        return []

    def queryset(self, request, queryset):
        value = self.value_as_list()
        if value:
            return queryset.filter(**{
                '{}__in'.format(self.field_name): value
            })

        return queryset

    def value_as_list(self):
        return self.value().split(',') if self.value() else []


class AncestorAdmin(NestedModelAdmin):

    inlines = [
        MarriageOfHusbandInLine, MarriageOfWifeInLine, LineageInLine, BioInLine
    ]

    list_display = ['get_fullname', 'get_age', 'slug']

    list_filter = [AncestorFilter, 'lineage']

    form = AncestorForm

    raw_id_fields = ['father', 'mother', 'christian_name']

    search_fields = ['christian_name__name', 'lastname', 'birthyear', 'year_of_death']

    def clear_caches(self, request, queryset):
        for ancestor in queryset:
            cache.delete('ancestor-url:{}'.format(ancestor.pk))

    actions = ['clear_caches']


admin.site.register(models.Ancestor, AncestorAdmin)


class LineageAdmin(admin.ModelAdmin):

    form = LineageForm

    def clear_caches(self, request, queryset):
        for lineage in queryset:
            cache.delete('lineages:{}'.format(lineage.ancestor_id))
            cache.delete('lineage-objects:ancestor={}'.format(
                lineage.ancestor_id))
            cache.delete(
                make_template_fragment_key('tree', [lineage.ancestor_id])
            )

    actions = ['clear_caches']


admin.site.register(models.Lineage, LineageAdmin)


class ChristianNameAdmin(admin.ModelAdmin):

    list_display = ['name']

    readonly_fields = ['name']


admin.site.register(models.ChristianName, ChristianNameAdmin)
