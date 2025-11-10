"""
NEW FILE: stitching-backend/notifications/urls.py

This file registers all viewsets for the 'notifications' app.
"""
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = router.urls