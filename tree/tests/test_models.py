from tree import models
from tree.tests.testcases import TreeTestCase


class TestAncestorQuerySet(TreeTestCase):

    def test_get_by_natural_key(self):
        ancestor = self.top_male
        ancestor.slug = 'top-male'
        ancestor.save()

        result = models.Ancestor.objects.get_by_natural_key('top-male')
        expected = self.top_male
        self.assertEqual(result, expected)

        self.top_male.refresh_from_db()

    def test_get_by_parent(self):
        parent = self.top_male

        result = models.Ancestor.objects.by_parent(parent)
        expected = self.generation_1
        self.assertItemsEqual(result, expected)

    def test_with_children(self):
        result = models.Ancestor.objects.with_children()
        expected = [
            self.top_male, self.top_female, self.generation_1[0],
            self.spouse_1, self.generation_1[1], self.spouse_2
        ]
        self.assertItemsEqual(result, expected)

    def test_order_by_age(self):
        children = self.generation_1
        children[0].birthyear = 1812
        children[0].year_of_death = 1874
        children[0].save()

        children[1].birthyear = None
        children[1].year_of_death = 1856
        children[1].save()

        result = list(
            models.Ancestor.objects.filter(father=self.top_male).order_by_age()
        )
        expected = [children[1], children[0]]
        self.assertEqual(result, expected)

        children[0].refresh_from_db()
        children[1].refresh_from_db()
