"""
URL configuration for the 'finance' app.

Registers all finance-related ViewSets, including core models,
analytics, and outstanding fee calculators.
"""

from rest_framework.routers import DefaultRouter
from .views import (
    FeesReceiptViewSet, ExpenseViewSet, StudentReceiptsViewSet
)
from .views_analytics import FinanceAnalyticsViewSet
from .views_outstanding import OutstandingFeesViewSet

router = DefaultRouter()
router.register("receipts", FeesReceiptViewSet, basename="fees-receipt")
router.register("expenses", ExpenseViewSet, basename="expense")
router.register("my-receipts", StudentReceiptsViewSet, basename="my-receipts")
router.register("analytics", FinanceAnalyticsViewSet, basename="finance-analytics")
router.register("outstanding", OutstandingFeesViewSet, basename="finance-outstanding")

urlpatterns = router.urls