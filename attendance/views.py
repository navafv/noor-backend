from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Attendance, AttendanceEntry
from .serializers import AttendanceSerializer, StudentAttendanceEntrySerializer
from api.permissions import IsAdmin, IsStudent

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.prefetch_related("entries__student__user").all()
    serializer_class = AttendanceSerializer
    filterset_fields = ["date"]
    ordering_fields = ["date"]
    search_fields = ["remarks"]

    def get_permissions(self):
        if self.action in ['my_attendance']:
             return [IsStudent()]
        return [IsAdmin()]

    @action(detail=False, methods=["get"], url_path="records")
    def records_by_date(self, request):
        """
        Convenience endpoint to get a specific date's record quickly.
        """
        date_param = request.query_params.get("date")
        if not date_param:
            return Response({"detail": "Date parameter is required."}, status=400)
            
        queryset = self.get_queryset().filter(date=date_param)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "results": serializer.data
        })

    @action(detail=False, methods=["get"], url_path="me")
    def my_attendance(self, request):
        """
        Endpoint for students to view their own attendance history.
        """
        try:
            student = request.user.student
        except AttributeError:
            return Response({"detail": "Student profile not found."}, status=400)

        # We query AttendanceEntry directly for the student
        entries = AttendanceEntry.objects.filter(student=student).select_related("attendance").order_by("-attendance__date")
        
        page = self.paginate_queryset(entries)
        if page is not None:
            serializer = StudentAttendanceEntrySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = StudentAttendanceEntrySerializer(entries, many=True)
        return Response(serializer.data)