"""
Django-admin integration for the scraper app.

"""
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from scraper import models
from services.scraper.factory import ScraperServiceFactory


class PageAdmin(admin.ModelAdmin):

    actions = ['scrape']

    list_display = ['url', 'name', 'ancestor_url']

    search_fields = ['name', 'ancestor__pk']

    def scrape(self, request, queryset):
        for page in queryset:
            ScraperServiceFactory.create().find(page, depth=3)
    scrape.short_description = 'Scrape pagina'

    def ancestor_url(self, obj):
        if not obj.ancestor:
            return '-'

        return format_html('<a href="{}">{}</a>'.format(
            reverse('admin:tree_ancestor_change', args=[obj.ancestor.pk]),
            str(obj.ancestor)
        ))
    ancestor_url.short_description = 'Voorouder'

admin.site.register(models.Page, PageAdmin)
