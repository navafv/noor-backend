from rest_framework import serializers
from .models import FeesReceipt, Expense
from courses.models import Enrollment

class FeesReceiptSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source="student.user.get_full_name")
    # FIXED: Use SerializerMethodField to handle deleted (null) courses safely
    course_title = serializers.SerializerMethodField()

    class Meta:
        model = FeesReceipt
        fields = [
            "id", "public_id", "receipt_no", "student", "student_name", "course", "course_title",
            "amount", "mode", "txn_id", "date", "posted_by", "remarks", 
            "locked", "pdf_file", "created_at"
        ]
        read_only_fields = ["receipt_no", "public_id", "posted_by", "locked", "student_name", "pdf_file", "created_at"]

    def get_course_title(self, obj):
        """Return course title or a placeholder if the course was deleted."""
        if not obj.course:
            return "Deleted Course"
        return obj.course.title

    def validate(self, attrs):
        if self.instance and self.instance.locked:
            raise serializers.ValidationError("This receipt is locked and cannot be modified.")

        course = attrs.get("course") or (self.instance.course if self.instance else None)
        student = attrs.get("student") or (self.instance.student if self.instance else None)

        if course and student:
            if not Enrollment.objects.filter(student=student, course=course).exists():
                raise serializers.ValidationError("Student is not enrolled in this course.")

        return attrs
    
    def create(self, validated_data):
        validated_data['posted_by'] = self.context['request'].user
        return super().create(validated_data)


class ExpenseSerializer(serializers.ModelSerializer):
    recorded_by_name = serializers.ReadOnlyField(source="recorded_by.get_full_name")

    class Meta:
        model = Expense
        fields = [
            "id", "category", "title", "amount", "date", 
            "description", "receipt_image", "recorded_by", "recorded_by_name"
        ]
        read_only_fields = ["id", "recorded_by"]

    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)