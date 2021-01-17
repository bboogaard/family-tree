from django.contrib.admin.sites import AdminSite
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from tree.admin import LineageAdmin
from tree.models import Lineage
from tree.tests.testcases import TreeTestCase


class MockRequest:
    pass


class MockSuperUser:
    def has_perm(self, perm, obj=None):
        return True


request = MockRequest()
request.user = MockSuperUser()


class TestLineageAdmin(TreeTestCase):

    def setUp(self):
        super().setUp()
        self.site = AdminSite()

    def test_clear_caches(self):
        cache.add('lineages:{}'.format(self.lineage.ancestor_id), 'foo')
        cache.add(
            'lineage-objects:ancestor={}'.format(self.lineage.ancestor_id),
            'foo'
        )
        cache.add(
            make_template_fragment_key('tree', [self.lineage.ancestor_id]), ''
        )
        ma = LineageAdmin(Lineage, self.site)
        ma.clear_caches(request, Lineage.objects.filter(pk=self.lineage.pk))
        self.assertCacheNotContains(
            'lineages:{}'.format(self.lineage.ancestor_id)
        )
        self.assertCacheNotContains(
            'lineage-objects:ancestor={}'.format(self.lineage.ancestor_id)
        )
        self.assertCacheNotContains(
            make_template_fragment_key('tree', [self.lineage.ancestor_id])
        )
