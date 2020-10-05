from tree.tests import factories
from tree.tests.testcases import TreeViewTest


class TestTreeView(TreeViewTest):

    def setUp(self):
        super().setUp()
        self.top_male.is_root = True
        self.top_male.firstname = 'John'
        self.top_male.lastname = 'Glass'
        self.top_male.birthyear = 1812
        self.top_male.year_of_death = 1874
        self.top_male.slug = ''
        self.top_male.full_clean()
        self.top_male.save()

        self.top_female.firstname = 'Jane'
        self.top_female.lastname = 'Snyder'
        self.top_female.birthyear = 1824
        self.top_female.year_of_death = 1890
        self.top_female.slug = ''
        self.top_female.full_clean()
        self.top_female.save()

        self.generation_1[0].firstname = 'Martin'
        self.generation_1[0].lastname = 'Glass'
        self.generation_1[0].birthyear = 1836
        self.generation_1[0].year_of_death = 1901
        self.generation_1[0].slug = ''
        self.generation_1[0].full_clean()
        self.generation_1[0].save()

        self.generation_1[1].firstname = 'Priscilla'
        self.generation_1[1].lastname = 'Glass'
        self.generation_1[1].birthyear = 1840
        self.generation_1[1].year_of_death = 1910
        self.generation_1[1].slug = ''
        self.generation_1[1].full_clean()
        self.generation_1[1].save()

        self.spouse_1.firstname = 'Sylvia'
        self.spouse_1.lastname = 'Reed'
        self.spouse_1.birthyear = 1851
        self.spouse_1.year_of_death = 1920
        self.spouse_1.slug = ''
        self.spouse_1.full_clean()
        self.spouse_1.save()

        self.spouse_2.firstname = 'Donald'
        self.spouse_2.lastname = 'Friend'
        self.spouse_2.birthyear = 1860
        self.spouse_2.year_of_death = 1934
        self.spouse_2.slug = ''
        self.spouse_2.full_clean()
        self.spouse_2.save()

        self.generation_2[0].firstname = 'Johnny'
        self.generation_2[0].lastname = 'Glass'
        self.generation_2[0].birthyear = 1871
        self.generation_2[0].year_of_death = 1952
        self.generation_2[0].slug = ''
        self.generation_2[0].full_clean()
        self.generation_2[0].save()

        self.generation_2[1].firstname = 'Sylvia'
        self.generation_2[1].lastname = 'Glass'
        self.generation_2[1].birthyear = 1873
        self.generation_2[1].year_of_death = 1960
        self.generation_2[1].slug = ''
        self.generation_2[1].full_clean()
        self.generation_2[1].save()

        self.generation_extra[0].firstname = 'Minny'
        self.generation_extra[0].lastname = 'Friend'
        self.generation_extra[0].birthyear = 1888
        self.generation_extra[0].year_of_death = 1953
        self.generation_extra[0].slug = ''
        self.generation_extra[0].full_clean()
        self.generation_extra[0].save()

        self.generation_extra[1].firstname = 'Donald'
        self.generation_extra[1].lastname = 'Friend'
        self.generation_extra[1].birthyear = 1890
        self.generation_extra[1].year_of_death = 1961
        self.generation_extra[1].slug = ''
        self.generation_extra[1].full_clean()
        self.generation_extra[1].save()

        factories.LineageFactory(
            ancestor=self.generation_1[1], descendant=self.generation_extra[0]
        )

    def test_get(self):
        response = self.app.get('/stamboom/')
        self.assertEqual(response.status_code, 200)

    def test_get_root_ancestor(self):
        response = self.app.get('/stamboom/john-glass-1812-1874/')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.location, '/stamboom/')

    def test_get_root_ancestor_with_descendant(self):
        response = self.app.get(
            '/stamboom/john-glass-1812-1874/donald-friend-1890-1961')
        self.assertEqual(response.status_code, 200)

    def test_get_root_ancestor_with_descendant_from_lineage(self):
        response = self.app.get(
            '/stamboom/john-glass-1812-1874/johnny-glass-1871-1952')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.location, '/stamboom/')

    def test_get_ancestor(self):
        response = self.app.get(
            '/stamboom/priscilla-glass-1840-1910/'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_ancestor_with_descendant(self):
        response = self.app.get(
            '/stamboom/priscilla-glass-1840-1910/donald-friend-1890-1961'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_ancestor_with_descendant_from_lineage(self):
        response = self.app.get(
            '/stamboom/priscilla-glass-1840-1910/minny-friend-1888-1953'
        )
        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response.location, '/stamboom/priscilla-glass-1840-1910/')

    def test_get_root_ancestor_not_found(self):
        self.top_male.is_root = False
        self.top_male.save()

        response = self.app.get('/stamboom/', expect_errors=True)
        self.assertEqual(response.status_code, 404)

    def test_get_ancestor_not_found(self):
        response = self.app.get(
            '/stamboom/priscilla-glass-1839-1910/', expect_errors=True
        )
        self.assertEqual(response.status_code, 404)

    def test_get_root_ancestor_no_lineage(self):
        self.top_male.lineage.delete()

        response = self.app.get('/stamboom/', expect_errors=True)
        self.assertEqual(response.status_code, 404)

        factories.LineageFactory(
            ancestor=self.top_male, descendant=self.generation_2[0]
        )

    def test_get_ancestor_no_lineage(self):
        response = self.app.get(
            '/stamboom/martin-glass-1836-1901/', expect_errors=True)
        self.assertEqual(response.status_code, 404)

    def test_get_root_ancestor_with_descendant_not_found(self):
        response = self.app.get(
            '/stamboom/john-glass-1812-1874/donald-friend-1889-1961',
            expect_errors=True)
        self.assertEqual(response.status_code, 404)

    def test_get_ancestor_with_descendant_not_found(self):
        response = self.app.get(
            '/stamboom/priscilla-glass-1840-1910/donald-friend-1889-1961',
            expect_errors=True
        )
        self.assertEqual(response.status_code, 404)
