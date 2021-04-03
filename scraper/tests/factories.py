import factory

from scraper.models import Page


class PageFactory(factory.django.DjangoModelFactory):

    url = '/path/to/url'

    class Meta:
        model = Page
