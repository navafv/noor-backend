from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsAdmin
from .models import AttendanceEntry
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

class AttendanceAnalyticsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        start_date = timezone.now().date() - timedelta(days=days)

        # 1. Overall Stats (in range)
        entries = AttendanceEntry.objects.filter(attendance__date__gte=start_date)
        total_entries = entries.count()
        
        if total_entries == 0:
            stats = {"present": 0, "absent": 0, "late": 0, "excused": 0, "rate": 0}
        else:
            present = entries.filter(status="P").count()
            absent = entries.filter(status="A").count()
            late = entries.filter(status="L").count()
            excused = entries.filter(status="E").count()
            
            # 'Present' includes Late for calculation purposes often, but let's keep it strict P
            # Calculate "Effective Presence"
            effective_present = present + late
            rate = round((effective_present / total_entries) * 100, 1)

            stats = {
                "present": present,
                "absent": absent,
                "late": late,
                "excused": excused,
                "rate": rate
            }

        # 2. Daily Trends (Last 7 days)
        week_start = timezone.now().date() - timedelta(days=7)
        daily_data = (
            AttendanceEntry.objects
            .filter(attendance__date__gte=week_start)
            .values("attendance__date")
            .annotate(
                present=Count("id", filter=Q(status="P")),
                absent=Count("id", filter=Q(status="A")),
            )
            .order_by("attendance__date")
        )
        
        chart_data = [
            {
                "date": entry["attendance__date"].strftime("%Y-%m-%d"),
                "present": entry["present"],
                "absent": entry["absent"]
            }
            for entry in daily_data
        ]

        return Response({
            "stats": stats,
            "chart_data": chart_data
        })