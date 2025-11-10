"""
UPDATED FILE: stitching-backend/students/urls.py

This file now correctly implements the nested route for measurements
using `rest_framework_nested`.
"""
from rest_framework_nested import routers
from .views import EnquiryViewSet, StudentViewSet, StudentMeasurementViewSet

# Main router
router = routers.DefaultRouter()
router.register(r"enquiries", EnquiryViewSet, basename="enquiry")
router.register(r"students", StudentViewSet, basename="student")

# Nested router for /students/<student_pk>/measurements/
students_router = routers.NestedSimpleRouter(router, r'students', lookup='student')
students_router.register(r'measurements', StudentMeasurementViewSet, basename='student-measurements')

# Combine the URL patterns
urlpatterns = router.urls + students_router.urls