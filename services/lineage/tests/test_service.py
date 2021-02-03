from services.lineage.service import LineageService
from tree.tests.factories import AncestorFactory, LineageFactory, MarriageFactory
from tree.tests.testcases import TreeTestCase


class TestLineageService(TreeTestCase):

    def setUp(self):
        super().setUp()
        self.service = LineageService()

    def test_find_root_for_lineage(self):
        result = self.service.find_root(self.top_male)
        expected = self.top_male
        self.assertEqual(result, expected)

    def test_find_root_for_spouse(self):
        result = self.service.find_root(self.spouse_1)
        expected = self.top_male
        self.assertEqual(result, expected)

    def test_find_root_in_lineage(self):
        result = self.service.find_root(self.generation_1[0])
        expected = self.top_male
        self.assertEqual(result, expected)

    def test_find_root_for_father(self):
        ancestor = AncestorFactory(
            gender='f', mother=None, father=self.generation_1[0],
            firstname='Mary'
        )
        result = self.service.find_root(ancestor)
        expected = self.top_male
        self.assertEqual(result, expected)

    def test_find_root_for_mother(self):
        ancestor = AncestorFactory(
            gender='f', mother=self.generation_1[1], father=None,
            firstname='Mary'
        )
        result = self.service.find_root(ancestor)
        expected = self.top_male
        self.assertEqual(result, expected)

    def test_find_root_multiple_lineages(self):
        spouse = AncestorFactory(gender='f')
        generation_3 = [
            AncestorFactory(
                gender='m', father=self.generation_2[0], mother=spouse,
                firstname='David'
            )
        ]
        MarriageFactory(
            husband=self.generation_2[0], wife=spouse
        )
        spouse = AncestorFactory(gender='f')
        generation_4 = [
            AncestorFactory(
                gender='m', father=generation_3[0], mother=spouse,
                firstname='Don'
            )
        ]
        MarriageFactory(
            husband=generation_3[0], wife=spouse
        )
        spouse = AncestorFactory(gender='f')
        generation_5 = [
            AncestorFactory(
                gender='m', father=generation_4[0], mother=spouse,
                firstname='Fred'
            )
        ]
        MarriageFactory(
            husband=generation_4[0], wife=spouse
        )
        LineageFactory(
            ancestor=self.top_female,
            descendant=generation_4[0]
        )
        LineageFactory(
            ancestor=self.generation_1[0],
            descendant=generation_5[0]
        )
        result = self.service.find_root(generation_3[0])
        expected = self.generation_1[0]
        self.assertEqual(result, expected)
