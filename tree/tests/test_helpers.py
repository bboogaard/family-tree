import operator

from django.test import TestCase

from tree import helpers
from tree.tests import factories


class TestHelpers(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.top_male = factories.AncestorFactory(gender='m')
        cls.top_female = factories.AncestorFactory(gender='f')
        cls.generation_1 = [
            factories.AncestorFactory(
                gender='m', father=cls.top_male, mother=cls.top_female
            ),
            factories.AncestorFactory(
                gender='f', father=cls.top_male, mother=cls.top_female
            )
        ]
        factories.MarriageFactory(husband=cls.top_male, wife=cls.top_female)

        cls.spouse_1 = factories.AncestorFactory(gender='f')
        cls.generation_2 = [
            factories.AncestorFactory(
                gender='m', father=cls.generation_1[0], mother=cls.spouse_1
            ),
            factories.AncestorFactory(
                gender='f', father=cls.generation_1[0], mother=cls.spouse_1
            )
        ]
        factories.MarriageFactory(
            husband=cls.generation_1[0], wife=cls.spouse_1
        )

        cls.spouse_2 = factories.AncestorFactory(gender='m')
        cls.generation_extra = [
            factories.AncestorFactory(
                gender='m', mother=cls.generation_1[1], father=cls.spouse_2
            ),
            factories.AncestorFactory(
                gender='f', mother=cls.generation_1[1], father=cls.spouse_2
            )
        ]
        factories.MarriageFactory(
            wife=cls.generation_1[1], husband=cls.spouse_2
        )
        factories.LineageFactory(
            ancestor=cls.top_male, descendant=cls.generation_2[0]
        )

    def test_get_lineage(self):
        result = helpers.get_lineage(self.top_male, self.generation_2[0])
        expected = [
            self.top_male, self.top_female, self.generation_1[0], self.spouse_1
        ]
        self.assertEqual(
            sorted(result, key=operator.attrgetter('id')),
            sorted(expected, key=operator.attrgetter('id'))
        )

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
