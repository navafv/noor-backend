from rest_framework_nested import routers
from .views import StudentViewSet, StudentMeasurementViewSet

router = routers.DefaultRouter()
router.register(r"students", StudentViewSet, basename="student")

students_router = routers.NestedSimpleRouter(router, r'students', lookup='student')
students_router.register(r'measurements', StudentMeasurementViewSet, basename='student-measurements')

urlpatterns = router.urls + students_router.urls