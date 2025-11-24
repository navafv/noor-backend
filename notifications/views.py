from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from api.permissions import IsAdmin
from accounts.models import User
import logging

logger = logging.getLogger(__name__)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by("-created_at")

    @action(detail=False, methods=["post"], permission_classes=[IsAdmin])
    def broadcast_active(self, request):
        """
        Send a notification to all students currently enrolled in an active course.
        """
        title = request.data.get("title")
        message = request.data.get("message")

        if not title or not message:
            return Response({"detail": "Title and message are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Find all users who are students AND have at least one active enrollment
        # We use the related names: 'student' (profile) -> 'enrollments' -> status='active'
        active_users = User.objects.filter(
            student__enrollments__status='active'
        ).distinct()

        count = 0
        notifications = []
        for user in active_users:
            notifications.append(Notification(
                recipient=user,
                title=title,
                message=message
            ))
            count += 1
        
        # Bulk create for performance
        Notification.objects.bulk_create(notifications)

        return Response({
            "success": True, 
            "message": f"Notification sent to {count} active students."
        })

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        try:
            notification = self.get_object()
            if not notification.read:
                notification.read = True
                notification.save(update_fields=['read'])
            return Response({"success": True, "status": "marked as read"})
        except Exception as e:
            logger.error(f"Error marking notification {pk} as read: {e}", exc_info=True)
            return Response(
                {"success": False, "message": "Could not update notification."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        try:
            self.get_queryset().filter(read=False).update(read=True)
            return Response({"success": True, "status": "all marked as read"})
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}", exc_info=True)
            return Response(
                {"success": False, "message": "Could not update notifications."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )