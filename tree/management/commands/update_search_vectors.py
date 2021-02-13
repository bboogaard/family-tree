from django.core.management.base import BaseCommand

from lib.search.search_vectors import search_vector_registry


class Command(BaseCommand):
    help = 'Update all search vector fields'

    def handle(self, *args, **options):
        search_vector_registry.update()
