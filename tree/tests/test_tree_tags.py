from django.template import Context, RequestContext, Template
from pyquery import PyQuery

from tree import models
from tree.tests import factories
from tree.tests.testcases import TreeTestCase


class TestTreeTags(TreeTestCase):

    def setUp(self):
        super().setUp()
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

        self.lineages = (
            models.Lineage
            .objects
            .select_related('descendant')
            .in_bulk(field_name='ancestor_id')
        )

    def render(self, value, **kwargs):
        request = kwargs.get('request')
        context = RequestContext(kwargs) if request else Context(kwargs)
        template = Template('{% load tree_tags %}' + value)
        return template.render(context)

    def test_render_tree(self):
        lineage = self.top_male.get_lineage()
        output = self.render(
            '{% render_tree ancestor descendant %}',
            ancestor=self.top_male,
            descendant=self.generation_2[0],
            lineage=[
                generation.ancestor
                for generation in (
                    lineage.generations.select_related('ancestor').all()
                )
            ],
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

        result = doc.attr('class')
        expected = 'male'
        self.assertEqual(result, expected)

        result = doc.attr('data-url')
        expected = '/stamboom/john-glass-1812-1874/johnny-glass-1871-1952'
        self.assertEqual(result, expected)

        result = doc.text()
        expected = 'Martin Glass (1836 - 1901)'
        self.assertEqual(result, expected)

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

        result = doc.attr('data-url')
        self.assertIsNone(result)

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

        result = doc.attr('class')
        expected = 'female'
        self.assertEqual(result, expected)

        result = doc.attr('data-url')
        expected = '/stamboom/priscilla-glass-1840-1910/minny-friend-1888-1953'
        self.assertEqual(result, expected)

        result = doc.text()
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

        result = doc.attr('class')
        expected = 'male foo'
        self.assertEqual(result, expected)

    def test_render_ancestor_no_root_ancestor(self):
        output = self.render(
            '{% render_ancestor ancestor css_class=css_class %}',
            ancestor=self.generation_1[0],
            lineages=self.lineages
        )
        self.assertEqual(output, '')
