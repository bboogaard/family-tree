from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from scraper.models import Page
from services.scraper.service import ScraperService


class Command(BaseCommand):
    help = 'Scrape a page'

    def add_arguments(self, parser):
        parser.add_argument('page_id', type=int, nargs=1, help='Page id')
        parser.add_argument('--depth', type=int, nargs='?', help='Search depth', default=2)
        parser.add_argument('--direction', type=str, nargs='?', help='Search direction', default=settings.SCRAPE_DIRECTION_DOWN)

    def handle(self, *args, **options):
        try:
            page = Page.objects.get(pk=options['page_id'][0])
        except Page.DoesNotExist:
            raise CommandError("Page not found")

        if options['direction'] not in settings.SCRAPE_DIRECTIONS:
            raise CommandError("Not a valid search direction")

        ScraperService().find(page, depth=options['depth'], direction=options['direction'])
