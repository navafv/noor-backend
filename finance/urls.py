from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeesReceiptViewSet, ExpenseViewSet
from .views_analytics import FinanceDashboardView
from .views_outstanding import OutstandingFeesViewSet

router = DefaultRouter()
router.register(r"receipts", FeesReceiptViewSet, basename="receipt")
router.register(r"expenses", ExpenseViewSet, basename="expense")

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/summary/", FinanceDashboardView.as_view(), name="finance-dashboard"),
    path("fees/outstanding/", OutstandingFeesViewSet.as_view({'get': 'list'}), name="outstanding-fees"),
]