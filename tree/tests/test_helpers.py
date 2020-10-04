import operator

from django.test import TestCase

from tree import helpers
from tree.tests import factories


class TestHelpers(TestCase):

    def test_get_lineage(self):
        top_male = factories.AncestorFactory(gender='m')
        top_female = factories.AncestorFactory(gender='f')
        generation_1 = [
            factories.AncestorFactory(
                gender='m', father=top_male, mother=top_female
            ),
            factories.AncestorFactory(
                gender='f', father=top_male, mother=top_female
            )
        ]
        factories.MarriageFactory(husband=top_male, wife=top_female)

        spouse_1 = factories.AncestorFactory(gender='f')
        generation_2 = [
            factories.AncestorFactory(
                gender='m', father=generation_1[0], mother=spouse_1
            ),
            factories.AncestorFactory(
                gender='f', father=generation_1[0], mother=spouse_1
            )
        ]
        factories.MarriageFactory(husband=generation_1[0], wife=spouse_1)

        spouse_2 = factories.AncestorFactory(gender='m')
        generation_extra = [
            factories.AncestorFactory(
                gender='m', mother=generation_1[1], father=spouse_2
            ),
            factories.AncestorFactory(
                gender='f', mother=generation_1[1], father=spouse_2
            )
        ]
        factories.MarriageFactory(wife=generation_1[1], husband=spouse_2)
        factories.LineageFactory(ancestor=top_male, descendant=generation_2[0])

        result = helpers.get_lineage(top_male, generation_2[0])
        expected = [top_male, top_female, generation_1[0], spouse_1]
        self.assertEqual(
            sorted(result, key=operator.attrgetter('id')),
            sorted(expected, key=operator.attrgetter('id'))
        )
