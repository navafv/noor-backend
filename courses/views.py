from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from api.permissions import IsAdminOrReadOnly, IsAdmin, IsStudent
from students.models import Student

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly] 
    filterset_fields = ["active", "duration_weeks", "required_attendance_days"]
    search_fields = ["code", "title"]
    ordering_fields = ["title", "duration_weeks", "total_fees"]


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related("student__user", "course")
    serializer_class = EnrollmentSerializer
    filterset_fields = ["status", "course", "student"]
    search_fields = ["student__user__first_name", "student__user__last_name", "course__title"]
    ordering_fields = ["enrolled_on", "status"]

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [IsAdmin | IsStudent]
        else:
            self.permission_classes = [IsAdmin]
        return super().get_permissions()
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Enrollment.objects.none()
        
        if user.is_staff:
            return super().get_queryset()
        else:
            try:
                student_id = user.student.id
                return super().get_queryset().filter(student_id=student_id)
            except Student.DoesNotExist:
                return Enrollment.objects.none()