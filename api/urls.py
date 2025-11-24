from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import health_check, DatabaseBackupView

urlpatterns = [
    # 1. Authentication (JWT)
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # 2. System & Utilities
    path("health/", health_check, name="health-check"),
    path("system/backup/", DatabaseBackupView.as_view(), name="system-backup"),

    # 3. App-level URLs
    path("", include("accounts.urls")),
    path("", include("students.urls")),
    path("", include("courses.urls")),
    path("", include("certificates.urls")),
    path("", include("notifications.urls")),
    path("attendance/", include("attendance.urls")),
    path("finance/", include("finance.urls")),
]