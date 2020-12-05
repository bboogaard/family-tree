from django_webtest import WebTest
from django.core.cache import cache
from django.test import TestCase

from lib.testing.mixins import AssertsMixin
from tree.tests import factories


missing = object()


class TreeTestCase(AssertsMixin, TestCase):

    with_persistent_names = False

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
        cls.lineage = factories.LineageFactory(
            ancestor=cls.top_male, descendant=cls.generation_2[0]
        )

    def setUp(self):
        super().setUp()
        if self.with_persistent_names:
            self._setup_names()
        cache.clear()

    def _setup_names(self):
        self.top_male.refresh_from_db()
        self.top_male.firstname = 'John'
        self.top_male.lastname = 'Glass'
        self.top_male.birthyear = 1812
        self.top_male.year_of_death = 1874
        self.top_male.slug = ''
        self.top_male.full_clean()
        self.top_male.save()

        self.top_female.refresh_from_db()
        self.top_female.firstname = 'Jane'
        self.top_female.lastname = 'Snyder'
        self.top_female.birthyear = 1824
        self.top_female.year_of_death = 1890
        self.top_female.slug = ''
        self.top_female.full_clean()
        self.top_female.save()

        self.generation_1[0].refresh_from_db()
        self.generation_1[0].firstname = 'Martin'
        self.generation_1[0].lastname = 'Glass'
        self.generation_1[0].birthyear = 1836
        self.generation_1[0].year_of_death = 1901
        self.generation_1[0].slug = ''
        self.generation_1[0].full_clean()
        self.generation_1[0].save()

        self.generation_1[1].refresh_from_db()
        self.generation_1[1].firstname = 'Priscilla'
        self.generation_1[1].lastname = 'Glass'
        self.generation_1[1].birthyear = 1840
        self.generation_1[1].year_of_death = 1910
        self.generation_1[1].slug = ''
        self.generation_1[1].full_clean()
        self.generation_1[1].save()

        self.spouse_1.refresh_from_db()
        self.spouse_1.firstname = 'Sylvia'
        self.spouse_1.lastname = 'Reed'
        self.spouse_1.birthyear = 1851
        self.spouse_1.year_of_death = 1920
        self.spouse_1.slug = ''
        self.spouse_1.full_clean()
        self.spouse_1.save()

        self.spouse_2.refresh_from_db()
        self.spouse_2.firstname = 'Donald'
        self.spouse_2.lastname = 'Friend'
        self.spouse_2.birthyear = 1860
        self.spouse_2.year_of_death = 1934
        self.spouse_2.slug = ''
        self.spouse_2.full_clean()
        self.spouse_2.save()

        self.generation_2[0].refresh_from_db()
        self.generation_2[0].firstname = 'Johnny'
        self.generation_2[0].lastname = 'Glass'
        self.generation_2[0].birthyear = 1871
        self.generation_2[0].year_of_death = 1952
        self.generation_2[0].slug = ''
        self.generation_2[0].full_clean()
        self.generation_2[0].save()

        self.generation_2[1].refresh_from_db()
        self.generation_2[1].firstname = 'Sylvia'
        self.generation_2[1].lastname = 'Glass'
        self.generation_2[1].birthyear = 1873
        self.generation_2[1].year_of_death = 1960
        self.generation_2[1].slug = ''
        self.generation_2[1].full_clean()
        self.generation_2[1].save()

        self.generation_extra[0].refresh_from_db()
        self.generation_extra[0].firstname = 'Minny'
        self.generation_extra[0].lastname = 'Friend'
        self.generation_extra[0].birthyear = 1888
        self.generation_extra[0].year_of_death = 1953
        self.generation_extra[0].slug = ''
        self.generation_extra[0].full_clean()
        self.generation_extra[0].save()

        self.generation_extra[1].refresh_from_db()
        self.generation_extra[1].firstname = 'Donald'
        self.generation_extra[1].lastname = 'Friend'
        self.generation_extra[1].birthyear = 1890
        self.generation_extra[1].year_of_death = 1961
        self.generation_extra[1].slug = ''
        self.generation_extra[1].full_clean()
        self.generation_extra[1].save()

    @staticmethod
    def assertCacheContains(key):
        try:
            assert cache.get_entry(key, missing) is not missing, "Cache does not contain key {}".format(key)
        except AttributeError:
            pass

    @staticmethod
    def assertCacheNotContains(key):
        try:
            assert cache.get_entry(key, missing) is missing, "Cache unexpectedly contains key {}".format(key)
        except AttributeError:
            pass

    @staticmethod
    def assertCacheValueEquals(key, value):
        try:
            assert cache.get_entry(key, missing) == value, "Cache value does not equal {}".format(value)
        except AttributeError:
            pass


class TreeViewTest(WebTest, TreeTestCase):
    pass
