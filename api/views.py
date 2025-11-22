from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import connection
from django.conf import settings
from django.core.management import call_command
from django.http import HttpResponse
from datetime import datetime
from io import StringIO, BytesIO
import time
import logging
import gzip
import json

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint to verify the backend is running.
    """
    start_time = time.time()
    db_status = "unknown"
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health Check DB Error: {e}")
        db_status = f"error: {str(e)}"

    duration = time.time() - start_time

    return Response({
        "status": "ok",
        "database": db_status,
        "latency_ms": round(duration * 1000, 2),
        "version": settings.SPECTACULAR_SETTINGS.get("VERSION", "1.0.0"),
        "mode": "development" if settings.DEBUG else "production"
    })


class DatabaseBackupView(APIView):
    """
    Admin-only endpoint to download a compressed database dump (JSON.GZ).
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # 1. Capture database dump in memory
        out = StringIO()
        try:
            # Exclude sensitive or auto-generated tables
            call_command(
                'dumpdata', 
                exclude=['contenttypes', 'sessions', 'auth.permission', 'admin.logentry'], 
                indent=2, 
                stdout=out
            )
        except Exception as e:
            logger.error(f"Backup generation failed: {e}", exc_info=True)
            return Response(
                {"success": False, "message": "Failed to generate backup.", "error": str(e)},
                status=500
            )

        # 2. Compress the data using Gzip
        json_data = out.getvalue()
        out.close()
        
        gzip_buffer = BytesIO()
        with gzip.GzipFile(mode='wb', fileobj=gzip_buffer) as gz_file:
            gz_file.write(json_data.encode('utf-8'))
        
        gzip_data = gzip_buffer.getvalue()
        gzip_buffer.close()

        # 3. Return as a downloadable file
        response = HttpResponse(gzip_data, content_type='application/gzip')
        response['Content-Disposition'] = f'attachment; filename="noor_db_backup_{timestamp}.json.gz"'
        response['Content-Length'] = len(gzip_data)
        
        return response