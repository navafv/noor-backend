"""
NEW FILE: stitching-backend/certificates/urls.py

This file registers all viewsets for the 'certificates' app.
"""
from rest_framework.routers import DefaultRouter
from .views import CertificateViewSet

router = DefaultRouter()
router.register(r"certificates", CertificateViewSet, basename="certificate")

urlpatterns = router.urls