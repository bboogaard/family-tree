import operator

from tree import models
from tree.tests.factories import LineageFactory
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


class TestAncestor(TreeTestCase):

    def setUp(self):
        super().setUp()
        self.top_male.refresh_from_db()

    def test_str(self):
        ancestor = self.top_male
        ancestor.firstname = 'John'
        ancestor.lastname = 'Doe'
        ancestor.save()

        result = str(ancestor)
        expected = 'John Doe'
        self.assertEqual(result, expected)

    def test_clean_set_has_expired(self):
        ancestor = self.top_male
        ancestor.has_expired = False
        ancestor.year_of_death = 1856
        ancestor.full_clean()

        result = ancestor.has_expired
        self.assertTrue(result)

    def test_clean_set_slug(self):
        ancestor = self.top_male
        ancestor.firstname = 'John'
        ancestor.lastname = 'Doe'
        ancestor.birthyear = 1812
        ancestor.year_of_death = 1874
        ancestor.full_clean()

        result = ancestor.slug
        expected = 'john-doe-1812-1874'
        self.assertEqual(result, expected)

    def test_clean_set_slug_slug_exists(self):
        self.generation_1[0].slug = 'john-doe-1812-1874'
        self.generation_1[0].save()

        ancestor = self.top_male
        ancestor.firstname = 'John'
        ancestor.lastname = 'Doe'
        ancestor.birthyear = 1812
        ancestor.year_of_death = 1874
        ancestor.full_clean()

        result = ancestor.slug
        expected = 'john-doe-1812-1874-1'
        self.assertEqual(result, expected)

        self.generation_1[0].refresh_from_db()

    def test_clean_set_slug_slug_exists_really_long_slug(self):
        self.generation_1[0].slug = (
            100 * 'a' + '-' + 100 * 'a' + '-' + 53 * 'a'
        )
        self.generation_1[0].save()

        ancestor = self.top_male
        ancestor.firstname = 100 * 'a'
        ancestor.middlename = 100 * 'a'
        ancestor.lastname = 100 * 'a'
        ancestor.birthyear = 1812
        ancestor.year_of_death = 1874
        ancestor.full_clean()

        result = ancestor.slug
        expected = 100 * 'a' + '-' + 100 * 'a' + '-' + 51 * 'a' + '-1'
        self.assertEqual(result, expected)

        self.generation_1[0].refresh_from_db()

    def test_natural_key(self):
        ancestor = self.top_male
        ancestor.slug = 'john-doe-1812-1874'

        result = ancestor.natural_key()
        expected = ('john-doe-1812-1874', )
        self.assertEqual(result, expected)

    def test_get_fullname(self):
        ancestor = self.top_male
        ancestor.firstname = 'John'
        ancestor.lastname = 'Doe'
        ancestor.save()

        result = ancestor.get_fullname()
        expected = 'John Doe'
        self.assertEqual(result, expected)

    def test_get_age(self):
        ancestor = self.top_male
        ancestor.birthyear = 1812
        ancestor.year_of_death = 1874

        result = ancestor.get_age()
        expected = '1812 - 1874'
        self.assertEqual(result, expected)

    def test_get_age_birthyear_expired(self):
        ancestor = self.top_male
        ancestor.birthyear = 1812
        ancestor.year_of_death = None
        ancestor.has_expired = True
        ancestor.save()

        result = ancestor.get_age()
        expected = '1812 - ????'
        self.assertEqual(result, expected)

    def test_get_age_birthyear_living(self):
        ancestor = self.top_male
        ancestor.birthyear = 1812
        ancestor.year_of_death = None
        ancestor.has_expired = False
        ancestor.save()

        result = ancestor.get_age()
        expected = '1812 -'
        self.assertEqual(result, expected)

    def test_get_age_year_of_death_only(self):
        ancestor = self.top_male
        ancestor.birthyear = None
        ancestor.year_of_death = 1874
        ancestor.has_expired = False
        ancestor.save()

        result = ancestor.get_age()
        expected = '???? - 1874'
        self.assertEqual(result, expected)

    def test_get_age_no_birthyear_no_year_of_death_expired(self):
        ancestor = self.top_male
        ancestor.birthyear = None
        ancestor.year_of_death = None
        ancestor.has_expired = True
        ancestor.save()

        result = ancestor.get_age()
        expected = '???? - ????'
        self.assertEqual(result, expected)

    def test_get_age_no_birthyear_no_year_of_death_living(self):
        ancestor = self.top_male
        ancestor.birthyear = None
        ancestor.year_of_death = None
        ancestor.has_expired = False
        ancestor.save()

        result = ancestor.get_age()
        expected = '???? -'
        self.assertEqual(result, expected)

    def test_get_age_different_placeholder(self):
        ancestor = self.top_male
        ancestor.birthyear = 1812
        ancestor.year_of_death = None
        ancestor.has_expired = True
        ancestor.save()

        result = ancestor.get_age('xxxx')
        expected = '1812 - xxxx'
        self.assertEqual(result, expected)

    def test_was_married_male(self):
        ancestor = self.top_male
        self.assertTrue(ancestor.was_married)

    def test_was_married_female(self):
        ancestor = self.top_female
        self.assertTrue(ancestor.was_married)

    def test_children_male(self):
        ancestor = self.top_male
        result = list(ancestor.children.all())
        expected = self.generation_1
        self.assertItemsEqual(result, expected)

    def test_children_female(self):
        ancestor = self.top_female
        result = list(ancestor.children.all())
        expected = self.generation_1
        self.assertItemsEqual(result, expected)

    def test_marriages_male(self):
        ancestor = self.top_male
        marriage = ancestor.marriages.first()
        result = marriage.wife
        expected = self.top_female
        self.assertEqual(result, expected)

    def test_marriages_female(self):
        ancestor = self.top_female
        marriage = ancestor.marriages.first()
        result = marriage.husband
        expected = self.top_male
        self.assertEqual(result, expected)

    def test_get_spouse_male(self):
        ancestor = self.top_male
        marriage = ancestor.marriages.first()
        result = ancestor.get_spouse(marriage)
        expected = self.top_female
        self.assertEqual(result, expected)

    def test_get_spouse_female(self):
        ancestor = self.top_female
        marriage = ancestor.marriages.first()
        result = ancestor.get_spouse(marriage)
        expected = self.top_male
        self.assertEqual(result, expected)

    def test_get_lineage(self):
        ancestor = self.top_male
        lineage = ancestor.get_lineage()
        result = lineage.descendant
        expected = self.generation_2[0]
        self.assertEqual(result, expected)

    def test_get_lineage_none(self):
        ancestor = self.generation_1[0]
        result = ancestor.get_lineage()
        self.assertIsNone(result)


class TestMarriage(TreeTestCase):

    def test_str(self):
        ancestor = self.top_male
        marriage = ancestor.marriages.first()
        result = str(marriage)
        expected = str(self.top_male) + ' x ' + str(self.top_female)
        self.assertEqual(result, expected)


class TestLineageQuerySet(TreeTestCase):

    with_persistent_names = True

    def test_for_ancestor(self):
        lineage = LineageFactory(
            ancestor=self.generation_1[1], descendant=self.generation_extra[0]
        )

        # Query count:
        # Generation query (1)
        # Children of father (1)
        # Marriages of husband (1)
        # Marriages of wife (1)

        with self.assertNumQueries(4):
            queryset = models.Lineage.objects.for_ancestor(self.top_male)
        result = list(queryset.order_by('id'))
        expected = sorted(
            [self.lineage, lineage], key=operator.attrgetter('id')
        )
        self.assertEqual(result, expected)


class TestLineage(TreeTestCase):

    def test_str(self):
        ancestor = self.top_male
        lineage = ancestor.get_lineage()
        result = str(lineage)
        expected = str(self.top_male) + ' > ' + str(self.generation_2[0])
        self.assertEqual(result, expected)
