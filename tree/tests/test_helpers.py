import operator

from django.test import TestCase

from tree import helpers
from tree.tests.testcases import TreeTestCase


class TestHelpers(TreeTestCase):

    def test_get_lineage(self):
        result = helpers.get_lineage(self.top_male, self.generation_2[0])
        expected = [
            self.top_male, self.top_female, self.generation_1[0], self.spouse_1
        ]
        self.assertItemsEqual(result, expected)

    def test_get_parent(self):
        result = helpers.get_parent(
            descendant=self.generation_1[0],
            visible_ancestors=[self.generation_1[0], self.spouse_1]
        )
        expected = self.top_male
        self.assertEqual(result, expected)

    def test_get_parent_doesnotexist(self):
        result = helpers.get_parent(
            descendant=self.top_male,
            visible_ancestors=[
                self.top_male, self.top_female, self.generation_1[0],
                self.spouse_1
            ]
        )
        self.assertIsNone(result)

    def test_get_parent_in_visible_ancestors(self):
        result = helpers.get_parent(
            descendant=self.generation_1[0],
            visible_ancestors=[
                self.top_male, self.top_female, self.generation_1[0],
                self.spouse_1
            ]
        )
        expected = self.top_male
        self.assertIsNone(result)
