from tree import helpers, models
from tree.tests.testcases import TreeTestCase


class TestHelpers(TreeTestCase):

    with_persistent_names = True

    def test_build_lineage(self):
        lineage = models.Lineage.objects.select_related(
            'ancestor', 'descendant'
        ).get(pk=self.lineage.pk)
        with self.assertNumQueries(2):
            result = helpers.build_lineage(lineage)
        expected = [
            (self.generation_1[0], 1)
        ]
        self.assertEqual(result, expected)

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
