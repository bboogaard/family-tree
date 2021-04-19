import mock

from api import tasks
from scraper.tests.factories import PageFactory
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
        data = {
            'ancestor_id': self.top_female.pk,
            'descendant_id': self.generation_2[0].pk
        }
        response = self.post_secure('/api/v1/trees', data)
        self.assertEqual(response.status_code, 201)
        lineage = self.top_female.get_lineage()
        self.assertIsNotNone(lineage)
        result = lineage.descendant
        expected = self.generation_2[0]
        self.assertEqual(result, expected)

    def test_create_exists(self):
        data = {
            'ancestor_id': self.top_male.pk,
            'descendant_id': self.generation_2[0].pk
        }
        response = self.post_secure('/api/v1/trees', data, expect_errors=True)
        self.assertEqual(response.status_code, 409)


class TestLookupView(TreeViewTest):

    with_persistent_names = True

    def test_list(self):
        PageFactory(name='John Glass')
        response = self.app.get('/api/v1/lookup/page?q=glass')
        self.assertEqual(response.status_code, 200)
        response.mustcontain('John Glass')

    def test_list_with_ancestor(self):
        PageFactory(name='John Glass', ancestor=self.generation_2[0])
        response = self.app.get('/api/v1/lookup/page?q=glass')
        self.assertEqual(response.status_code, 200)
        response.mustcontain('Johnny Glass')


@mock.patch.object(tasks, 'call_command')
class TestTaskView(TreeViewTest):

    def test_run_command(self, mock_call):
        data = {
            'page_id': 1,
            'depth': 2,
            'direction': 'down'
        }
        response = self.get_secure('/api/v1/tasks/scrape_page', data)
        self.assertEqual(response.status_code, 200)
        command = mock_call.call_args[0][0]
        self.assertEqual(command, 'scrape_page')
        page_id = mock_call.call_args[0][1]
        self.assertEqual(page_id, 1)
        depth = mock_call.call_args[1]['depth']
        self.assertEqual(depth, 2)
        direction = mock_call.call_args[1]['direction']
        self.assertEqual(direction, 'down')

    def test_run_command_with_validation_errors(self, mock_call):
        data = {
            'page_id': 'foo',
            'depth': 2,
            'direction': 'down'
        }
        response = self.get_secure('/api/v1/tasks/scrape_page', data, expect_errors=True)
        self.assertEqual(response.status_code, 400)

    def test_run_command_with_command_error(self, mock_call):
        data = {}
        response = self.get_secure('/api/v1/tasks/foo', data, expect_errors=True)
        self.assertEqual(response.status_code, 400)
