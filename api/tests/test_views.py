from tree.tests.testcases import TreeViewTest


class TestTreeView(TreeViewTest):

    with_persistent_names = True

    def test_get(self):
        response = self.app.get('/api/v1/search/names')
        self.assertEqual(response.status_code, 200)

    def test_get_search(self):
        response = self.app.get('/api/v1/search/names?search=Johnny')
        self.assertEqual(response.status_code, 200)
        response.mustcontain('John Glass', 'Johnny Glass')
