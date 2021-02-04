from django.conf import settings

from services.search.service import search_service
from tree.tests.testcases import TreeTestCase


class TestSearchService(TreeTestCase):

    with_persistent_names = True

    def test_search(self):
        with self.assertNumQueries(4):
            result = list(search_service.search('Johnny'))
        expected = [
            self.top_male, self.generation_2[0]
        ]
        self.assertEqual(result, expected)

    def test_search_by_score(self):
        with self.assertNumQueries(4):
            result = list(search_service.search('Johnny', settings.SEARCH_ORDER_BY_SCORE))
        expected = [
            self.generation_2[0], self.top_male
        ]
        self.assertEqual(result, expected)

    def test_search_by_no_valid_order_by(self):
        result = list(search_service.search('Johnny', 'foo'))
        expected = [
            self.top_male, self.generation_2[0]
        ]
        self.assertEqual(result, expected)
