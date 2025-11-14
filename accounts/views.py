"""
Accounts Views
--------------
Enhancements:
- Added selective permissions for safety.
- Optimized queryset (select_related for role).
- Added endpoint for self-profile retrieval.
- NEW: Added Forgot Password & Reset Password views.
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Role, User
from .serializers import (
    RoleSerializer, UserSerializer, UserCreateSerializer, 
    PasswordChangeSerializer, HistoricalUserSerializer,
    PasswordResetRequestSerializer, SetNewPasswordSerializer
)
from api.permissions import IsAdmin
from rest_framework_simplejwt.authentication import JWTAuthentication

# --- NEW IMPORTS ---
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
# --- END NEW IMPORTS ---


class RoleViewSet(viewsets.ModelViewSet):
    """Admin-only Role management."""
    queryset = Role.objects.all().order_by("name")
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]
    authentication_classes = [JWTAuthentication]
    filterset_fields = ["name"]
    search_fields = ["name"]
    ordering_fields = ["name", "id"]


class UserViewSet(viewsets.ModelViewSet):
    """
    User management.
    Admins can manage all users.
    Authenticated users can view or update their own profile via /me endpoint.
    """
    queryset = User.objects.select_related("role")
    filterset_fields = ["is_active", "role"]
    search_fields = ["username", "email", "first_name", "last_name", "phone"]
    ordering_fields = ["id", "username", "first_name", "last_name"]
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ["me", "partial_update", "set_password"]:
            return [IsAuthenticated()]
        return [IsAdmin()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "set_password":
            return PasswordChangeSerializer
        return UserSerializer

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get the authenticated user's own profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["post"], url_path="me/set-password")
    def set_password(self, request):
        """
        Allows the authenticated user to change their own password.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class HistoricalUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only view for User history.
    """
    queryset = User.history.select_related("history_user").all()
    serializer_class = HistoricalUserSerializer
    permission_classes = [IsAdmin]
    authentication_classes = [JWTAuthentication]
    filterset_fields = ["history_type", "history_user", "username"]
    search_fields = ["username", "first_name", "history_change_reason"]


# --- NEW VIEWS FOR FORGOT PASSWORD ---

class ForgotPasswordView(generics.GenericAPIView):
    """
    Request a password reset email.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.get(email__iexact=serializer.validated_data['email'])
        
        # Generate token and UID
        token = PasswordResetTokenGenerator().make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Get frontend URL from settings (first one)
        frontend_url = settings.CORS_ALLOWED_ORIGINS[0]
        reset_link = f"{frontend_url}/reset-password/{uidb64}/{token}/"
        
        context = {
            'first_name': user.first_name or user.username,
            'reset_link': reset_link,
        }
        
        # Render email
        email_message = render_to_string('account/password_reset_email.html', context)
        
        try:
            # Send email
            send_mail(
                subject="Password Reset for Noor Institute",
                message=f"Click here to reset your password: {reset_link}", # Plain text fallback
                html_message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
        except Exception as e:
            return Response(
                {"detail": "Error sending email. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"detail": "Password reset link has been sent to your email."},
            status=status.HTTP_200_OK
        )


class ResetPasswordView(generics.GenericAPIView):
    """
    Confirm and set a new password using the token.
    """
    permission_classes = [AllowAny]
    serializer_class = SetNewPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {"detail": "Password has been reset successfully. You can now log in."},
            status=status.HTTP_200_OK
        )