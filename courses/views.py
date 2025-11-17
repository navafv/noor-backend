from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Course, Enrollment, CourseMaterial
from .serializers import (
    CourseSerializer, EnrollmentSerializer, CourseMaterialSerializer
)
from api.permissions import IsAdminOrReadOnly, IsAdmin, IsStudent
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from students.models import Student
import logging

logger = logging.getLogger(__name__)

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


class CourseMaterialViewSet(viewsets.ModelViewSet):
    queryset = CourseMaterial.objects.all()
    serializer_class = CourseMaterialSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'download']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdmin]
        return super().get_permissions()

    def get_queryset(self):
        return self.queryset.filter(
            course_id=self.kwargs.get("course_pk")
        ).select_related("course")

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def download(self, request, course_pk=None, pk=None):
        material = get_object_or_404(CourseMaterial, course_id=course_pk, pk=pk)
        
        if not material.file:
            return Response({"detail": "This material is a link, not a file."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = request.user.is_staff
        is_enrolled = False
        if not is_admin:
            try:
                student = request.user.student
                is_enrolled = Enrollment.objects.filter(
                    student=student, 
                    course_id=course_pk,
                    status="active"
                ).exists()
            except Student.DoesNotExist:
                is_enrolled = False
        
        if not (is_admin or is_enrolled):
            return Response({"detail": "Not authorized to download this file."}, status=status.HTTP_403_FORBIDDEN)

        try:
            return FileResponse(
                material.file.open('rb'), 
                as_attachment=True, 
                filename=material.file.name.split('/')[-1]
            )
        except FileNotFoundError:
            logger.warning(f"CourseMaterial file not found in storage: {material.file.name}")
            return Response({"detail": "File not found on server."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error accessing material file {material.file.name}: {e}")
            return Response({"detail": f"Error accessing file: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentMaterialsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseMaterialSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        try:
            student = self.request.user.student
            enrolled_course_ids = Enrollment.objects.filter(
                student=student,
                status="active"
            ).values_list("course_id", flat=True).distinct()
            
            return CourseMaterial.objects.filter(
                course_id__in=enrolled_course_ids
            ).select_related("course").order_by("course__title", "-uploaded_at")
            
        except Student.DoesNotExist:
            return CourseMaterial.objects.none()