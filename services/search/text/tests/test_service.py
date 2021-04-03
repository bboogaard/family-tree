from django.conf import settings

from services.search.models import SearchTextRequest
from services.search.text.service import SearchTextService
from tree.tests.testcases import TreeTestCase


class TestSearchService(TreeTestCase):

    with_persistent_names = True

    def setUp(self):
        super().setUp()
        self.service = SearchTextService()
        self.top_male.birthplace = 'Oldtown'
        self.top_male.place_of_death = 'Newtown'
        self.top_male.save()

        self.generation_1[0].birthplace = 'Newtown'
        self.generation_1[0].place_of_death = 'Newtown'
        self.generation_1[0].save()

    def test_search(self):
        with self.assertNumQueries(1):
            result = list(self.service.search(SearchTextRequest(text='Newtown')))
        expected = [
            self.top_male, self.generation_1[0]
        ]
        self.assertEqual(result, expected)

    def test_search_by_score(self):
        with self.assertNumQueries(1):
            result = list(self.service.search(
                SearchTextRequest(text='Newtown'), settings.SEARCH_ORDER_BY_RANK))
        expected = [
            self.generation_1[0], self.top_male
        ]
        self.assertEqual(result, expected)

    def test_search_by_no_valid_order_by(self):
        result = list(self.service.search(SearchTextRequest(text='Newtown'), 'foo'))
        expected = [
            self.top_male, self.generation_1[0]
        ]
        self.assertEqual(result, expected)
