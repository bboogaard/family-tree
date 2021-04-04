from rest_framework.routers import SimpleRouter

from .views.search import SearchViewSet


router = SimpleRouter(trailing_slash=False)
router.register('search', SearchViewSet, basename='search')
urlpatterns = router.urls
