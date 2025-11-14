from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Event
from .serializers import EventSerializer
from api.permissions import IsAdminOrReadOnly
from django.utils import timezone
from django.db import models

class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint for institute events.
    - Admins can create, update, delete.
    - All users (including public/students) can read.
    """
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly] # Use the existing permission
    
    def get_queryset(self):
        """
        By default, only show events that haven't ended yet.
        Allow admins to see all events.
        """
        today = timezone.now().date()
        
        if self.request.user.is_staff:
            return Event.objects.all().order_by('-start_date')

        # For students/public, only show upcoming/ongoing events
        return Event.objects.filter(
            models.Q(end_date__gte=today) | models.Q(end_date__isnull=True, start_date__gte=today)
        ).order_by('start_date')