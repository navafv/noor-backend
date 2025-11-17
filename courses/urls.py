from rest_framework_nested import routers
from .views import (
    CourseViewSet, EnrollmentViewSet,
    CourseMaterialViewSet, StudentMaterialsViewSet
)

router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")

router.register(r"my-materials", StudentMaterialsViewSet, basename="my-materials")

courses_router = routers.NestedSimpleRouter(router, r'courses', lookup='course')
courses_router.register(r'materials', CourseMaterialViewSet, basename='course-materials')

urlpatterns = router.urls + courses_router.urls