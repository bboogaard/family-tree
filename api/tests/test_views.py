from tree.tests.testcases import TreeViewTest


class TestSearchNamesView(TreeViewTest):

    with_persistent_names = True

    def test_get(self):
        response = self.app.get('/api/v1/search/names')
        self.assertEqual(response.status_code, 200)

    def test_get_search(self):
        response = self.app.get('/api/v1/search/names?name=Johnny')
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
        response = self.app.get('/api/v1/search/text?text=Newtown')
        self.assertEqual(response.status_code, 200)
        response.mustcontain('John Glass', 'Martin Glass')


class TestSearchAncestorView(TreeViewTest):

    with_persistent_names = True

    def test_get(self):
        response = self.app.get('/api/v1/search/ancestors')
        self.assertEqual(response.status_code, 200)

    def test_get_search(self):
        response = self.app.get('/api/v1/search/ancestors?lastname=snyder')
        self.assertEqual(response.status_code, 200)
        response.mustcontain('Jane Snyder')


class TestTreeView(TreeViewTest):

    with_persistent_names = True

    def test_create(self):
        response = self.app.get('/api/v1/trees/{}/create'.format(
            self.generation_2[0].pk
        ), user=self.test_user)
        form = response.form
        result = list(map(int, [val for val, _, _ in form['ancestor_id'].options]))
        expected = [self.top_male.pk, self.top_female.pk, self.spouse_1.pk]
        self.assertEqual(result, expected)
        form['ancestor_id'].value = self.top_female.pk
        response = form.submit()
        self.assertEqual(response.status_code, 302)
        lineage = self.top_female.get_lineage()
        self.assertIsNotNone(lineage)
        result = lineage.descendant
        expected = self.generation_2[0]
        self.assertEqual(result, expected)

    def test_create_exists(self):
        response = self.app.get('/api/v1/trees/{}/create'.format(
            self.generation_2[0].pk
        ), user=self.test_user)
        form = response.form
        response = form.submit(expect_errors=True)
        self.assertEqual(response.status_code, 400)
