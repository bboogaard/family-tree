from rest_framework.routers import SimpleRouter

from .views.lookup import LookupViewSet
from .views.search import SearchViewSet
from .views.tree import TreeViewSet


app_name = 'api'


router = SimpleRouter(trailing_slash=False)
router.register('search', SearchViewSet, basename='search')
router.register('trees', TreeViewSet, basename='trees')
router.register('lookup', LookupViewSet, basename='lookup')
urlpatterns = router.urls
