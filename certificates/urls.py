from rest_framework.routers import DefaultRouter
from .views import CertificateViewSet, StudentCertificateViewSet

router = DefaultRouter()
router.register(r"certificates", CertificateViewSet, basename="certificate")
router.register(r"my-certificates", StudentCertificateViewSet, basename="my-certificates")

urlpatterns = router.urls