from django_webtest import WebTest
from django.test import TestCase

from lib.testing.mixins import AssertsMixin
from tree.tests import factories


class TreeTestCase(AssertsMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.top_male = factories.AncestorFactory(gender='m', is_root=True)
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


class TreeViewTest(WebTest, TreeTestCase):
    pass
