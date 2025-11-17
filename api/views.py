from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from django.conf import settings
import time

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint to verify the backend is running
    and can connect to the database.
    """
    start_time = time.time()
    db_status = "unknown"
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    duration = time.time() - start_time

    return Response({
        "status": "ok",
        "database": db_status,
        "latency_ms": round(duration * 1000, 2),
        "version": "1.0.0",
        "mode": "development" if settings.DEBUG else "production"
    })