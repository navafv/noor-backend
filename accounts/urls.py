from rest_framework.routers import DefaultRouter
from .views import (
    RoleViewSet, UserViewSet, HistoricalUserViewSet,
    ForgotPasswordView, ResetPasswordView
)
from django.urls import path

router = DefaultRouter()
router.register("roles", RoleViewSet, basename="role")
router.register("users", UserViewSet, basename="user")
router.register("history/users", HistoricalUserViewSet, basename="user-history")

# Add paths for password reset
urlpatterns = router.urls + [
    path("auth/password-reset/", ForgotPasswordView.as_view(), name="password-reset-request"),
    path("auth/password-reset-confirm/", ResetPasswordView.as_view(), name="password-reset-confirm"),
]