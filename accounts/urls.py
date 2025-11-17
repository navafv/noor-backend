from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ForgotPasswordView, ResetPasswordView
from django.urls import path

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = router.urls + [
    path("auth/password-reset/", ForgotPasswordView.as_view(), name="password-reset-request"),
    path("auth/password-reset-confirm/", ResetPasswordView.as_view(), name="password-reset-confirm"),
]