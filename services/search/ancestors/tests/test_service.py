from services.search.ancestors.service import SearchAncestorService
from services.search.models import SearchAncestorRequest
from tree.tests.testcases import TreeTestCase


class TestSearchAncestorService(TreeTestCase):

    with_persistent_names = True

    def setUp(self):
        super().setUp()
        self.service = SearchAncestorService()

    def test_search_by_has_children(self):
        result = list(self.service.search(SearchAncestorRequest(
            has_children=False
        )))
        expected = self.generation_2 + self.generation_extra
        self.assertEqual(result, expected)

    def test_search_by_lastname(self):
        result = list(self.service.search(SearchAncestorRequest(
            lastname='snyder'
        )))
        expected = [self.top_female]
        self.assertEqual(result, expected)

    def test_search_by_birthyear(self):
        result = list(self.service.search(SearchAncestorRequest(
            birthyear_from=1890
        )))
        expected = [self.generation_extra[1]]
        self.assertEqual(result, expected)
