from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Event
from .serializers import EventSerializer
from api.permissions import IsAdminOrReadOnly 
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint for institute events.
    - Admins can create, update, and delete events.
    - All users (including public/students) can read events.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly] 
    
    def get_queryset(self):
        """
        Filters the visible events based on user role.
        - Admins see all events (past and future).
        - Students/Public see only *ongoing or future* events.
        """
        try:
            if self.request.user.is_authenticated and self.request.user.is_staff:
                return Event.objects.all().order_by('-start_date')

            today = timezone.now().date()
            return Event.objects.filter(end_date__gte=today).order_by('start_date')
        except Exception as e:
            logger.error(f"Error fetching events: {e}", exc_info=True)
            return Event.objects.none()