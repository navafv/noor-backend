from django.db import transaction
from rest_framework import serializers
from .models import Student, StudentMeasurement
from accounts.serializers import UserSerializer, StudentUserCreateSerializer
from django.utils import timezone

class StudentSerializer(serializers.ModelSerializer):
    """
    Serializer for student data.
    Handles nested User creation via the 'user_payload' field.
    """
    # Read-only nested User details
    user = UserSerializer(read_only=True)
    # Write-only field to accept data for creating a new User
    user_payload = StudentUserCreateSerializer(write_only=True, required=False)

    class Meta:
        model = Student
        fields = [
            "id", "user", "user_payload", "reg_no", "guardian_name",
            "guardian_phone", "admission_date", "address", "photo", "active",
        ]
        read_only_fields = ["id", "reg_no"]

    def validate_admission_date(self, value):
        """Ensure admission date is not in the future."""
        if value > timezone.localdate():
            raise serializers.ValidationError("Admission date cannot be in the future.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Creates a User and a Student profile together in a single transaction.
        The 'user_payload' is required for creation.
        """
        user_payload = validated_data.pop("user_payload", None)
        if not user_payload:
            raise serializers.ValidationError({
                "user_payload": "This field is required to create a new student."
            })
        
        # Create the User account
        user = StudentUserCreateSerializer().create(user_payload)

        # Create the student *without* a reg_no
        student = Student.objects.create(user=user, **validated_data)

        # Now that the student has an ID, generate the reg_no
        year = student.admission_date.year
        student.reg_no = f"STU{year}-{student.id:04d}"
        student.save(update_fields=["reg_no"])
        
        return student

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Updates the Student instance.
        'user_payload' is ignored on updates; user data must be
        updated via the /accounts/users/{id}/ endpoint.
        """
        validated_data.pop("user_payload", None)
        return super().update(instance, validated_data)


class StudentMeasurementSerializer(serializers.ModelSerializer):
    """Serializer for student measurements."""
    student_name = serializers.ReadOnlyField(source="student.user.get_full_name")

    class Meta:
        model = StudentMeasurement
        fields = "__all__"
        read_only_fields = ["id", "student"]


class StudentSelfUpdateSerializer(serializers.ModelSerializer):
    """
    A limited serializer for students to update their own profile
    via the '/students/me/' endpoint.
    Intended primarily for changing the profile photo.
    """
    class Meta:
        model = Student
        fields = ["photo"]