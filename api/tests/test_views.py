from tree.tests.testcases import TreeViewTest


class TestSearchNamesView(TreeViewTest):

    with_persistent_names = True

    def test_get(self):
        response = self.app.get('/api/v1/search/names')
        self.assertEqual(response.status_code, 200)

    def test_get_search(self):
        response = self.app.get('/api/v1/search/names?search=Johnny')
        self.assertEqual(response.status_code, 200)
        response.mustcontain('John Glass', 'Johnny Glass')


class TestSearchTextView(TreeViewTest):

    with_persistent_names = True

    def setUp(self):
        super().setUp()
        self.top_male.birthplace = 'Oldtown'
        self.top_male.place_of_death = 'Newtown'
        self.top_male.save()

        self.generation_1[0].birthplace = 'Newtown'
        self.generation_1[0].place_of_death = 'Newtown'
        self.generation_1[0].save()

    def test_get(self):
        response = self.app.get('/api/v1/search/text')
        self.assertEqual(response.status_code, 200)

    def test_get_search(self):
        response = self.app.get('/api/v1/search/text?search=Newtown')
        self.assertEqual(response.status_code, 200)
        response.mustcontain('John Glass', 'Martin Glass')
