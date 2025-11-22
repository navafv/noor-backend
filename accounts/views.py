from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import User
from .serializers import (
    UserSerializer, UserCreateSerializer, 
    PasswordChangeSerializer,
    PasswordResetRequestSerializer, SetNewPasswordSerializer
)
from api.permissions import IsAdmin
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
import logging
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by('username')
    filterset_fields = ["is_active", "is_staff"]
    search_fields = ["username", "email", "first_name", "last_name", "phone"]
    ordering_fields = ["id", "username", "first_name", "last_name"]
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ["me", "set_password"]:
            return [IsAuthenticated()]
        return [IsAdmin()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "set_password":
            return PasswordChangeSerializer
        return UserSerializer 

    @action(detail=False, methods=["get", "patch", "put"], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(user, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="me/set-password")
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Password updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    @staticmethod
    def send_sendgrid_email(to_email, subject, html_content):
        """
        Helper to send email via SendGrid. Returns status code or None.
        """
        if not settings.SENDGRID_API_KEY:
            logger.warning("SendGrid API Key is missing. Email not sent.")
            return None

        try:
            message = Mail(
                from_email=settings.EMAIL_SENDER,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            return response.status_code

        except Exception as e:
            logger.error(f"SendGrid Error: {e}", exc_info=True)
            return None

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Note: Serializer validation ensures user exists and is active
        user = User.objects.get(email__iexact=serializer.validated_data["email"])

        token = PasswordResetTokenGenerator().make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip('/')
        reset_link = f"{frontend_url}/reset-password/{uidb64}/{token}"

        context = {
            "first_name": user.first_name or user.username,
            "reset_link": reset_link,
        }

        html_message = render_to_string("account/password_reset_email.html", context)

        result = ForgotPasswordView.send_sendgrid_email(
            user.email,
            "Password Reset for Noor Institute",
            html_message,
        )

        # In development, just logging the link is often helpful
        if settings.DEBUG:
            logger.info(f"Password Reset Link for {user.email}: {reset_link}")

        if result and result not in [200, 202]:
            return Response(
                {"success": False, "message": "Failed to send email provider error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"success": True, "message": "Password reset link sent to your email."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SetNewPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {"success": True, "message": "Password has been reset successfully. You can now log in."},
            status=status.HTTP_200_OK
        )