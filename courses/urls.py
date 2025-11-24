from rest_framework import routers
from .views import CourseViewSet, EnrollmentViewSet

router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")

urlpatterns = router.urls