from django.template import Context, RequestContext, Template
from pyquery import PyQuery

from tree import helpers, models
from tree.tests import factories
from tree.tests.testcases import TreeTestCase


class TestTreeTags(TreeTestCase):

    with_persistent_names = True

    def setUp(self):
        super().setUp()
        self.lineages = helpers.get_lineages(self.top_male)

    def render(self, value, **kwargs):
        request = kwargs.get('request')
        context = RequestContext(kwargs) if request else Context(kwargs)
        template = Template('{% load tree_tags %}' + value)
        return template.render(context)

    def test_render_tree(self):
        output = self.render(
            '{% render_tree ancestor %}',
            ancestor=self.top_male,
            root_ancestor=self.top_male,
            lineages=self.lineages
        )
        doc = PyQuery(output)
        marriages = doc.find('.marriage')
        self.assertEqual(len(marriages), 2)

        marriage = PyQuery(marriages[0])
        result = ' '.join(marriage.text().split('\n'))
        expected = 'John Glass (1812 - 1874) x Jane Snyder (1824 - 1890)'
        self.assertEqual(result, expected)

        marriage = PyQuery(marriages[1])
        result = ' '.join(marriage.text().split('\n'))
        expected = 'Martin Glass (1836 - 1901) x Sylvia Reed (1851 - 1920)'
        self.assertEqual(result, expected)

        children = doc.find('ul li')
        self.assertEqual(len(children), 4)

        child = PyQuery(children[0])
        self.assertIn('Martin Glass (1836 - 1901)', child.text())

        child = PyQuery(children[1])
        result = child.text()
        expected = 'Johnny Glass (1871 - 1952)'
        self.assertEqual(result, expected)

        child = PyQuery(children[2])
        result = child.text()
        expected = 'Sylvia Glass (1873 - 1960)'
        self.assertEqual(result, expected)

        child = PyQuery(children[3])
        result = child.text()
        expected = 'Priscilla Glass (1840 - 1910)'
        self.assertEqual(result, expected)

    def test_render_ancestor(self):
        output = self.render(
            '{% render_ancestor ancestor %}',
            ancestor=self.generation_1[0],
            root_ancestor=self.top_male,
            lineages=self.lineages
        )
        doc = PyQuery(output)
        element = PyQuery(doc.find('.male'))

        result = element.text()
        expected = 'Martin Glass (1836 - 1901)'
        self.assertEqual(result, expected)

        element = PyQuery(
            doc.find('#meta-ancestor-{}'.format(self.generation_1[0].pk))
        )
        self.assertIn('/stamboom/john-glass-1812-1874', element.html())

    def test_render_ancestor_parent_visible(self):
        output = self.render(
            '{% render_ancestor ancestor %}',
            ancestor=self.generation_1[0],
            root_ancestor=self.top_male,
            flat_ancestors=[self.top_male],
            lineages=self.lineages
        )
        doc = PyQuery(output)

        result = doc.attr('class')
        expected = 'male'
        self.assertEqual(result, expected)

        result = doc.text()
        expected = 'Martin Glass (1836 - 1901)'
        self.assertEqual(result, expected)

    def test_render_ancestor_different_lineage(self):
        factories.LineageFactory(
            ancestor=self.generation_1[1],
            descendant=self.generation_extra[0]
        )

        lineages = (
            models.Lineage
            .objects
            .select_related('descendant')
            .in_bulk(field_name='ancestor_id')
        )

        output = self.render(
            '{% render_ancestor ancestor %}',
            ancestor=self.generation_1[1],
            root_ancestor=self.top_male,
            lineages=lineages
        )
        doc = PyQuery(output)
        element = PyQuery(doc.find('.female'))

        result = element.attr('data-url')
        expected = '/stamboom/priscilla-glass-1840-1910/'
        self.assertEqual(result, expected)

        result = element.text()
        expected = 'Priscilla Glass (1840 - 1910)'
        self.assertEqual(result, expected)

    def test_render_ancestor_with_css_class(self):
        output = self.render(
            '{% render_ancestor ancestor css_class=css_class %}',
            ancestor=self.generation_1[0],
            root_ancestor=self.top_male,
            css_class='foo',
            lineages=self.lineages
        )
        doc = PyQuery(output)
        element = PyQuery(doc.find('.male'))

        result = element.attr('class')
        expected = 'male foo'
        self.assertEqual(result, expected)

    def test_render_ancestor_no_root_ancestor(self):
        output = self.render(
            '{% render_ancestor ancestor css_class=css_class %}',
            ancestor=self.generation_1[0],
            lineages=self.lineages
        )
        self.assertEqual(output, '')

    def test_render_bio(self):
        factories.BioFactory(
            details='1: Foo\n2: Bar',
            ancestor=self.top_male
        )
        output = self.render('{% render_bio ancestor %}', ancestor=self.top_male)

        doc = PyQuery(output)
        lst = PyQuery(doc.find('dd'))
        self.assertEqual(len(lst), 5)
