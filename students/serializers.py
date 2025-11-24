from django.db import transaction
from rest_framework import serializers
from .models import Student
from accounts.serializers import UserSerializer, StudentUserCreateSerializer
from django.utils import timezone

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_payload = StudentUserCreateSerializer(write_only=True, required=False)

    class Meta:
        model = Student
        fields = [
            "id", "user", "user_payload", "reg_no", "guardian_name",
            "guardian_phone", "admission_date", "address", "photo", "active",
        ]
        read_only_fields = ["id", "reg_no"]

    def validate_admission_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Admission date cannot be in the future.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user_payload = validated_data.pop("user_payload", None)
        if not user_payload:
            raise serializers.ValidationError({
                "user_payload": "This field is required to create a new student."
            })
        
        user = StudentUserCreateSerializer().create(user_payload)

        student = Student.objects.create(user=user, **validated_data)

        year = student.admission_date.year
        student.reg_no = f"STU{year}-{student.id:04d}"
        student.save(update_fields=["reg_no"])
        
        return student

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data.pop("user_payload", None)
        return super().update(instance, validated_data)


class StudentSelfUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["photo"]