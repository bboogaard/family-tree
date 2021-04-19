import mock

from lib.api import requests
from scraper.tests.factories import PageFactory
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
        response = self.app.get('/stamboom/john-glass-1812-1874/')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.location, '/stamboom/')

    def test_get_ancestor(self):
        response = self.app.get(
            '/stamboom/priscilla-glass-1840-1910/'
        )
        self.assertEqual(response.status_code, 200)

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

    @mock.patch.object(requests, 'post')
    def test_create_tree(self, mock_post):
        mock_response = mock.Mock(status_code=201)
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        response = self.app.get(
            '/tree/create/{}'.format(self.generation_2[0].pk),
            user=self.test_user
        )
        form = response.form
        result = list(
            map(int, filter(None, [ancestor_id for ancestor_id, _, _ in form['ancestor_id'].options]))
        )
        expected = [self.top_female.pk, self.spouse_1.pk]
        self.assertEqual(result, expected)

        form['ancestor_id'] = self.top_female.pk
        response = form.submit()
        self.assertEqual(response.status_code, 302)

    def test_create_tree_with_form_errors(self):
        response = self.app.get(
            '/tree/create/{}'.format(self.generation_2[0].pk),
            user=self.test_user
        )
        form = response.form
        response = form.submit()
        self.assertEqual(response.status_code, 200)

    @mock.patch.object(requests, 'get')
    def test_run_task(self, mock_get):
        mock_response = mock.Mock(status_code=200)
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        response = self.app.get(
            '/task/run',
            user=self.test_user
        )
        form = response.form
        result = list(
            filter(None, [command for command, _, _ in form['command'].options])
        )
        expected = ['scrape_page']
        self.assertEqual(result, expected)

        form['command'].value = 'scrape_page'
        form['query_string'] = 'page=1'
        response = form.submit()
        self.assertEqual(response.status_code, 302)

    def test_run_task_with_form_error(self):
        response = self.app.get(
            '/task/run',
            user=self.test_user
        )
        form = response.form
        response = form.submit()
        self.assertEqual(response.status_code, 200)

    def test_run_task_with_prefill(self):
        response = self.app.get(
            '/task/run?command=scrape_page&query_string=page=1',
            user=self.test_user
        )
        form = response.form
        result = [selected for _, selected, _ in form['command'].options]
        expected = [False, True]
        self.assertEqual(result, expected)

        result = form['query_string'].value
        expected = 'page=1'
        self.assertEqual(result, expected)

    def test_task_helper(self):
        response = self.app.get(
            '/task/helper/scrape_page',
            user=self.test_user
        )
        form = response.form
        form['page_id-hidden'] = '1'
        response = form.submit()
        self.assertEqual(response.status_code, 302)

    def test_task_helper_with_form_error(self):
        response = self.app.get(
            '/task/helper/scrape_page',
            user=self.test_user
        )
        form = response.form
        response = form.submit()
        self.assertEqual(response.status_code, 200)

    def test_task_helper_with_prefilled(self):
        PageFactory(pk=1, name='John Glass')
        response = self.app.get(
            '/task/helper/scrape_page?page_id=1',
            user=self.test_user
        )

        form = response.form
        result = form['page_id-hidden'].value
        expected = '1'
        self.assertEqual(result, expected)

    def test_get_preview(self):
        response = self.app.get(
            '/tree/preview/john-glass-1812-1874/priscilla-glass-1840-1910',
            user=self.test_user
        )
        self.assertEqual(response.status_code, 200)

    def test_get_preview_not_logged_in(self):
        response = self.app.get(
            '/tree/preview/john-glass-1812-1874/priscilla-glass-1840-1910'
        )
        self.assertEqual(response.status_code, 302)

    def test_get_preview_descendant_not_found(self):
        response = self.app.get(
            '/tree/preview/john-glass-1812-1874/priscilla-glass-1839-1910',
            user=self.test_user,
            expect_errors=True
        )
        self.assertEqual(response.status_code, 404)

    def test_get_bio(self):
        response = self.app.get(
            '/stamboom/john-glass-1812-1874/persoonlijke-gegevens',
            expect_errors=True
        )
        self.assertEqual(response.status_code, 200)

    def test_get_bio_with_bio(self):
        factories.BioFactory(
            details='1: Foo\n2: Bar',
            ancestor=self.top_male,
            links=[
                ('/path/to/link/1', 'Link text 1'),
                ('/path/to/link/2', 'Link text 2')
            ]
        )
        response = self.app.get(
            '/stamboom/john-glass-1812-1874/persoonlijke-gegevens')
        self.assertEqual(response.status_code, 200)
        response.mustcontain(
            '<dd>1: Foo</dd>',
            '<dd>2: Bar</dd>',
            '<a href="/path/to/link/1" target="_blank">Link text 1</a>',
            '<a href="/path/to/link/2" target="_blank">Link text 2</a>'
        )

    def test_version(self):
        response = self.app.get('/stamboom/about')
        self.assertEqual(response.status_code, 200)
