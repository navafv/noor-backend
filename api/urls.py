"""
UPDATED FILE: stitching-backend/api/urls.py

This file is the single source of truth for all v1 API routes.
It has been refactored to use `include()` to delegate routing to each
app's `urls.py` file. This is cleaner and more maintainable than
registering all viewsets here.
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import health_check

urlpatterns = [
    # 1. Authentication
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # 2. Health Check
    path("health/", health_check, name="health-check"),
    
    # 3. App-level URLs
    # Includes: /roles/, /users/, /users/me/
    path("", include("accounts.urls")),
    
    # Includes: /enquiries/, /students/, /students/<id>/measurements/
    path("", include("students.urls")),
    
    # Includes: /courses/, /trainers/, /batches/, /enrollments/, /feedback/
    path("", include("courses.urls")),
    
    # Includes: /certificates/, /certificates/verify/<hash>/
    path("", include("certificates.urls")),
    
    # Includes: /notifications/, /notifications/send-bulk/
    path("", include("notifications.urls")),
    
    # Includes: /attendance/records/, /attendance/analytics/
    path("attendance/", include("attendance.urls")),
    
    # Includes: /finance/receipts/, /finance/expenses/, /finance/analytics/, etc.
    path("finance/", include("finance.urls")),
    
    # 4. API Documentation
    # Includes: /schema/, /docs/swagger/, /docs/redoc/
    path("", include("api.schema")),
]