from rest_framework_nested import routers
from .views import StudentViewSet, StudentMeasurementViewSet

# Main router
router = routers.DefaultRouter()
router.register(r"students", StudentViewSet, basename="student")

# Nested router for: /students/<student_pk>/measurements/
students_router = routers.NestedSimpleRouter(router, r'students', lookup='student')
students_router.register(r'measurements', StudentMeasurementViewSet, basename='student-measurements')

# Combine the URL patterns
urlpatterns = router.urls + students_router.urls