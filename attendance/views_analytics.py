from django.db.models import Count, Q
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AttendanceEntry
from students.models import Student


class AttendanceAnalyticsViewSet(viewsets.ViewSet):
    """
    Provides read-only analytical endpoints for attendance.
    Permissions are checked manually within each action.
    """
    permission_classes = [IsAuthenticated] # Base permission

    @action(detail=False, methods=["get"], url_path="student/(?P<student_id>[^/.]+)")
    def student_summary(self, request, student_id=None):
        """
        (Admin or Owning Student)
        Returns a student-level attendance summary, aggregated by batch.
        """
        # Permission Check: Allow admin or the student themselves
        try:
            student_profile_id = request.user.student.id
        except Student.DoesNotExist:
            student_profile_id = None

        is_owner = (str(student_profile_id) == str(student_id))
        is_admin = request.user.is_staff
        
        if not (is_owner or is_admin):
            return Response(
                {"detail": "You do not have permission to view this attendance data."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = Student.objects.filter(id=student_id).select_related("user").first()
        if not student:
            return Response({"detail": "Student not found."}, status=404)

        # Aggregate attendance status for this student, grouped by batch
        entries = (
            AttendanceEntry.objects
            .filter(student=student)
            .values("attendance__batch__id", "attendance__batch__code", "attendance__batch__course__title")
            .annotate(
                presents=Count("id", filter=Q(status="P")),
                absents=Count("id", filter=Q(status="A")),
                leaves=Count("id", filter=Q(status="L")),
                total_days=Count("id")
            )
            .order_by("-total_days")
        )

        # Calculate percentages for each batch
        for e in entries:
            e["attendance_percentage"] = round((e["presents"] / e["total_days"] * 100) if e["total_days"] else 0, 2)

        data = {
            "student_name": student.user.get_full_name(),
            "reg_no": student.reg_no,
            "batches": list(entries),
        }
        return Response(data)