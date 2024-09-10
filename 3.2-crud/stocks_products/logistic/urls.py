from rest_framework.routers import DefaultRouter

from logistic.views import ProductModelViewSet, StockModelViewSet

router = DefaultRouter()
router.register('products', ProductModelViewSet)
router.register('stocks', StockModelViewSet)

urlpatterns = router.urls
