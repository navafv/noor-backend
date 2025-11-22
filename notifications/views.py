from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
import logging

logger = logging.getLogger(__name__)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by("-created_at")

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
            # Efficient bulk update
            self.get_queryset().filter(read=False).update(read=True)
            return Response({"success": True, "status": "all marked as read"})
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}", exc_info=True)
            return Response(
                {"success": False, "message": "Could not update notifications."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )