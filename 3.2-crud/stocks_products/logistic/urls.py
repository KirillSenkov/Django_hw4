from rest_framework.routers import DefaultRouter

from logistic.views import ProductModelViewSet, StockViewSet

router = DefaultRouter()
router.register('products', ProductModelViewSet)
router.register('stocks', StockViewSet)

urlpatterns = router.urls
