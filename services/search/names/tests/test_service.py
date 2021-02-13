from django.conf import settings

from services.search.names.service import SearchNameService
from tree.tests.testcases import TreeTestCase


class TestSearchService(TreeTestCase):

    with_persistent_names = True

    def setUp(self):
        super().setUp()
        self.service = SearchNameService()

    def test_search(self):
        with self.assertNumQueries(4):
            result = list(self.service.search('Johnny'))
        expected = [
            self.top_male, self.generation_2[0]
        ]
        self.assertEqual(result, expected)

    def test_search_by_score(self):
        with self.assertNumQueries(4):
            result = list(self.service.search(
                'Johnny', settings.SEARCH_ORDER_BY_SCORE))
        expected = [
            self.generation_2[0], self.top_male
        ]
        self.assertEqual(result, expected)

    def test_search_by_no_valid_order_by(self):
        result = list(self.service.search('Johnny', 'foo'))
        expected = [
            self.top_male, self.generation_2[0]
        ]
        self.assertEqual(result, expected)
