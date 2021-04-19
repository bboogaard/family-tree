from django.conf import settings
from django.core.management import call_command

from lib.tasks import task


@task
def scrape_page(page_id, depth=2, direction=settings.SCRAPE_DIRECTION_DOWN):
    call_command('scrape_page', page_id, depth=depth, direction=direction)
    print("Done")
