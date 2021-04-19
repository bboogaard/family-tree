from api.exceptions import Conflict
from services.tree.service import TreeService

from tree.tests.testcases import TreeTestCase


class TestTreeService(TreeTestCase):

    with_persistent_names = True

    def setUp(self):
        super().setUp()
        self.service = TreeService()

    def test_create(self):
        result = TreeService().create(self.top_female, self.generation_2[0])
        expected = self.top_female
        self.assertEqual(result, expected)

    def test_create_exists(self):
        with self.assertRaises(Conflict):
            TreeService().create(self.top_male, self.generation_2[0])

    def test_find(self):
        result = TreeService().find(self.generation_2[0])
        expected = [self.top_female, self.spouse_1]
        self.assertEqual(result, expected)
