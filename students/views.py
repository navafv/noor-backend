from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Student, StudentMeasurement
from .serializers import (
    StudentSerializer, StudentMeasurementSerializer, 
    StudentSelfUpdateSerializer
)
from api.permissions import IsStaffOrReadOnly, IsStudent

class StudentViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD for student records.
    - Staff/Admins have full read/write access.
    - Authenticated students can use the '/me' endpoint.
    """
    queryset = Student.objects.select_related("user", "user__role")
    permission_classes = [IsStaffOrReadOnly]
    filterset_fields = ["active", "admission_date"]
    search_fields = [
        "reg_no",
        "user__first_name",
        "user__last_name",
        "guardian_name",
        "guardian_phone",
    ]
    ordering_fields = ["admission_date", "reg_no", "id"]

    def get_serializer_class(self):
        """
        Use a limited serializer for the 'me' endpoint PATCH,
        otherwise use the default StudentSerializer.
        """
        if self.action == 'me' and self.request.method == 'PATCH':
            return StudentSelfUpdateSerializer
        return StudentSerializer

    def get_permissions(self):
        """Assign IsStudent permission for the 'me' action."""
        if self.action == 'me':
            self.permission_classes = [IsStudent]
        return super().get_permissions()
    
    @action(
        detail=False, 
        methods=["get", "patch"], 
        permission_classes=[IsStudent], 
        parser_classes=[MultiPartParser, FormParser] # For photo uploads
    )
    def me(self, request):
        """
        GET: Retrieve the student profile for the logged-in user.
        PATCH: Update the student profile (e.g., photo) for the logged-in user.
        """
        try:
            student = request.user.student
        except Student.DoesNotExist:
            return Response({"detail": "Student profile not found for this user."}, status=404)
 
        if request.method == 'GET':
            serializer = self.get_serializer(student)
            return Response(serializer.data)
 
        if request.method == 'PATCH':
            serializer = self.get_serializer(student, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)


class StudentMeasurementViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing a student's measurements.
    Accessed via the nested route:
    /api/v1/students/<student_pk>/measurements/
    """
    queryset = StudentMeasurement.objects.all()
    serializer_class = StudentMeasurementSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        """Filter measurements by the student_pk in the URL."""
        return self.queryset.filter(student_id=self.kwargs.get("student_pk"))

    def perform_create(self, serializer):
        """Automatically associate measurements with the student from the URL."""
        student_pk = self.kwargs.get("student_pk")
        serializer.save(student_id=student_pk)