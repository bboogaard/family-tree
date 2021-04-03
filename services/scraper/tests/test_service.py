import os

import mock
from extruct.w3cmicrodata import MicrodataExtractor
from django.test.testcases import TestCase

from scraper.models import Page
from scraper.tests.factories import PageFactory
from services.scraper.service import requests, ScraperService
from tree.models import Ancestor


SUPPORT_DIR = os.path.join(os.path.dirname(__file__), 'support')


@mock.patch.object(MicrodataExtractor, 'extract')
@mock.patch.object(requests, 'get')
@mock.patch('services.scraper.md_parser._parse_url', lambda url: url)
class TestScraperService(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.page = PageFactory(url='http://path/to/john-glass')

    def setUp(self):
        super().setUp()
        self.html = open(os.path.join(SUPPORT_DIR, 'response_1.html'), 'r').read()

    def test_find(self, mock_get, mock_extract):
        mock_response = mock.Mock(status_code=200, content=self.html)
        mock_get.return_value = mock_response
        mock_microdata = [
            {
                'type': 'http://schema.org/Person',
                'properties': {
                    'url': 'http://path/to/john-glass',
                    'givenName': 'John',
                    'familyName': 'Glass',
                    'gender': 'male',
                    'birthDate': '1812',
                    'birthPlace': 'Newtown',
                    'deathDate': '1874',
                    'deathPlace': 'Newtown',
                    'parent': [],
                    'spouse': [],
                    'children': []
                }
            }
        ]
        mock_extract.return_value = mock_microdata

        ScraperService().find(self.page)

        page = Page.objects.get(pk=self.page.pk)
        self.assertEqual(page.name, 'John Glass')
        self.assertTrue(page.processed)

        ancestor = Ancestor.objects.first()
        self.assertEqual(ancestor.firstname, 'John')
        self.assertEqual(ancestor.lastname, 'Glass')
        self.assertEqual(ancestor.gender, 'm')
        self.assertEqual(ancestor.birthyear, 1812)
        self.assertEqual(ancestor.birthplace, 'Newtown')
        self.assertEqual(ancestor.year_of_death, 1874)
        self.assertEqual(ancestor.place_of_death, 'Newtown')
        bio = ancestor.get_bio()
        self.assertNotEqual(bio.details, '')

    def test_find_recursive(self, mock_get, mock_extract):
        mock_responses = [
            mock.Mock(status_code=200, content=self.html),
            mock.Mock(status_code=200, content=self.html),
            mock.Mock(status_code=200, content=self.html)
        ]
        mock_get.side_effect = mock_responses
        mock_microdata = [
            {
                'type': 'http://schema.org/Person',
                'properties': {
                    'url': 'http://path/to/john-glass',
                    'givenName': 'John',
                    'familyName': 'Glass',
                    'gender': 'male',
                    'birthDate': '1812',
                    'birthPlace': 'Newtown',
                    'deathDate': '1874',
                    'deathPlace': 'Newtown',
                    'parent': [],
                    'spouse': [
                        {
                            'type': 'http://schema.org/Person',
                            'properties': {
                                'url': 'http://path/to/jane-snyder',
                                'givenName': 'Jane',
                                'familyName': 'Snyder'
                            }
                        }
                    ],
                    'children': [
                        {
                            'type': 'http://schema.org/Person',
                            'properties': {
                                'url': 'http://path/to/martin-glass',
                                'givenName': 'Martin',
                                'familyName': 'Glass'
                            }
                        }
                    ]
                }
            },
            {
                'type': 'http://schema.org/Person',
                'properties': {
                    'url': 'http://path/to/jane-snyder',
                    'givenName': 'Jane',
                    'familyName': 'Snyder',
                    'gender': 'female',
                    'birthDate': '1824',
                    'birthPlace': 'Newtown',
                    'deathDate': '1890',
                    'deathPlace': 'Newtown',
                    'parent': [],
                    'spouse': [],
                    'children': []
                }
            },
            {
                'type': 'http://schema.org/Person',
                'properties': {
                    'url': 'http://path/to/martin-glass',
                    'givenName': 'Martin',
                    'familyName': 'Glass',
                    'gender': 'male',
                    'birthDate': '1836',
                    'birthPlace': 'Newtown',
                    'deathDate': '1901',
                    'deathPlace': 'Newtown',
                    'parent': [
                        {
                            'type': 'http://schema.org/Person',
                            'properties': {
                                'url': 'http://path/to/john-glass',
                                'givenName': 'John',
                                'familyName': 'Glass'
                            }
                        },
                        {
                            'type': 'http://schema.org/Person',
                            'properties': {
                                'url': 'http://path/to/jane-snyder',
                                'givenName': 'Jane',
                                'familyName': 'Snyder'
                            }
                        }
                    ],
                    'spouse': [],
                    'children': []
                }
            }
        ]
        mock_extract.side_effect = [
            mock_microdata[:1],
            mock_microdata[1:2],
            mock_microdata[2:3]
        ]

        ScraperService().find(self.page)

        pages = Page.objects.all()
        self.assertTrue(all([page.processed for page in pages]))

        ancestor = Ancestor.objects.get_by_natural_key('john-glass-1812-1874')
        self.assertEqual(ancestor.firstname, 'John')
        self.assertEqual(ancestor.lastname, 'Glass')
        self.assertEqual(ancestor.gender, 'm')
        self.assertEqual(ancestor.birthyear, 1812)
        self.assertEqual(ancestor.birthplace, 'Newtown')
        self.assertEqual(ancestor.year_of_death, 1874)
        self.assertEqual(ancestor.place_of_death, 'Newtown')
        self.assertEqual(ancestor.marriages_of_husband.count(), 1)
        bio = ancestor.get_bio()
        self.assertNotEqual(bio.details, '')

        spouse = Ancestor.objects.get_by_natural_key('jane-snyder-1824-1890')
        self.assertEqual(spouse.firstname, 'Jane')
        self.assertEqual(spouse.lastname, 'Snyder')
        self.assertEqual(spouse.gender, 'f')
        self.assertEqual(spouse.birthyear, 1824)
        self.assertEqual(spouse.birthplace, 'Newtown')
        self.assertEqual(spouse.year_of_death, 1890)
        self.assertEqual(spouse.place_of_death, 'Newtown')
        self.assertEqual(spouse.marriages_of_wife.count(), 1)
        bio = spouse.get_bio()
        self.assertNotEqual(bio.details, '')

        child = Ancestor.objects.get_by_natural_key('martin-glass-1836-1901')
        self.assertEqual(child.firstname, 'Martin')
        self.assertEqual(child.lastname, 'Glass')
        self.assertEqual(child.gender, 'm')
        self.assertEqual(child.birthyear, 1836)
        self.assertEqual(child.birthplace, 'Newtown')
        self.assertEqual(child.year_of_death, 1901)
        self.assertEqual(child.place_of_death, 'Newtown')
        self.assertEqual(child.father, ancestor)
        self.assertEqual(child.mother, spouse)
        bio = child.get_bio()
        self.assertNotEqual(bio.details, '')
