from tree.tests import factories
from tree.tests.testcases import TreeViewTest


class TestTreeView(TreeViewTest):

    with_persistent_names = True

    def setUp(self):
        super().setUp()
        factories.LineageFactory(
            ancestor=self.generation_1[1], descendant=self.generation_extra[0]
        )

    def test_get(self):
        response = self.app.get('/stamboom/')
        self.assertEqual(response.status_code, 200)

    def test_get_root_ancestor(self):
        response = self.app.get('/stamboom/john-glass-1812-1874')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.location, '/stamboom/')

    def test_get_ancestor(self):
        response = self.app.get(
            '/stamboom/priscilla-glass-1840-1910'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_root_ancestor_not_found(self):
        self.top_male.is_root = False
        self.top_male.save()

        response = self.app.get('/stamboom/', expect_errors=True)
        self.assertEqual(response.status_code, 404)

    def test_get_ancestor_not_found(self):
        response = self.app.get(
            '/stamboom/priscilla-glass-1839-1910', expect_errors=True
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
            '/stamboom/martin-glass-1836-1901', expect_errors=True)
        self.assertEqual(response.status_code, 404)
