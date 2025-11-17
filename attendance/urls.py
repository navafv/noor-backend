from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet
from .views_analytics import AttendanceAnalyticsView

router = DefaultRouter()
router.register(r"records", AttendanceViewSet, basename="attendance")

urlpatterns = [
    path("", include(router.urls)),
    path("analytics/summary/", AttendanceAnalyticsView.as_view(), name="attendance-analytics"),
]