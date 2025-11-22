from rest_framework import viewsets, status
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
    queryset = Student.objects.select_related("user")
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
        if self.action == 'me' and self.request.method == 'PATCH':
            return StudentSelfUpdateSerializer
        return StudentSerializer

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsStudent]
        return super().get_permissions()
    
    @action(
        detail=False, 
        methods=["get", "patch"], 
        permission_classes=[IsStudent], 
        parser_classes=[MultiPartParser, FormParser]
    )
    def me(self, request):
        """
        Endpoint for a logged-in student to view or update (photo only) their profile.
        """
        try:
            student = request.user.student
        except Student.DoesNotExist:
            return Response(
                {"detail": "Student profile not found for this user."}, 
                status=status.HTTP_404_NOT_FOUND
            )
 
        if request.method == 'GET':
            serializer = self.get_serializer(student)
            return Response(serializer.data)
 
        if request.method == 'PATCH':
            serializer = self.get_serializer(student, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentMeasurementViewSet(viewsets.ModelViewSet):
    queryset = StudentMeasurement.objects.all()
    serializer_class = StudentMeasurementSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        return self.queryset.filter(student_id=self.kwargs.get("student_pk"))

    def perform_create(self, serializer):
        student_pk = self.kwargs.get("student_pk")
        serializer.save(student_id=student_pk)