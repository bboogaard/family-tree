from tree import helpers, models
from tree.tests.testcases import TreeTestCase


class TestHelpers(TreeTestCase):

    with_persistent_names = True

    def test_build_lineage(self):
        lineage = models.Lineage.objects.select_related(
            'ancestor', 'descendant'
        ).get(pk=self.lineage.pk)
        result = helpers.build_lineage(lineage)
        expected = [
            (self.generation_1[0], 1)
        ]
        self.assertEqual(result, expected)

    def test_get_lineages(self):
        lineages = helpers.get_lineages(self.top_male)
        lineage = lineages[self.top_male.pk]
        self.assertIn(self.generation_1[0], lineage)

        self.assertCacheContains('lineages:{}'.format(self.top_male.pk))
        self.assertCacheContains('lineage-objects:ancestor={}'.format(
            self.top_male.pk))

    def test_get_lineages_with_descendant(self):
        lineages = helpers.get_lineages(self.top_male, self.generation_extra[0])
        lineage = lineages[self.top_male.pk]
        self.assertIn(self.generation_1[1], lineage)

        self.assertCacheContains('lineages:{}:{}'.format(
            self.top_male.pk, self.generation_extra[0].pk))
        self.assertCacheContains('lineage-objects:ancestor={}:{}'.format(
            self.top_male.pk, self.generation_1[1].pk))

    def test_get_parents(self):
        parents = helpers.get_parents(
            descendant=self.generation_1[0],
            visible_ancestors=[self.generation_1[0], self.spouse_1]
        )
        result = list(parents.keys())
        expected = ['father', 'mother']
        self.assertEqual(result, expected)

    def test_get_parents_none_found(self):
        result = helpers.get_parents(
            descendant=self.top_male,
            visible_ancestors=[
                self.top_male, self.top_female, self.generation_1[0],
                self.spouse_1
            ]
        )
        self.assertIsNone(result)

    def test_get_parents_parent_in_visible_ancestors(self):
        result = helpers.get_parents(
            descendant=self.generation_1[0],
            visible_ancestors=[
                self.top_male, self.top_female, self.generation_1[0],
                self.spouse_1
            ]
        )
        self.assertIsNone(result)
